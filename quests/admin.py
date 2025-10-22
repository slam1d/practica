from django.contrib import admin
from .models import Quest, Scene, Choice, Item, Tag

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'difficulty', 'is_published', 'created_at']
    list_filter = ['difficulty', 'is_published', 'tags']
    search_fields = ['title', 'description']

@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ['title', 'quest', 'order', 'is_starting_scene', 'is_ending_scene']
    list_filter = ['quest']

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text', 'scene', 'next_scene']

admin.site.register(Item)
admin.site.register(Tag)