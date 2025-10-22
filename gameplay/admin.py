from django.contrib import admin
from .models import UserProgress, UserInventory, QuestRating

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'quest', 'current_scene', 'is_completed', 'last_played']
    list_filter = ['is_completed']

admin.site.register(UserInventory)
admin.site.register(QuestRating)