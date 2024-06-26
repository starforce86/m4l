from builtins import str

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from tendenci.apps.base.http import Http403
from tendenci.apps.base.utils import template_exists
from tendenci.apps.base.views import file_display
from tendenci.apps.chapters.models import Chapter
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.pages.models import HeaderImage
from tendenci.apps.versions.models import Version
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import (update_perms_and_save,
                                       get_notice_recipients,
                                       has_perm,
                                       has_view_perm,
                                       get_query_filters)
from tendenci.apps.categories.forms import CategoryForm
from tendenci.apps.categories.models import Category
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.exports.utils import run_export_task
from tendenci.apps.notifications import models as notification

from tendenci.apps.chapter_pages.models import ChapterPage
from tendenci.apps.chapter_pages.forms import ChapterPageForm
from tendenci.apps.categories.models import CategoryItem
from tendenci.apps.perms.utils import assign_files_perms


def get_chapter(slug):
    return get_object_or_404(Chapter, slug=slug)


@is_enabled('chapter_pages')
def index(request, chapter_slug=None, slug=None, id=None, hash=None,
          template_name="chapter_pages/view.html"):
    """
    Return page object, either as an archive, active, or version.
    """

    chapter = get_chapter(chapter_slug)
    if not slug and not id and not hash:
        return HttpResponseRedirect(reverse('chapter_page.search', args=[chapter_slug]))

    if hash:
        version = get_object_or_404(Version, hash=hash)
        current_page = get_object_or_404(ChapterPage, pk=version.object_id)
        page = version.get_version_object()
        msg_string = 'You are viewing a previous version of this article. View the ' + \
         '<a href="%s">Current Version</a>.' % current_page.get_absolute_url()
        messages.add_message(request, messages.WARNING, _(msg_string))
    elif id:
        page = get_object_or_404(ChapterPage, pk=id)
        if page.status_detail != 'active':
            if not request.user.is_authenticated:
                pages = ChapterPage.objects.filter(
                    slug=page.slug, status_detail='active'
                ).order_by('-pk')
                if not pages:
                    pages = ChapterPage.objects.filter(slug=slug).order_by('-pk')
                if not pages:
                    raise Http404
                return HttpResponseRedirect(reverse('page', args=[page.slug]))

    else:
        try:
            page = get_object_or_404(ChapterPage, slug=slug, chapter=chapter)
        except ChapterPage.MultipleObjectsReturned:
            pages = ChapterPage.objects.filter(
                slug=slug,
                chapter=chapter,
                status_detail='active'
            ).order_by('-pk')
            if not pages:
                pages = ChapterPage.objects.filter(slug=slug, chapter=chapter).order_by('-pk')
            if not pages:
                raise Http404

            page = pages[0]

    if not has_view_perm(request.user, 'chapter_pages.view_chapterpage', page):
        raise Http403

    if not page.template or not template_exists(page.template):
        page.template = 'default.html'
    if page.template in ["default.html", "base.html"]:
        page.template = "chapter_pages/base.html"

    EventLog.objects.log(instance=page)

    return render_to_resp(
        request=request,
        template_name=template_name,
        context={
            'page': page,
            'chapter': chapter
        })


@is_enabled('chapter_pages')
def search(request, chapter_slug=None, template_name="chapter_pages/search.html"):
    """
    Search pages.
    """
    query = request.GET.get('q')

    filters = get_query_filters(request.user, 'pages.view_page')
    chapter = get_chapter(chapter_slug)
    filters &= Q(chapter=chapter)

    pages = ChapterPage.objects.filter(filters).distinct()
    if query:
        if "category:" in query or "sub_category:" in query:
            # handle category and sub_category
            key, name = query.split(':', 1)
            categories = Category.objects.filter(name__iexact=name)
            if categories.exists():
                category = categories[0]
                if key == 'category':
                    page_ids = CategoryItem.objects.filter(content_type_id=ContentType.objects.get_for_model(ChapterPage), category_id=category.id, parent_id__isnull=True).values_list('object_id', flat=True)
                else:
                    page_ids = CategoryItem.objects.filter(content_type_id=ContentType.objects.get_for_model(ChapterPage), parent_id=category.id, category_id__isnull=True).values_list('object_id', flat=True)
                pages = pages.filter(id__in=page_ids)
            else:
                pages = ChapterPage.objects.none()

        else:
            pages = pages.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(slug__icontains=query))
            pages = pages.exclude(status_detail='archive')

    pages = pages.order_by('-create_dt')

    EventLog.objects.log()

    return render_to_resp(
        request=request,
        template_name=template_name,
        context={
            'pages': pages,
            'chapter': chapter,
            'is_in_chapter': chapter.is_in_chapter(request.user)
        })


