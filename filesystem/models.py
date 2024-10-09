import uuid
from django.db import models
from treebeard.mp_tree import MP_Node
from django.contrib.auth import get_user_model

User = get_user_model()


class Directory(MP_Node):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)  # Edit 1
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        'organizations.Organization', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_directories')

    def __str__(self):
        return self.name

    def get_path(self):
        # Get ancestors and convert to list
        ancestors = list(self.get_ancestors())
        # Manually include the current directory
        full_path = ancestors + [self]
        # Use the directory names to construct the path, starting from the root
        return '/'.join([str(ancestor.id) for ancestor in full_path])


class File(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)  # Edit 2
    name = models.CharField(max_length=255)
    directory = models.ForeignKey(
        Directory, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_size = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_files')
    organization = models.ForeignKey(
        'organizations.Organization', on_delete=models.CASCADE)

    def upload_file_to(self, filename):
        return f"{self.organization.id}/{filename}"

    file = models.FileField(upload_to=upload_file_to, max_length=2024)

    def __str__(self):
        return self.name
