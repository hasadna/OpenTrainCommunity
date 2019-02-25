from django.contrib import admin
from . import models


@admin.register(models.Story)
class StoryAdmin(admin.ModelAdmin):
    pass