@is_enabled('chapter_pages')
def print_view(request, chapter_slug, slug, template_name="chapter_pages/print-view.html"):
    chapter = get_chapter(chapter_slug)

    try:
        page = get_object_or_404(ChapterPage, slug=slug, chapter=chapter)
    except ChapterPage.MultipleObjectsReturned:
        pages = ChapterPage.objects.filter(
            slug=slug,
            chapter=chapter,
            status_detail='active'
        ).order_by('-pk')
        if not pages:
            pages = ChapterPage.objects.filter(slug=slug, chapter=chapter).order_by('-pk')
        if not pages:
            raise Http404

        page = pages[0]

    if not has_perm(request.user, 'chapter_pages.view_chapterpage', page):
        raise Http403

    EventLog.objects.log(instance=page)

    return render_to_resp(request=request, template_name=template_name,
        context={'page': page, 'chapter': chapter})


@is_enabled('chapter_pages')
@login_required
def edit(request, chapter_slug, id, form_class=ChapterPageForm,
         meta_form_class=MetaForm,
         category_form_class=CategoryForm, template_name="chapter_pages/edit.html"):
    chapter = get_chapter(chapter_slug)
    page = get_object_or_404(ChapterPage, pk=id, chapter=chapter)

    can_edit = (chapter.is_in_chapter(request.user) and has_perm(request.user, 'chapter_pages.change_chapterpage', page)) or request.user.profile.is_superuser
    if not can_edit:
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='chapter_pages',
                                     model='chapterpage')

    if request.method == "POST":
        form = form_class(request.POST, request.FILES,
                          instance=page,
                          user=request.user)
        metaform = meta_form_class(request.POST,
                                   instance=page.meta,
                                   prefix='meta')
        categoryform = category_form_class(content_type,
                                           request.POST,)
        if form.is_valid() and metaform.is_valid() and categoryform.is_valid():
            page = form.save()

            # handle header image
            f = form.cleaned_data['header_image']
            if f:
                header = HeaderImage()
                header.content_type = ContentType.objects.get_for_model(ChapterPage)
                header.object_id = page.id
                header.creator = request.user
                header.creator_username = request.user.username
                header.owner = request.user
                header.owner_username = request.user.username
                filename = "%s-%s" % (page.slug, f.name)
                f.file.seek(0)
                header.file.save(filename, f)
                page.header_image = header

            #save meta
            meta = metaform.save()
            page.meta = meta

            ## update the category and subcategory
            page.update_category_subcategory(
                            categoryform.cleaned_data['category'],
                            categoryform.cleaned_data['sub_category']
                            )

            # update all permissions
            page = update_perms_and_save(request, form, page)
            #if page.pk == 1:  # the about page has id 1 in the npo defaults fixture
            #    checklist_update('update-about')

            messages.add_message(request, messages.SUCCESS,
                                 _('Successfully updated %(p)s' % {'p': str(page)}))

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module', 'pages',
                                                   'pagerecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': page,
                            'chapter': chapter,
                            'request': request,
                        }
                        notification.send_emails(recipients,
                                                 'page_edited',
                                                 extra_context)

            return HttpResponseRedirect(reverse('chapter_page', args=[chapter_slug, page.slug]))
    else:
        form = form_class(instance=page, user=request.user)
        metaform = meta_form_class(instance=page.meta, prefix='meta')
        #setup categories
        category = Category.objects.get_for_object(page, 'category')
        sub_category = Category.objects.get_for_object(page, 'sub_category')

        initial_category_form_data = {
            'app_label': 'pages',
            'model': 'page',
            'pk': page.pk,
            'category': getattr(category, 'name', '0'),
            'sub_category': getattr(sub_category, 'name', '0')
        }

        categoryform = category_form_class(content_type,
                                           initial=initial_category_form_data,)

    return render_to_resp(request=request, template_name=template_name,
        context={
            'page': page,
            'form': form,
            'chapter': chapter,
            'metaform': metaform,
            'categoryform': categoryform,
        })


