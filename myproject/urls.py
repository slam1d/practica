from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import gameplay

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('gameplay/', include('gameplay.urls')),
    path('', include('quests.urls')),  # Главная страница и квесты
]

# Для отображения загруженных файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)