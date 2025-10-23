from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from .models import Quest, Tag, Scene, Choice
from gameplay.models import QuestRating
import json


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


@login_required
def quest_create_view(request):
    """Создание нового квеста"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        difficulty = request.POST.get('difficulty', 'medium')
        estimated_time = request.POST.get('estimated_time', 30)

        quest = Quest.objects.create(
            title=title,
            description=description,
            author=request.user,
            difficulty=difficulty,
            estimated_time=estimated_time,
            is_published=False
        )

        # Создаём начальную сцену
        Scene.objects.create(
            quest=quest,
            title='Начало',
            content='Начало вашего квеста. Отредактируйте этот текст.',
            order=1,
            is_starting_scene=True
        )

        messages.success(request, f'Квест "{title}" создан!')
        return redirect('quests:editor', pk=quest.pk)

    return render(request, 'quests/create.html')


@login_required
def quest_editor_view(request, pk):
    """Редактор квеста"""
    quest = get_object_or_404(Quest, pk=pk, author=request.user)
    scenes = quest.scenes.all().order_by('order')
    tags = Tag.objects.all()

    context = {
        'quest': quest,
        'scenes': scenes,
        'tags': tags,
    }
    return render(request, 'quests/editor.html', context)


@login_required
def quest_update_view(request, pk):
    """Обновление основной информации о квесте"""
    quest = get_object_or_404(Quest, pk=pk, author=request.user)

    if request.method == 'POST':
        quest.title = request.POST.get('title', quest.title)
        quest.description = request.POST.get('description', quest.description)
        quest.difficulty = request.POST.get('difficulty', quest.difficulty)
        quest.estimated_time = request.POST.get('estimated_time', quest.estimated_time)

        # Обработка тегов
        tag_ids = request.POST.getlist('tags')
        quest.tags.set(tag_ids)

        quest.save()
        messages.success(request, 'Квест обновлён!')
        return redirect('quests:editor', pk=quest.pk)

    return redirect('quests:editor', pk=quest.pk)


@login_required
def quest_publish_view(request, pk):
    """Публикация квеста"""
    quest = get_object_or_404(Quest, pk=pk, author=request.user)

    # Проверка: есть ли хотя бы одна сцена
    if quest.scenes.count() == 0:
        messages.error(request, 'Нельзя опубликовать квест без сцен!')
        return redirect('quests:editor', pk=quest.pk)

    # Проверка: есть ли начальная сцена
    if not quest.scenes.filter(is_starting_scene=True).exists():
        messages.error(request, 'Необходимо отметить начальную сцену!')
        return redirect('quests:editor', pk=quest.pk)

    quest.is_published = True
    quest.save()
    messages.success(request, 'Квест опубликован! Теперь его могут видеть другие пользователи.')
    return redirect('quests:detail', pk=quest.pk)


@login_required
def quest_unpublish_view(request, pk):
    """Снятие квеста с публикации"""
    quest = get_object_or_404(Quest, pk=pk, author=request.user)
    quest.is_published = False
    quest.save()
    messages.info(request, 'Квест снят с публикации.')
    return redirect('quests:editor', pk=quest.pk)


# === API для работы со сценами ===

@login_required
def scene_create_api(request, quest_pk):
    """API: Создание новой сцены"""
    if request.method == 'POST':
        quest = get_object_or_404(Quest, pk=quest_pk, author=request.user)
        data = json.loads(request.body)

        # Определяем следующий порядковый номер
        max_order = quest.scenes.aggregate(models.Max('order'))['order__max'] or 0

        scene = Scene.objects.create(
            quest=quest,
            title=data.get('title', 'Новая сцена'),
            content=data.get('content', 'Описание сцены...'),
            order=max_order + 1
        )

        return JsonResponse({
            'success': True,
            'scene': {
                'id': scene.id,
                'title': scene.title,
                'content': scene.content,
                'order': scene.order,
                'is_starting_scene': scene.is_starting_scene,
                'is_ending_scene': scene.is_ending_scene,
            }
        })

    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
def scene_update_api(request, scene_pk):
    """API: Обновление сцены"""
    if request.method == 'POST':
        scene = get_object_or_404(Scene, pk=scene_pk, quest__author=request.user)
        data = json.loads(request.body)

        scene.title = data.get('title', scene.title)
        scene.content = data.get('content', scene.content)
        scene.is_starting_scene = data.get('is_starting_scene', scene.is_starting_scene)
        scene.is_ending_scene = data.get('is_ending_scene', scene.is_ending_scene)
        scene.save()

        return JsonResponse({
            'success': True,
            'scene': {
                'id': scene.id,
                'title': scene.title,
                'content': scene.content,
                'is_starting_scene': scene.is_starting_scene,
                'is_ending_scene': scene.is_ending_scene,
            }
        })

    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
def scene_delete_api(request, scene_pk):
    """API: Удаление сцены"""
    if request.method == 'POST':
        scene = get_object_or_404(Scene, pk=scene_pk, quest__author=request.user)
        scene_id = scene.id
        scene.delete()

        return JsonResponse({'success': True, 'deleted_id': scene_id})

    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
def choice_create_api(request, scene_pk):
    """API: Создание выбора"""
    if request.method == 'POST':
        scene = get_object_or_404(Scene, pk=scene_pk, quest__author=request.user)
        data = json.loads(request.body)

        next_scene_id = data.get('next_scene_id')
        next_scene = None
        if next_scene_id:
            next_scene = Scene.objects.filter(
                id=next_scene_id,
                quest=scene.quest
            ).first()

        max_order = scene.choices.aggregate(models.Max('order'))['order__max'] or 0

        choice = Choice.objects.create(
            scene=scene,
            text=data.get('text', 'Новый выбор'),
            next_scene=next_scene,
            order=max_order + 1
        )

        return JsonResponse({
            'success': True,
            'choice': {
                'id': choice.id,
                'text': choice.text,
                'next_scene_id': choice.next_scene.id if choice.next_scene else None,
                'order': choice.order,
            }
        })

    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
def choice_update_api(request, choice_pk):
    """API: Обновление выбора"""
    if request.method == 'POST':
        choice = get_object_or_404(Choice, pk=choice_pk, scene__quest__author=request.user)
        data = json.loads(request.body)

        choice.text = data.get('text', choice.text)

        next_scene_id = data.get('next_scene_id')
        if next_scene_id:
            next_scene = Scene.objects.filter(
                id=next_scene_id,
                quest=choice.scene.quest
            ).first()
            choice.next_scene = next_scene
        else:
            choice.next_scene = None

        choice.save()

        return JsonResponse({
            'success': True,
            'choice': {
                'id': choice.id,
                'text': choice.text,
                'next_scene_id': choice.next_scene.id if choice.next_scene else None,
            }
        })

    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
def choice_delete_api(request, choice_pk):
    """API: Удаление выбора"""
    if request.method == 'POST':
        choice = get_object_or_404(Choice, pk=choice_pk, scene__quest__author=request.user)
        choice_id = choice.id
        choice.delete()

        return JsonResponse({'success': True, 'deleted_id': choice_id})

    return JsonResponse({'success': False, 'error': 'Invalid method'})