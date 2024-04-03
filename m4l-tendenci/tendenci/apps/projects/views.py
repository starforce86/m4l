from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.projects.models import Project, Category
from tendenci.apps.perms.utils import has_perm, get_query_filters
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting


def index(request, template_name="projects/detail.html"):
    return HttpResponseRedirect(reverse('projects.search'))


def detail(request, slug=None, template_name="projects/detail.html"):
    if not slug:
        return HttpResponseRedirect(reverse('projects.search'))
    project = get_object_or_404(Project, slug=slug)
    project_photos = project.projects_photo_related.all()
    if has_perm(request.user, 'project.view_project', project):
        log_defaults = {
            'event_id': 1180500,
            'event_data': '%s (%d) viewed by %s' % (project._meta.object_name, project.pk, request.user),
            'description': '%s viewed' % project._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': project,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_resp(request=request, template_name=template_name,
            context={'project': project, 'project_photos': project_photos})
    else:
        raise Http403

def search(request, template_name="projects/search.html"):
    query = request.GET.get('q', None)

    if get_setting('site', 'global', 'searchindex') and query:
        projects = Project.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'projects.search')
        projects = Project.objects.filter(filters).distinct()

    categories = Category.objects.all()
    category_id = request.GET.get('category', None)

    if category_id:
        try:
            category = Category.objects.get(pk=category_id)
        except:
            category = None

        if category:
            projects = projects.filter(category=category)

    log_defaults = {
        'event_id' : 1180400,
        'event_data': '%s searched by %s' % ('Project', request.user),
        'description': '%s searched' % 'Project',
        'user': request.user,
        'request': request,
        'source': 'projects'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_resp(request=request, template_name=template_name,
        context={'projects':projects, 'categories': categories
        })

def category(request, template_name="projects/category.html"):
    query = request.GET.get('q', None)

    if get_setting('site', 'global', 'searchindex') and query:
        projects = Project.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'projects.search')
        projects = Project.objects.filter(filters).distinct()

    categories = Category.objects.all()
    category_id = request.GET.get('category', None)

    if category_id:
        try:
            category = Category.objects.get(pk=category_id)
        except:
            category = None

        if category:
            projects = projects.filter(category=category)

    log_defaults = {
        'event_id' : 1180400,
        'event_data': '%s searched by %s' % ('Project', request.user),
        'description': '%s searched' % 'Project',
        'user': request.user,
        'request': request,
        'source': 'projects'
    }

    EventLog.objects.log(**log_defaults)

    return render_to_resp(request=request, template_name=template_name,
        context={'projects':projects, 'categories': categories
        })