@is_enabled('chapter_pages')
@login_required
def edit_meta(request, chapter_slug, id, form_class=MetaForm, template_name="chapter_pages/edit-meta.html"):
    """
    Return page that allows you to edit meta-html information.
    """
    # check permission
    chapter = get_chapter(chapter_slug)
    page = get_object_or_404(ChapterPage, pk=id, chapter=chapter)

    can_edit = (chapter.is_in_chapter(request.user) and has_perm(request.user, 'chapter_pages.change_chapterpage', page)) or request.user.profile.is_superuser
    if not can_edit:
        raise Http403

    defaults = {
        'title': page.get_title(),
        'description': page.get_description(),
        'keywords': page.get_keywords(),
        'canonical_url': page.get_canonical_url(),
    }
    page.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=page.meta)
        if form.is_valid():
            page.meta = form.save()  # save meta
            page.save()  # save relationship

            messages.add_message(request, messages.SUCCESS,
                                 _('Successfully updated meta for %(p)s' % {'p': str(page)}))

            return HttpResponseRedirect(reverse('chapter_page', args=[chapter_slug, page.slug]))
    else:
        form = form_class(instance=page.meta)

    return render_to_resp(request=request, template_name=template_name,
        context={'page': page, 'form': form, 'chapter': chapter})


@login_required
def preview(request, chapter_slug, id=None, form_class=ChapterPageForm, meta_form_class=MetaForm,
        category_form_class=CategoryForm, template="chapter_pages/preview.html"):

    content_type = get_object_or_404(ContentType,
                                     app_label='chapter_pages',
                                     model='chapterpage')

    chapter = get_chapter(chapter_slug)
    page = None
    if id:
        page = get_object_or_404(ChapterPage, pk=id, chapter=chapter)

    if request.method == "POST":
        if page:
            form = form_class(request.POST, request.FILES, instance=page, user=request.user)
        else:
            form = form_class(request.POST, request.FILES, user=request.user)
        metaform = meta_form_class(request.POST, prefix='meta')
        categoryform = category_form_class(content_type,
                                           request.POST,
                                           prefix='category')
        if form.is_valid():
            page = form.save(commit=False)

            edit_button = False
            if request.POST.get('preview_for', '') == 'edit':
                edit_button = True

            f = form.cleaned_data['header_image']
            if f:
                header = HeaderImage()
                header.content_type = ContentType.objects.get_for_model(ChapterPage)
                header.object_id = page.id
                header.creator = request.user
                header.creator_username = request.user.username
                header.owner = request.user
                header.owner_username = request.user.username
                filename = "%s-%s" % (page.slug, f.name)
                f.file.seek(0)
                header.file.save(filename, f, save=False)
                page.header_image = header

            if 'preview_for' not in request.POST:
                page.save()

                if metaform.is_valid():
                    #save meta
                    meta = metaform.save()
                    page.meta = meta

                if categoryform.is_valid():
                    ## update the category and subcategory
                    page.update_category_subcategory(
                                    categoryform.cleaned_data['category'],
                                    categoryform.cleaned_data['sub_category']
                                    )

                # update all permissions
                page = update_perms_and_save(request, form, page)

                messages.add_message(request, messages.SUCCESS,
                                 _('Successfully updated %(p)s' % {'p': str(page)}))
                if not request.user.profile.is_superuser:
                    # send notification to administrators
                    recipients = get_notice_recipients('module', 'pages',
                                                       'pagerecipients')
                    if recipients:
                        if notification:
                            extra_context = {
                                'object': page,
                                'chapter': chapter,
                                'request': request,
                            }
                            notification.send_emails(recipients,
                                                     'page_edited',
                                                     extra_context)

                return HttpResponseRedirect(reverse('chapter_page', args=[chapter_slug, page.slug]))

            return render_to_resp(
                request=request,
                template_name=template,
                context={
                    'page': page,
                    'chapter': chapter,
                    'form': form,
                    'metaform': metaform,
                    'categoryform': categoryform,
                    'edit_button': edit_button
                })

    return HttpResponseRedirect(reverse('chapter_page.search', args=[chapter_slug]))


