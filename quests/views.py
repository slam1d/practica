from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from .models import Quest, Tag, Scene
from gameplay.models import QuestRating


def home_view(request):
    """Главная страница с популярными квестами"""
    # Популярные квесты (по количеству прохождений)
    popular_quests = Quest.objects.filter(is_published=True).order_by('-play_count')[:6]

    # Теги для фильтрации
    tags = Tag.objects.all()

    context = {
        'popular_quests': popular_quests,
        'tags': tags,
    }
    return render(request, 'quests/home.html', context)


def quest_catalog_view(request):
    """Каталог всех квестов с фильтрами"""
    quests = Quest.objects.filter(is_published=True)

    # Фильтр по жанру (тегу)
    tag_slug = request.GET.get('tag')
    if tag_slug:
        quests = quests.filter(tags__slug=tag_slug)

    # Фильтр по сложности
    difficulty = request.GET.get('difficulty')
    if difficulty:
        quests = quests.filter(difficulty=difficulty)

    # Поиск по названию
    search_query = request.GET.get('search')
    if search_query:
        quests = quests.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Сортировка
    sort = request.GET.get('sort', '-created_at')
    quests = quests.order_by(sort)

    tags = Tag.objects.all()

    context = {
        'quests': quests,
        'tags': tags,
        'current_tag': tag_slug,
        'current_difficulty': difficulty,
        'search_query': search_query,
    }
    return render(request, 'quests/catalog.html', context)


def quest_detail_view(request, pk):
    """Детальная страница квеста"""
    quest = get_object_or_404(Quest, pk=pk, is_published=True)

    # Средний рейтинг
    avg_rating = quest.ratings.aggregate(Avg('rating'))['rating__avg']
    ratings = quest.ratings.all().order_by('-created_at')[:5]

    # Проверка прогресса пользователя
    user_progress = None
    if request.user.is_authenticated:
        from gameplay.models import UserProgress
        user_progress = UserProgress.objects.filter(
            user=request.user,
            quest=quest
        ).first()

    context = {
        'quest': quest,
        'avg_rating': avg_rating,
        'ratings': ratings,
        'user_progress': user_progress,
    }
    return render(request, 'quests/detail.html', context)