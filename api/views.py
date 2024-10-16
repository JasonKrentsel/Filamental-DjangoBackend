import json
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.transaction import atomic

from filesystem.models import DirectoryModel
from .serializers import DirectoryCreateSerializer, OrgCreateSerializer, FileCreateSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_OrgDescriptions(request):
    '''
    Get the descriptions of the organizations the user is in

    In the json format, it should be like this:
    {
        "org_name": string;
        "org_icon_src": string;
        "org_id": string;
        "org_root_directory_id": string;
    }
    '''
    user = request.user
    orgRelations = user.organizationRelation.all()

    orgs = []
    for orgRel in orgRelations:
        orgs.append({
            "org_name": orgRel.organization.name,
            "org_icon_src": "",  # TODO: implement once we have org logos
            "org_id": orgRel.organization.id,
            "org_root_directory_id": orgRel.organization.root_directory.id,
        })

    # Return the list of dictionaries directly
    return Response(orgs, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@atomic
def create_Org(request):
    '''
    Create a new organization

    In the json format, it should be like this:
    {
        "new_org_name": string;
    }

    returns a standard org description
    {
        "org_name": string;
        "org_icon_src": string;
        "org_id": string;
        "org_root_directory_id": string;
    }
    '''
    serializer = OrgCreateSerializer(
        data=request.data, context={'request': request})
    if serializer.is_valid():
        org = serializer.save()
        return Response({
            "org_name": org.name,
            "org_icon_src": "",  # TODO: implement once we have org logos
            "org_id": org.id,
            "org_root_directory_id": org.root_directory.id,
        }, status=status.HTTP_201_CREATED)

    print(serializer.errors)
    print(request.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_directory_by_id(request, id):
    '''
    Get a directory by its id

    In the json format, it should be like this:
    {
        "id": string;
    }

    This returns a DirectoryContents Object:

    DirectoryContents = {
        "id": string;
        "name": string;
        "files": FileDescription[];
        "sub_directories": SubDirectoryDescription[];
    }

    FileDescription = {
        "id": string;
        "name": string;
        "created_at": Date;
        "created_by": string;
        "file_size": number;
        "embedded": boolean;
    }

    SubDirectoryDescription = {
        "id": string;
        "name": string;
        "created_at": Date;
        "created_by": string;
    }
    '''

    print(f"\033[94mGetting directory by id: {id}\033[0m")

    try:
        directory = DirectoryModel.objects.get(id=id)
    except DirectoryModel.DoesNotExist:
        print(f"\033[Directory does not exist: {id}\033[0m")
        return Response({"error": "Directory does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has access to the directory's organization
    if not request.user.organizationRelation.filter(organization_id=directory.organization_id).exists():
        return Response({"error": "You don't have access to this directory's organization"}, status=status.HTTP_403_FORBIDDEN)

    # If we've reached this point, the directory exists and the user has access

    files = []
    sub_directories = []

    for file in directory.files.all():
        files.append({
            "id": file.id,
            "name": file.name,
            "created_at": file.created_at,
            "created_by": file.created_by.getName(),
            "file_size": file.file_size,
            "embedded": file.rag_file_profile.exists(),
        })

    for sub_directory in directory.get_children():
        sub_directories.append({
            "id": sub_directory.id,
            "name": sub_directory.name,
            "created_at": sub_directory.created_at,
            "created_by": sub_directory.created_by.getName(),
        })

    return Response({"id": directory.id, "name": directory.name, "files": files, "sub_directories": sub_directories}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@atomic
def create_directory(request):
    '''
    Create a new directory in the organization

    In the json format, it should be like this:
    {
        "new_directory_name": string;
        "parent_directory_id": string;
    }

    This returns a subdirectory description:

    {
        "id": string;
        "name": string;
        "created_at": Date;
        "created_by": string;
    }
    '''

    user = request.user

    try:
        parent_directory_id = request.data.get('parent_directory_id')
        parent_directory = DirectoryModel.objects.get(id=parent_directory_id)

        # Check if the user has access to the parent directory's organization
        if not user.organizationRelation.filter(organization_id=parent_directory.organization_id).exists():
            return Response({"error": "You don't have access to this directory's organization"}, status=status.HTTP_403_FORBIDDEN)
    except DirectoryModel.DoesNotExist:
        parent_directory = None

    # if parent directory doesn't exist, return an error
    if not parent_directory:
        return Response({"error": "Parent directory does not exist or does not belong to the specified organization"}, status=status.HTTP_403_FORBIDDEN)

    # check if there is a directory with the same name in the parent directory
    if parent_directory.get_children().filter(name=request.data.get('new_directory_name')).exists():
        return Response({"error": "Directory with the same name already exists"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = DirectoryCreateSerializer(
        data=request.data, context={'request': request})
    if serializer.is_valid():
        directory = serializer.save()
        return Response({
            "id": directory.id,
            "name": directory.name,
            "created_at": directory.created_at,
            # TODO: change to user id when we can get it for avatars
            "created_by": directory.created_by.getName(),
        }, status=status.HTTP_201_CREATED)

    print(serializer.errors)
    print(request.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@atomic
def create_file(request):
    '''
    Create a new file in the organization

    In the json format, it should be like this:
    {
        "file": File;
        "parent_directory_id": string;
    }
    '''
    user = request.user

    parent_directory_id = request.data.get('parent_directory_id')
    parent_directory = DirectoryModel.objects.get(id=parent_directory_id)

    # Check if the user has access to the directory's organization
    if not user.organizationRelation.filter(organization_id=parent_directory.organization_id).exists():
        return Response({"error": "You don't have access to this directory's organization"}, status=status.HTTP_403_FORBIDDEN)

    # check if there is a file with the same name in the parent directory
    file_name = request.data.get(
        'file').name if 'file' in request.data else None
    if file_name and parent_directory.files.filter(name=file_name).exists():
        return Response({"error": "File with the same name already exists"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = FileCreateSerializer(
        data=request.data, context={'request': request})
    if serializer.is_valid():
        file = serializer.save()
        return Response({"file_id": file.id}, status=status.HTTP_201_CREATED)

    print(serializer.errors)
    print(request.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
