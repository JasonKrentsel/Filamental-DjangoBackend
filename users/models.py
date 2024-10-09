from organizations.models import UserOrganizationRelation
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from .managers import UserModelManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=False)
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    organizationRelation = models.ManyToManyField(
        UserOrganizationRelation, related_name='user_organization_relations')
    profile = models.OneToOneField(
        'UserProfile', on_delete=models.CASCADE, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects: UserModelManager = UserModelManager()

    def add_org_relation(self, org, role):
        new_relation = UserOrganizationRelation.objects.create(
            organization=org, role=role)
        new_relation.save()
        self.organizationRelation.add(new_relation)
        self.save()
        return new_relation

    def getName(self):
        return f"{self.first_name} {self.last_name}"


class UserProfile(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True)
