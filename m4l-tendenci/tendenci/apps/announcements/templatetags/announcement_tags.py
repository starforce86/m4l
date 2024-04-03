from django.template import Library

from tendenci.apps.announcements.models import EmergencyAnnouncement
from tendenci.apps.perms.utils import get_query_filters

register = Library()


@register.inclusion_tag("announcements/emergency_area.html", takes_context=True)
def emergency_announcement(context, user):

    filters = get_query_filters(user, 'announcements.view_emergencyannouncement')
    announcements = EmergencyAnnouncement.objects.filter(filters).distinct()
    announcements = announcements.filter(enabled=True).order_by('-create_dt')

    context.update({
        "user": user,
        "announcements": announcements
    })
    return context
