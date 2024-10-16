from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(DirectoryModel)
admin.site.register(FileModel)
