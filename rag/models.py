import uuid
from django.db import models

from filesystem.models import FileModel
from organizations.models import Organization
from rag.utils.ragUtil import file_to_summaries, summary_to_embeddings


RAG_FILE_TYPES = ['pdf', 'plain']


class RAGFileProfileManager(models.Manager):
    def create(self, fileInstance: FileModel, organization: Organization):
        if fileInstance.file_type not in RAG_FILE_TYPES:
            raise ValueError(
                f"File type {fileInstance.file_type} is not supported for RAG")

        rag_file_profile = super().create(file=fileInstance, organization=organization)

        summaries = file_to_summaries(fileInstance)

        for page_number, summary in enumerate(summaries):
            RAGPage.objects.create(
                rag_file_profile=rag_file_profile,
                page_number=page_number,
                summary=summary,
                embeddings=summary_to_embeddings(summary)
            )

        return rag_file_profile


class RAGFileProfile(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.ForeignKey(
        FileModel, on_delete=models.CASCADE, related_name='rag_file_profile')
    organization = models.ForeignKey(
        'organizations.Organization', on_delete=models.CASCADE, related_name='rag_file_profiles')

    objects = RAGFileProfileManager()


class RAGPage(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    rag_file_profile = models.ForeignKey(
        RAGFileProfile, on_delete=models.CASCADE, related_name='rag_pages')
    page_number = models.IntegerField(null=False, blank=False)

    # summary is the summary of the page, generated by the LLM
    summary = models.TextField(null=False, blank=False)

    # embeddings is a list of embeddings for each token in the page
    # in the format of [[embedding], [embedding], ...]
    embeddings = models.JSONField(null=False, blank=False)

    class Meta:
        ordering = ['page_number']
