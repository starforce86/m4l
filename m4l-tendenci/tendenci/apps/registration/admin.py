from django.contrib import admin

from tendenci.apps.registration.models import RegistrationProfile


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'activation_key_expired')
    search_fields = ('user__username', 'user__first_name')


admin.site.register(RegistrationProfile, RegistrationAdmin)
