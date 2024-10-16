from rest_framework import serializers
from filesystem.models import DirectoryModel, FileModel
from organizations.models import Organization
from django.db.transaction import atomic
from django.core.files.uploadedfile import InMemoryUploadedFile

from rag.models import RAG_FILE_TYPES, RAGFileProfile


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
        model = DirectoryModel
        fields = ['new_directory_name', 'parent_directory_id']

    @atomic
    def create(self, validated_data):
        name = validated_data.pop('new_directory_name')
        parent_directory_id = validated_data.pop('parent_directory_id')
        creator = self.context.get('request').user

        parent_directory = DirectoryModel.objects.get(id=parent_directory_id)

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
        model = FileModel
        fields = ['file', 'parent_directory_id']

    @atomic
    def create(self, validated_data):
        file = validated_data.pop('file')
        parent_directory_id = validated_data.pop('parent_directory_id')
        creator = self.context.get('request').user

        parent_directory = DirectoryModel.objects.get(id=parent_directory_id)

        # Ensure file is an InMemoryUploadedFile
        if not isinstance(file, InMemoryUploadedFile):
            raise serializers.ValidationError(
                "Invalid file type. Expected InMemoryUploadedFile.")

        # creating the file
        fileInstance = FileModel.objects.create(
            file=file,
            name=file.name,
            directory=parent_directory,
            created_by=creator,
            organization=parent_directory.organization,
            file_size=file.size,
            file_type=file.content_type.split('/')[1]
        )

        # now we must create the rag file profile, IF it is a supported file type
        print(fileInstance.file_type)
        if fileInstance.file_type in RAG_FILE_TYPES:
            try:
                RAGFileProfile.objects.create(
                    fileInstance=fileInstance,
                    organization=parent_directory.organization,
                )
            except Exception as e:
                # delete the file we just created
                fileInstance.delete()
                raise e
        return fileInstance