@is_enabled('chapter_pages')
@login_required
def add(request, chapter_slug, form_class=ChapterPageForm, meta_form_class=MetaForm,
        category_form_class=CategoryForm,
        template_name="chapter_pages/add.html"):

    chapter = get_chapter(chapter_slug)
    can_add = (chapter.is_in_chapter(request.user) and has_perm(request.user, 'chapter_pages.add_chapterpage')) or request.user.profile.is_superuser
    if not can_add:
        raise Http403

    content_type = get_object_or_404(ContentType,
                                     app_label='chapter_pages',
                                     model='chapterpage')

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=request.user)
        metaform = meta_form_class(request.POST, prefix='meta')
        categoryform = category_form_class(content_type,
                                           request.POST,)
        if form.is_valid() and metaform.is_valid() and categoryform.is_valid():
            page = form.save(commit=False)
            # add all permissions and save the model
            page = update_perms_and_save(request, form, page)

            # handle header image
            f = form.cleaned_data['header_image']
            if f:
                header = HeaderImage()
                header.content_type = ContentType.objects.get_for_model(ChapterPage)
                header.object_id = page.id
                header.creator = request.user
                header.creator_username = request.user.username
                header.owner = request.user
                header.owner_username = request.user.username
                filename = "%s-%s" % (page.slug, f.name)
                f.file.seek(0)
                header.file.save(filename, f)
                page.header_image = header
                page.save()
                assign_files_perms(page, files=[page.header_image])

            #save meta
            meta = metaform.save()
            page.meta = meta

            ## update the category and subcategory
            page.update_category_subcategory(
                                    categoryform.cleaned_data['category'],
                                    categoryform.cleaned_data['sub_category']
                                    )

            messages.add_message(request, messages.SUCCESS,
                                 _('Successfully added %(p)s' % {'p': str(page)}))

            # checklist_update('add-page')

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module',
                                                   'pages',
                                                    'pagerecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': page,
                            'chapter': chapter,
                            'request': request,
                        }
                        notification.send_emails(recipients, 'page_added', extra_context)
            if page.status and page.status_detail == 'active':
                return HttpResponseRedirect(reverse('chapter_page', args=[chapter_slug, page.slug]))
            return HttpResponseRedirect(reverse('chapter_page.search', args=[chapter_slug]))
    else:
        initial_category_form_data = {
            'app_label': 'chapter_pages',
            'model': 'ChapterPage',
            'pk': 0,
        }
        form = form_class(user=request.user, initial={'chapter': chapter.pk})
        metaform = meta_form_class(prefix='meta')
        categoryform = category_form_class(content_type,
                                           initial=initial_category_form_data,)
    return render_to_resp(request=request, template_name=template_name,
            context={
                'form': form,
                'chapter': chapter,
                'metaform': metaform,
                'categoryform': categoryform,
            })


@is_enabled('chapter_pages')
@login_required
def delete(request, chapter_slug, id, template_name="chapter_pages/delete.html"):
    chapter = get_chapter(chapter_slug)
    page = get_object_or_404(ChapterPage, pk=id, chapter=chapter)

    can_delete = (chapter.is_in_chapter(request.user) and has_perm(request.user, 'chapter_pages.delete_chapterpage')) or request.user.profile.is_superuser
    if not can_delete:
        raise Http403

    if request.method == "POST":
        EventLog.objects.log(instance=page)
        messages.add_message(request, messages.SUCCESS,
                             _('Successfully deleted %(p)s' % { 'p': str(page)}))

        # send notification to administrators
        recipients = get_notice_recipients('module', 'pages', 'pagerecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': page,
                    'chapter': chapter,
                    'request': request,
                }
                notification.send_emails(recipients, 'page_deleted', extra_context)

        # Soft delete
        page.status = False
        page.status_detail = 'inactive'
        page.save()
        return HttpResponseRedirect(reverse('chapter_page.search', args=[chapter_slug]))

    return render_to_resp(request=request, template_name=template_name,
        context={'page': page, 'chapter': chapter})


@is_enabled('pages')
def display_header_image(request, id):
    page = get_object_or_404(ChapterPage, pk=id)

    if not has_view_perm(request.user,
                        'chapter_pages.view_chapterpage',
                        page):
        raise Http403

    if not page.header_image:
        raise Http404

    return file_display(request, page.header_image.file.name)


@is_enabled('chapter_pages')
@login_required
def export(request, chapter_slug, template_name="chapter_pages/export.html"):
    """Export Pages"""
    if not request.user.is_superuser:
        raise Http403

    # TODO: filter export by chapter?
    chapter = get_chapter(chapter_slug)

    if request.method == 'POST':

        fields = [
            'guid',
            'title',
            'slug',
            'header_image',
            'content',
            'view_contact_form',
            'design_notes',
            'syndicate',
            'template',
            'tags',
            'entity',
            'meta',
            'categories',
            'chapter',
        ]

        export_id = run_export_task('chapter_pages', 'ChapterPage', fields)
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })
