from rest_framework import serializers
from filesystem.models import Directory, File
from organizations.models import Organization
from django.db.transaction import atomic
from django.core.files.uploadedfile import InMemoryUploadedFile


class OrgCreateSerializer(serializers.ModelSerializer):
    new_org_name = serializers.CharField(max_length=32)

    class Meta:
        model = Organization
        fields = ['new_org_name']

    @atomic
    def create(self, validated_data):
        name = validated_data.pop('new_org_name')
        creator = self.context.get('request').user

        org = Organization.objects.create_organization(
            name=name, ownerUser=creator)

        return org


class DirectoryCreateSerializer(serializers.ModelSerializer):
    new_directory_name = serializers.CharField(max_length=32)
    parent_directory_id = serializers.UUIDField()

    class Meta:
        model = Directory
        fields = ['new_directory_name', 'parent_directory_id']

    @atomic
    def create(self, validated_data):
        name = validated_data.pop('new_directory_name')
        parent_directory_id = validated_data.pop('parent_directory_id')
        creator = self.context.get('request').user

        parent_directory = Directory.objects.get(id=parent_directory_id)

        if parent_directory.organization_id != creator.organizationRelation.filter(organization_id=parent_directory.organization_id).first().organization_id:
            raise serializers.ValidationError(
                "Parent directory does not belong to the same organization as the creator")

        directory = parent_directory.add_child(
            name=name,
            organization=parent_directory.organization,
            created_by=creator
        )

        return directory


class FileCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    parent_directory_id = serializers.UUIDField()

    class Meta:
        model = File
        fields = ['file', 'parent_directory_id']

    @atomic
    def create(self, validated_data):
        file = validated_data.pop('file')
        parent_directory_id = validated_data.pop('parent_directory_id')
        creator = self.context.get('request').user

        parent_directory = Directory.objects.get(id=parent_directory_id)

        # Ensure file is an InMemoryUploadedFile
        if not isinstance(file, InMemoryUploadedFile):
            raise serializers.ValidationError(
                "Invalid file type. Expected InMemoryUploadedFile.")

        file = File.objects.create(
            file=file,
            name=file.name,
            directory=parent_directory,
            created_by=creator,
            organization=parent_directory.organization,
            file_size=file.size
        )

        return file
