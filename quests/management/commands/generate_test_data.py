from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quests.models import Quest, Scene, Choice, Tag
from gameplay.models import UserProgress

User = get_user_model()


class Command(BaseCommand):
    help = 'Генерирует тестовые данные для LoreLoom'

    def handle(self, *args, **kwargs):
        self.stdout.write('Создание тестовых данных...')

        # Создание тестовых пользователей
        if not User.objects.filter(username='author1').exists():
            author1 = User.objects.create_user(
                username='author1',
                email='author1@example.com',
                password='password123'
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан пользователь author1'))
        else:
            author1 = User.objects.get(username='author1')

        # Создание тегов
        tags_data = [
            ('Детектив', 'detective'),
            ('Фэнтези', 'fantasy'),
            ('Хоррор', 'horror'),
            ('Приключения', 'adventure'),
            ('Научная фантастика', 'scifi'),
        ]

        tags = []
        for name, slug in tags_data:
            tag, created = Tag.objects.get_or_create(name=name, slug=slug)
            tags.append(tag)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Создан тег {name}'))

        # Создание квестов
        quests_data = [
            {
                'title': 'Тайна отеля "Гранд"',
                'description': 'Детективный квест о загадочном убийстве в роскошном отеле. Вы - частный детектив, который должен разгадать тайну, опросив подозреваемых и собрав улики.',
                'difficulty': 'medium',
                'estimated_time': 45,
                'tags': [tags[0], tags[3]],  # Детектив, Приключения
            },
            {
                'title': 'Проклятие древнего леса',
                'description': 'Вы заблудились в мистическом лесу, где обитают странные существа. Найдите выход, разгадав загадки древних духов.',
                'difficulty': 'hard',
                'estimated_time': 60,
                'tags': [tags[1], tags[2]],  # Фэнтези, Хоррор
            },
            {
                'title': 'Космическая станция "Надежда"',
                'description': 'На орбитальной станции произошла авария. Вы - последний выживший член экипажа. Сможете ли вы вернуться на Землю?',
                'difficulty': 'easy',
                'estimated_time': 30,
                'tags': [tags[4]],  # Научная фантастика
            },
        ]

        for quest_data in quests_data:
            quest_tags = quest_data.pop('tags')
            quest, created = Quest.objects.get_or_create(
                title=quest_data['title'],
                defaults={
                    **quest_data,
                    'author': author1,
                    'is_published': True,
                    'play_count': 15,
                    'rating': 4.5,
                }
            )
            if created:
                quest.tags.set(quest_tags)
                self.create_quest_scenes(quest)
                self.stdout.write(self.style.SUCCESS(f'✓ Создан квест "{quest.title}"'))

        self.stdout.write(self.style.SUCCESS('\n✅ Все тестовые данные созданы!'))
        self.stdout.write('Используйте: username=author1, password=password123')

    def create_quest_scenes(self, quest):
        """Создает базовую структуру сцен для квеста"""
        # Начальная сцена
        scene1 = Scene.objects.create(
            quest=quest,
            title='Начало',
            content='Вы стоите у входа. Что будете делать?',
            order=1,
            is_starting_scene=True
        )

        # Вторая сцена
        scene2 = Scene.objects.create(
            quest=quest,
            title='Исследование',
            content='Вы начинаете исследовать местность...',
            order=2
        )

        # Финальная сцена
        scene3 = Scene.objects.create(
            quest=quest,
            title='Финал',
            content='Вы разгадали все загадки! Поздравляем!',
            order=3,
            is_ending_scene=True
        )

        # Создание выборов
        Choice.objects.create(
            scene=scene1,
            text='Войти внутрь',
            next_scene=scene2,
            order=1
        )

        Choice.objects.create(
            scene=scene2,
            text='Продолжить расследование',
            next_scene=scene3,
            order=1
        )