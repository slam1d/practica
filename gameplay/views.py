from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from quests.models import Quest, Scene, Choice
from .models import UserProgress, UserInventory
import json


@login_required
def quest_start_view(request, quest_pk):
    """Начало прохождения квеста"""
    quest = get_object_or_404(Quest, pk=quest_pk, is_published=True)

    # Проверяем, есть ли уже прогресс
    progress = UserProgress.objects.filter(user=request.user, quest=quest).first()

    if progress:
        # Если квест уже начат, продолжаем
        return redirect('gameplay:play', progress_pk=progress.pk)

    # Находим начальную сцену
    starting_scene = quest.scenes.filter(is_starting_scene=True).first()

    if not starting_scene:
        messages.error(request, 'В квесте не указана начальная сцена!')
        return redirect('quests:detail', pk=quest.pk)

    # Создаём новый прогресс
    progress = UserProgress.objects.create(
        user=request.user,
        quest=quest,
        current_scene=starting_scene
    )

    # Увеличиваем счётчик прохождений
    quest.play_count += 1
    quest.save()

    messages.success(request, f'Квест "{quest.title}" начат!')
    return redirect('gameplay:play', progress_pk=progress.pk)


@login_required
def quest_play_view(request, progress_pk):
    """Основной плеер квеста"""
    progress = get_object_or_404(
        UserProgress,
        pk=progress_pk,
        user=request.user
    )

    current_scene = progress.current_scene
    choices = current_scene.choices.all()

    # Проверяем, финальная ли это сцена
    is_final = current_scene.is_ending_scene

    # Если квест завершён
    if is_final and not progress.is_completed:
        progress.is_completed = True
        progress.save()

    context = {
        'progress': progress,
        'quest': progress.quest,
        'scene': current_scene,
        'choices': choices,
        'is_final': is_final,
    }

    return render(request, 'gameplay/play.html', context)


@login_required
def quest_choice_view(request, progress_pk, choice_pk):
    """Обработка выбора игрока"""
    progress = get_object_or_404(
        UserProgress,
        pk=progress_pk,
        user=request.user
    )

    choice = get_object_or_404(Choice, pk=choice_pk)

    # Проверяем, что выбор принадлежит текущей сцене
    if choice.scene != progress.current_scene:
        messages.error(request, 'Недопустимый выбор!')
        return redirect('gameplay:play', progress_pk=progress.pk)

    # Проверяем, есть ли следующая сцена
    if not choice.next_scene:
        messages.error(request, 'Этот выбор не ведёт дальше. Автор квеста ещё не настроил переход!')
        return redirect('gameplay:play', progress_pk=progress.pk)

    # Переходим к следующей сцене
    progress.current_scene = choice.next_scene
    progress.save()

    return redirect('gameplay:play', progress_pk=progress.pk)


@login_required
def quest_restart_view(request, progress_pk):
    """Начать квест заново"""
    progress = get_object_or_404(
        UserProgress,
        pk=progress_pk,
        user=request.user
    )

    # Находим начальную сцену
    starting_scene = progress.quest.scenes.filter(is_starting_scene=True).first()

    if not starting_scene:
        messages.error(request, 'Не удалось перезапустить квест!')
        return redirect('quests:detail', pk=progress.quest.pk)

    # Сбрасываем прогресс
    progress.current_scene = starting_scene
    progress.is_completed = False
    progress.save()

    # Очищаем инвентарь
    progress.inventory.all().delete()

    messages.success(request, 'Квест перезапущен!')
    return redirect('gameplay:play', progress_pk=progress.pk)


@login_required
def quest_abandon_view(request, progress_pk):
    """Покинуть квест"""
    progress = get_object_or_404(
        UserProgress,
        pk=progress_pk,
        user=request.user
    )

    quest_title = progress.quest.title
    quest_pk = progress.quest.pk

    # Удаляем прогресс
    progress.delete()

    messages.info(request, f'Вы покинули квест "{quest_title}"')
    return redirect('quests:detail', pk=quest_pk)


@login_required
def rate_quest_view(request, quest_pk):
    """Оценка квеста"""
    from gameplay.models import QuestRating

    if request.method == 'POST':
        quest = get_object_or_404(Quest, pk=quest_pk)

        # Проверяем, не автор ли пытается оценить
        if quest.author == request.user:
            messages.error(request, 'Вы не можете оценить свой собственный квест!')
            return redirect('quests:detail', pk=quest_pk)

        rating_value = request.POST.get('rating')
        review_text = request.POST.get('review', '')

        if not rating_value:
            messages.error(request, 'Выберите оценку!')
            return redirect('quests:detail', pk=quest_pk)

        # Создаём или обновляем оценку
        rating, created = QuestRating.objects.update_or_create(
            user=request.user,
            quest=quest,
            defaults={
                'rating': int(rating_value),
                'review': review_text
            }
        )

        # Пересчитываем средний рейтинг
        from django.db.models import Avg
        avg_rating = quest.ratings.aggregate(Avg('rating'))['rating__avg']
        quest.rating = avg_rating or 0
        quest.save()

        if created:
            messages.success(request, 'Спасибо за оценку!')
        else:
            messages.success(request, 'Ваша оценка обновлена!')

        return redirect('quests:detail', pk=quest_pk)

    return redirect('quests:detail', pk=quest_pk)