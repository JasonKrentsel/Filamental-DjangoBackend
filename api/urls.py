from django.urls import path, include
from . import views

user_patterns = [
    path('org-descriptions/', views.get_OrgDescriptions,
         name='get_org_descriptions'),
    path('create-org/', views.create_Org, name='create_org'),

]

organization_patterns = [
    path('get-directory-by-id/<str:directory_id>/',
         views.get_directory_by_id, name='get_directory_by_id'),

    path('new-directory/', views.create_directory, name='create_directory'),
    path('new-file/', views.create_file, name='create_file'),

    # path('delete-folder/', views.delete_folder, name='delete_folder'),
    # path('delete-file/', views.delete_file, name='delete_file'),
]

urlpatterns = [
    path('user/', include(user_patterns)),
    path('organization/', include(organization_patterns)),
]
