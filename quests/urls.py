from django.urls import path
from . import views

app_name = 'quests'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('catalog/', views.quest_catalog_view, name='catalog'),
    path('quest/<int:pk>/', views.quest_detail_view, name='detail'),

    # Конструктор
    path('create/', views.quest_create_view, name='create'),
    path('quest/<int:pk>/editor/', views.quest_editor_view, name='editor'),
    path('quest/<int:pk>/update/', views.quest_update_view, name='update'),
    path('quest/<int:pk>/publish/', views.quest_publish_view, name='publish'),
    path('quest/<int:pk>/unpublish/', views.quest_unpublish_view, name='unpublish'),

    # API для сцен
    path('api/quest/<int:quest_pk>/scene/create/', views.scene_create_api, name='scene_create_api'),
    path('api/scene/<int:scene_pk>/update/', views.scene_update_api, name='scene_update_api'),
    path('api/scene/<int:scene_pk>/delete/', views.scene_delete_api, name='scene_delete_api'),

    # API для выборов
    path('api/scene/<int:scene_pk>/choice/create/', views.choice_create_api, name='choice_create_api'),
    path('api/choice/<int:choice_pk>/update/', views.choice_update_api, name='choice_update_api'),
    path('api/choice/<int:choice_pk>/delete/', views.choice_delete_api, name='choice_delete_api'),
]