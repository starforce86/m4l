
from haystack.query import SearchQuerySet
from haystack.backends import SQ

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from tendenci.apps.perms.object_perms import ObjectPermission


PUBLIC_FILTER = {'status':True,'status_detail':"active",'allow_anonymous_view':True}

def set_perm_bits(request, form, instance):
    """
    Sets object-level permissions bits for a model instance
    """
    # owners and creators
    if not instance.pk:
        if request.user.is_authenticated:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username

    # set up user permissions
    if 'user_perms' in form.cleaned_data:
        instance.allow_user_view, instance.allow_user_edit = form.cleaned_data['user_perms']
    else:
        instance.allow_user_view, instance.allow_user_edit = False, False

    # set up member permissions
    if 'member_perms' in form.cleaned_data:
        instance.allow_member_view, instance.allow_member_edit = form.cleaned_data['member_perms']
    else:
        instance.allow_member_view, instance.allow_member_edit = False, False

    return instance


def update_perms_and_save(request, form, instance, **kwargs):
    """
    Adds object row-level permissions for a model instance
    """
    # permissions bits
    instance = set_perm_bits(request, form, instance)

    if not request.user.is_anonymous:
        if not instance.pk:
            if hasattr(instance, 'creator'):
                instance.creator = request.user
            if hasattr(instance, 'creator_username'):
                instance.creator_username = request.user.username

        if hasattr(instance, 'owner'):
            instance.owner = request.user
        if hasattr(instance, 'owner_username'):
            instance.owner_username = request.user.username

    # save the instance because we need the primary key
    if instance.pk:
        ObjectPermission.objects.remove_all(instance)
    else:
        try:
            instance.save()
        except Exception as e:
            print('boom! in update_perms_and_save()', e)

    # assign permissions for selected groups
    if 'group_perms' in form.cleaned_data:
        ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], instance)

    # save again for indexing purposes
    # TODO: find a better solution, saving twice kinda sux
    instance.save(**kwargs)

    # assign the permission to the medial files
    assign_files_perms(instance)

    return instance


def assign_files_perms(instance, **kwargs):
    from tendenci.apps.files.models import File
    files = kwargs.pop('files', None)
    # get content type and instance
    content_type = ContentType.objects.get_for_model(instance.__class__)

    if not files:
        orphaned_files = File.objects.filter(content_type=content_type, object_id=0)
        if hasattr(instance, 'owner') and instance.owner:
            # When adding new content (articles, news,...), files uploaded would not be
            # associated with any object, thus the orphaned files.
            # Only update perms for the orphaned files OWNED by this user.
            orphaned_files = orphaned_files.filter(creator=instance.owner)
        orphaned_files = list(orphaned_files)
        coupled_files = list(File.objects.filter(content_type=content_type, object_id=instance.pk))
        files = orphaned_files + coupled_files

    file_ct = ContentType.objects.get_for_model(File)

    perm_attrs = []

    tmp_perm_attrs = [
        'allow_anonymous_view',
        'allow_user_view',
        'allow_member_view',
        'allow_user_edit',
        'allow_member_edit',
        'status',
        'status_detail',
    ]

    for attr in tmp_perm_attrs:
        if hasattr(instance, attr):
            perm_attrs.append(attr)

    for file in files:  # loop through media files and update
        if not file.object_id:  # pick up orphans
            file.object_id = instance.pk

        # remove all group permissions on file
        ObjectPermission.objects.filter(
            content_type=file_ct, object_id=file.pk, group__isnull=False).delete()

        # get all instance permissions [for copying]
        instance_perms = ObjectPermission.objects.filter(
            content_type=content_type, object_id=instance.pk, group__isnull=False
        )

        # copy instance group permissions to file
        for file_perm in instance_perms:
            file_perm.pk = None
            file_perm.content_type = file_ct
            file_perm.object_id = file.pk
            file_perm.codename = '%s_%s' % (file_perm.codename.split('_')[0], 'file')
            file_perm.save()

        # copy permission attributes
        for attr in perm_attrs:
            # example: file.status = instance.status
            setattr(file, attr, getattr(instance, attr))

        # only update file instances that have changed
        if file.has_changed():
            # Update the owner and owner_username since we are
            # updating the update_dt automatically.
            if hasattr(instance, 'owner'):
                file.owner = instance.owner
            if hasattr(instance, 'owner_username'):
                file.owner_username = instance.owner_username

            file.save()


