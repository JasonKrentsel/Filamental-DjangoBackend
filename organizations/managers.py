from django.db import models
from django.apps import apps
from django.db.transaction import atomic


class OrganizationModelManager(models.Manager):
    @atomic
    def create_organization(self, name, ownerUser):
        DirectoryModel = apps.get_model('filesystem', 'Directory')

        organization = super().create(
            name=name, owner=ownerUser)

        root_directory = DirectoryModel.add_root(
            name=f"{name} Home", organization=organization, created_by=ownerUser)

        organization.root_directory = root_directory
        organization.save()

        ownerUser.add_org_relation(organization, 'owner')

        return organization

    def create(self, **kwargs):
        raise NotImplementedError("Use create_organization instead.")
