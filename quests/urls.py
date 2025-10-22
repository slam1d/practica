from django.urls import path
from . import views

app_name = 'quests'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('catalog/', views.quest_catalog_view, name='catalog'),
    path('quest/<int:pk>/', views.quest_detail_view, name='detail'),
]