def has_perm(user, perm, obj=None):
    """
        A simple wrapper around the user.has_perm
        functionality.
    """
    if user.profile.is_superuser:
        return True
    allowed = user.has_perm(perm, obj)
    trace_perm(user, perm, obj, allowed)

    return allowed


def trace_perm(user, perm, obj, allowed):
    if not hasattr(user, '_perm_trace'):
        return

    if not hasattr(user, '_group_perm_origin'):
        return

    if allowed:
        for (content_type, name, group) in user._group_perm_origin:
            owned = "%s.%s" % (content_type, name)
            if perm == owned:
                user._perm_trace.append(dict(
                    perm=perm,
                    allowed=allowed,
                    granted_by=group,
                ))
    else:
        user._perm_trace.append(dict(
                    perm=perm,
                    allowed=allowed,
                    granted_by=None,
                ))


def has_view_perm(user, perm, obj=None):
    """
    Method used in details views to check permissions faster on a single object.
    """
    obj.status_detail = obj.status_detail.lower()
    active_status_details = ("active", 'published')
    if obj:
        if user.is_anonymous:
            if obj.status and obj.status_detail in active_status_details and obj.allow_anonymous_view:
                return True
            else:
                return False
        elif user.profile.is_superuser:
            return True
        elif obj.creator_id == user.pk or obj.owner_id == user.pk:
            return True
        elif user.profile.is_member and obj.status and obj.status_detail in active_status_details \
                    and (obj.allow_anonymous_view or obj.allow_user_view or obj.allow_member_view):
            return True
        elif obj.status and obj.status_detail in active_status_details \
                    and (obj.allow_anonymous_view or obj.allow_user_view):
            return True
        else:
            return has_perm(user, perm, obj)
    return False


def get_query_filters(user, perm, **kwargs):
    """
    Method to generate search query filters for different user types.
    * super_perm kwarg simulates admin behavior.
    """

    perms_field = kwargs.get('perms_field', True)
    #super_perm = kwargs.get('super_perm', False)

    group_perm = Q()
    group_q = Q()

    if not isinstance(user, User) or user.is_anonymous:
        anon_q = Q(allow_anonymous_view=True)
        status_q = Q(status=True)
        status_detail_q = Q(status_detail__in=['active', 'published'])
        anon_filter = (anon_q & status_q & status_detail_q)
        return anon_filter
    else:
        if user.profile.is_superuser:
            return Q(status=True)
        else:

            if '.' in perm and perms_field:
                group_perm = Q(perms__codename=perm.split(".")[-1])

            # skip checking the allow_xxx_view for profiles 'cause those fields are not editable in profiles
            if perm == 'profiles.view_profile':
                return (Q(status=True) & group_perm & Q(status_detail='active')) | (Q(creator=user) | Q(owner=user))

            if user.profile.is_member:
                anon_q = Q(allow_anonymous_view=True)
                user_q = Q(allow_user_view=True)
                member_q = Q(allow_member_view=True)
                status_q = Q(status=True)
                status_detail_q = Q(status_detail__in=['active', 'published'])

                if perms_field:
                    group_ids = [int(g.group.id) for g in user.group_member.select_related('group')]
                    group_q = Q(perms__group__in=group_ids)

                creator_perm_q = Q(creator=user)
                owner_perm_q = Q(owner=user)
                member_filter = (status_q & (((anon_q | user_q | member_q | (group_q & group_perm)) & status_detail_q) | (creator_perm_q | owner_perm_q)))

                return member_filter
            else:
                anon_q = Q(allow_anonymous_view=True)
                user_q = Q(allow_user_view=True)
                status_q = Q(status=True)
                status_detail_q = Q(status_detail__in=['active', 'published'])

                if perms_field:
                    group_ids = [int(g.group.id) for g in user.group_member.select_related('group')]
                    group_q = Q(perms__group__in=group_ids)

                creator_perm_q = Q(creator=user)
                owner_perm_q = Q(owner=user)
                user_filter = (status_q & (((anon_q | user_q | (group_q & group_perm)) & status_detail_q) | (creator_perm_q | owner_perm_q)))

                return user_filter


