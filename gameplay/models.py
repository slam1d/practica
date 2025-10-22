from django.db import models
from django.conf import settings
from quests.models import Quest, Scene, Item


class UserProgress(models.Model):
    """Прогресс пользователя в квесте"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    current_scene = models.ForeignKey(Scene, on_delete=models.CASCADE)

    started_at = models.DateTimeField(auto_now_add=True)
    last_played = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Прогресс"
        verbose_name_plural = "Прогресс пользователей"
        unique_together = ['user', 'quest']

    def __str__(self):
        return f"{self.user.username} - {self.quest.title}"


class UserInventory(models.Model):
    """Инвентарь пользователя для конкретного квеста"""
    progress = models.ForeignKey(UserProgress, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    acquired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Инвентарь"
        verbose_name_plural = "Инвентарь пользователей"


class QuestRating(models.Model):
    """Оценка квеста пользователем"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 звёзд
    review = models.TextField(blank=True, verbose_name="Отзыв")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        unique_together = ['user', 'quest']

    def __str__(self):
        return f"{self.user.username} - {self.quest.title}: {self.rating}★"