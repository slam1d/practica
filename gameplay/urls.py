from django.urls import path
from . import views

app_name = 'gameplay'

urlpatterns = [
    path('quest/<int:quest_pk>/start/', views.quest_start_view, name='start'),
    path('play/<int:progress_pk>/', views.quest_play_view, name='play'),
    path('play/<int:progress_pk>/choice/<int:choice_pk>/', views.quest_choice_view, name='choice'),
    path('play/<int:progress_pk>/restart/', views.quest_restart_view, name='restart'),
    path('play/<int:progress_pk>/abandon/', views.quest_abandon_view, name='abandon'),
    path('quest/<int:quest_pk>/rate/', views.rate_quest_view, name='rate'),
]