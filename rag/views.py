from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.transaction import atomic
from rag.models import RAGFileProfile, RAGPage
from rag.utils.ragUtil import run_rag


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@atomic
def post_query(request):
    '''
    Run a query on the RAG store of a specific organization

    In the json format, it should be like this:
    {
        "query": string;
        "organization_id": string;
    }
    '''

    query = request.data.get('query')
    organization_id = request.data.get('organization_id')
    user = request.user

    # check if the user has access to the organization
    if not user.organizationRelation.filter(organization_id=organization_id).exists():
        return Response({"error": "You don't have access to this organization"}, status=status.HTTP_403_FORBIDDEN)

    # check if the organization has any rag file profiles
    if not RAGFileProfile.objects.filter(organization_id=organization_id).exists():
        return Response({"error": "This organization doesn't have any RAG file profiles"}, status=status.HTTP_404_NOT_FOUND)

    # get the rag file profiles of the organization
    rag_file_profiles = RAGFileProfile.objects.filter(
        organization_id=organization_id)

    # get the rag pages of the rag file profiles
    rag_pages = RAGPage.objects.filter(
        rag_file_profile_id__in=rag_file_profiles.values_list('id', flat=True))

    # Create a list of objects containing embeddings and rag_page ids
    embeddings_with_ids = []
    for page in rag_pages:
        for embedding in page.embeddings:
            embeddings_with_ids.append({
                'embedding': embedding,
                'rag_page_id': page.id
            })

    # run RAG
    similar_embeddings = run_rag(query, embeddings_with_ids)

    # get the rag pages of the similar embeddings
    for embedding in similar_embeddings:
        rag_page = RAGPage.objects.get(id=embedding['rag_page_id'])
        embedding['page'] = rag_page.page_number
        embedding['name'] = rag_page.rag_file_profile.file.name

    return Response(similar_embeddings, status=status.HTTP_200_OK)
