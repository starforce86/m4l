from django.template import Library, TemplateSyntaxError

from tendenci.apps.chapters.models import Chapter
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.chapters.utils import get_chapter_membership_field_values

register = Library()


class ListChaptersNode(ListNode):
    model = Chapter
    perms = 'chapters.view_chapter'

@register.inclusion_tag("chapters/nav.html", takes_context=True)
def chapter_nav(context, user, chapter=None):
    context.update({
        'nav_object': chapter,
        "user": user
    })
    return context


@register.inclusion_tag("chapters/top_nav_items.html", takes_context=True)
def chapter_current_app(context, user, chapter=None):
    context.update({
        "app_object": chapter,
        "user": user
    })
    return context


@register.tag
def list_chapters(parser, token):
    """
    Example::

        {% list_chapters as chapters_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
        {% for chapter in chapters %}
            {{ chapter.something }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListChaptersNode(context_var, *args, **kwargs)

@register.inclusion_tag("chapters/search-form.html", takes_context=True)
def chapter_search(context):
    return context

@register.inclusion_tag("chapters/options.html", takes_context=True)
def chapter_options(context, user, chapter):
    context.update({
        "opt_object": chapter,
        "user": user
    })
    return context

@register.inclusion_tag("chapters/form.html", takes_context=True)
def chapter_form(context, form, formset=None):
    context.update({
        'form': form,
        'formset': formset
    })
    return context

@register.inclusion_tag("chapters/edit_form.html", takes_context=True)
def chapter_edit_form(context, form, officer_formset=None, field_formset=None):
    context.update({
        'form': form,
        'officer_formset': officer_formset,
        'field_formset': field_formset
    })
    return context

@register.inclusion_tag("chapters/officer-formset.html", takes_context=True)
def chapter_officer_formset(context, officer_formset):
    context.update({
        'formset': officer_formset
    })
    return context

@register.inclusion_tag("chapters/field-formset.html", takes_context=True)
def chapter_field_formset(context, formset):
    context.update({
        'formset': formset
    })
    return context


@register.inclusion_tag("memberships/applications/render_membership_field.html")
def render_chapter_membership_field(request, field_obj,
                            chapter_membership_form):
    field_pwd = None
    if field_obj.field_type == "section_break":
        field = None
    else:
        field_name = field_obj.field_name
        if field_name in chapter_membership_form.fields:
            field = chapter_membership_form[field_name]
        else:
            field = None

    return {'request': request, 'field_obj': field_obj,
            'field': field, 'field_pwd': field_pwd}


@register.inclusion_tag('chapters/memberships/search-member-line.html')
def render_chapter_member_row(chapter_membership, app_fields):
    field_values_list = get_chapter_membership_field_values(chapter_membership, app_fields)

    return {'chapter_membership': chapter_membership,
            'field_values_list': field_values_list}