def get_groups_query_filters(user, **kwargs):
    """
    This function generates the query filters for a list of groups that
    the user has the CHANGE (EDIT) permission.

    For example, for the group dropdown on newsletters generator,
      only those groups that the user can change will show up.
    """
    if not isinstance(user, User) or user.is_anonymous:
        return Q()
    else:
        if user.profile.is_superuser:
            return Q(status=True)
        elif has_perm(user, 'user_groups.change_group'):
            return Q(status=True, status_detail__in=['active', 'published'])
        else:
            from tendenci.apps.user_groups.models import Group
            group_q = Q()
            perm = 'change_group'
            # groups user is member of
            group_ids = [int(g.group.id) for g in user.group_member.select_related('group')]

            content_type = ContentType.objects.get(
                    app_label=Group._meta.app_label, model=Group._meta.model_name)
            # get a list of groups that the user can change
            group_ids_with_perm = ObjectPermission.objects.filter(
                            codename=perm,
                            content_type=content_type,
                            ).filter(Q(group__in=group_ids) | Q(user=user)
                                             ).values_list('object_id', flat=True)
            if group_ids_with_perm:
                group_q = Q(id__in=group_ids_with_perm)

            status_q = Q(status=True)
            status_detail_q = Q(status_detail__in=['active', 'published'])
            creator_perm_q = Q(creator=user)
            owner_perm_q = Q(owner=user)

            if user.profile.is_member:
                user_q = Q(allow_user_edit=True)
                member_q = Q(allow_member_edit=True)
                return (status_q & (((user_q | member_q | group_q) & status_detail_q) | (creator_perm_q | owner_perm_q)))
            else:
                user_q = Q(allow_user_edit=True)
                return (status_q & (((user_q | group_q) & status_detail_q) | (creator_perm_q | owner_perm_q)))


def get_administrators():
    return User.objects.filter(is_active=True, is_staff=True)


# get a list of the admin notice recipients
def get_notice_recipients(scope, scope_category, setting_name):
    from tendenci.apps.site_settings.utils import get_setting
    from tendenci.apps.base.utils import validate_email

    recipients = []
    # global recipients
    g_recipients = (get_setting('site', 'global', 'allnoticerecipients')).split(',')
    g_recipients = [r.strip() for r in g_recipients]

    # module recipients
    m_recipients = (get_setting(scope, scope_category, setting_name)).split(',')
    m_recipients = [r.strip() for r in m_recipients]

    # consolidate [remove duplicate email address]
    for recipient in list(set(g_recipients + m_recipients)):
        if validate_email(recipient):
            recipients.append(recipient)

    # if the settings for notice recipients are not set up, return admin contact email
    if not recipients:
        admin_contact_email = (get_setting('site', 'global', 'admincontactemail')).strip()
        recipients = admin_contact_email.split(',')

    return recipients


def _specific_view(user, obj):
    """
    determines if a user has specific permissions to view the object.
    note this is based only on:

    (users_can_view contains user)
    +
    (groups_can_view contains one of user's groups)
    """
    sqs = SearchQuerySet()
    sqs = sqs.models(obj.__class__)

    groups = [g.pk for g in user.user_groups.all()]

    q_primary_key = SQ(primary_key=obj.pk)
    q_groups = SQ(groups_can_view__in=groups)
    q_users = SQ(users_can_view__in=[user.pk])

    if groups:
        sqs = sqs.filter(q_primary_key & (q_groups | q_users))
    else:
        sqs = sqs.filter(q_primary_key & q_users)

    if sqs:
        # Make sure the index isn't doing something unexpected with the query,
        # like when the Whoosh StopFilter caused the primary_key portion of the
        # query to be ignored.
        assert len(sqs) == 1, "Index returned an unexpected result set when searching for view permissions on an object"
        return True

    return False


def can_view(user, obj):
    """
    Checks for tendenci specific permissions to viewing objects
    through the search index
    """
    return _specific_view(user, obj)
