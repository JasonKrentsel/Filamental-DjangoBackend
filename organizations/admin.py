from django.contrib import admin
from .models import Organization, UserOrganizationRelation

admin.site.register(Organization)
admin.site.register(UserOrganizationRelation)
