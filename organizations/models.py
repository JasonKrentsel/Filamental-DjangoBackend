from django.db import models
from django.conf import settings
from .managers import OrganizationModelManager
import uuid


class Organization(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_of', null=False, blank=False)
    storage_limit_gb = models.IntegerField(default=10)
    root_directory = models.ForeignKey(
        'filesystem.Directory', on_delete=models.CASCADE, related_name='root_directory', null=True)

    objects = OrganizationModelManager()


class UserOrganizationRelation(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='user_org_relations', null=False, blank=False)
    role = models.CharField(max_length=10, choices=[
        ('member', 'Member'), ('admin', 'Admin'), ('owner', 'Owner')], null=False, blank=False)
