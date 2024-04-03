from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from tendenci.apps.perms.managers import ObjectPermissionManager
from tendenci.apps.user_groups.models import Group


class ObjectPermission(models.Model):
    """
    Object level permissions

    Don't move this model into the models.py
    because it will cause circular references
    all over the place. Please leave it here.
    """
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    codename = models.CharField(max_length=255)
    object_id = models.IntegerField()
    create_dt = models.DateTimeField(auto_now_add=True)
    object = GenericForeignKey('content_type', 'object_id')

    objects = ObjectPermissionManager()

    class Meta:
        app_label = 'perms'
