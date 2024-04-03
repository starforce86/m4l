from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import has_perm, get_query_filters

from tendenci.apps.testimonials.models import Testimonial


def details(request, pk=None, template_name="testimonials/view.html"):
    if not pk: return HttpResponseRedirect(reverse('testimonials'))
    testimonial = get_object_or_404(Testimonial, pk=pk)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (testimonial.status_detail).lower() != 'active' and (not request.user.profile.is_superuser):
        raise Http403

    if has_perm(request.user, 'testimonials.view_testimonial', testimonial):
        EventLog.objects.log(instance=testimonial)

        return render_to_resp(request=request, template_name=template_name,
            context={'testimonial': testimonial})
    else:
        raise Http403

def search(request, template_name="testimonials/search.html"):
    """
    This page lists out all testimonials from newest to oldest.
    If a search index is available, this page will also
    have the option to search through testimonials.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        testimonials = Testimonial.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'testimonials.view_story')
        testimonials = Testimonial.objects.filter(filters).distinct()
        if request.user.is_authenticated:
            testimonials = testimonials.select_related()
    testimonials = testimonials.order_by('-position', '-create_dt')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'testimonials': testimonials})

def search_redirect(request):
    return HttpResponseRedirect(reverse('testimonials'))
