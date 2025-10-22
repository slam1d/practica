from django.db import models
from django.conf import settings


class Tag(models.Model):
    """Теги для категоризации квестов"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Quest(models.Model):
    """Основная модель квеста"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Лёгкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quests',
        verbose_name="Автор"
    )
    cover_image = models.ImageField(upload_to='quest_covers/', blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    estimated_time = models.IntegerField(help_text="Время прохождения в минутах", default=30)

    tags = models.ManyToManyField(Tag, related_name='quests', blank=True)

    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Статистика
    play_count = models.IntegerField(default=0, verbose_name="Количество прохождений")
    rating = models.FloatField(default=0.0, verbose_name="Рейтинг")

    class Meta:
        verbose_name = "Квест"
        verbose_name_plural = "Квесты"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Scene(models.Model):
    """Сцена квеста"""
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='scenes')
    title = models.CharField(max_length=200, verbose_name="Название сцены")
    content = models.TextField(verbose_name="Текст сцены")
    order = models.IntegerField(default=0, verbose_name="Порядковый номер")

    is_starting_scene = models.BooleanField(default=False, verbose_name="Начальная сцена")
    is_ending_scene = models.BooleanField(default=False, verbose_name="Финальная сцена")

    background_image = models.ImageField(upload_to='scene_backgrounds/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сцена"
        verbose_name_plural = "Сцены"
        ordering = ['order']

    def __str__(self):
        return f"{self.quest.title} - {self.title}"


class Choice(models.Model):
    """Выбор игрока в сцене"""
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300, verbose_name="Текст выбора")
    next_scene = models.ForeignKey(
        Scene,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_choices',
        verbose_name="Следующая сцена"
    )
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Выбор"
        verbose_name_plural = "Выборы"
        ordering = ['order']

    def __str__(self):
        return self.text


class Item(models.Model):
    """Предметы в квесте"""
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100, verbose_name="Название предмета")
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='item_icons/', blank=True, null=True)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return self.name