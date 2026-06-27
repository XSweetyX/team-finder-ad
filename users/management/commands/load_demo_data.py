from django.core.management.base import BaseCommand

from users.models import User
from projects.models import Project


class Command(BaseCommand):
    help = 'Наполняет базу данных тестовыми пользователями и проектами'

    def handle(self, *args, **options):
        self.stdout.write('Cоздание демо-данных...')

  
        users_data = [
            {'email': 'ivan@test.com', 'name': 'Иван', 'surname': 'Иванов', 'about': 'Frontend-разработчик'},
            {'email': 'sergey@test.com', 'name': 'Сергей', 'surname': 'Тихонов', 'about': 'Python Backend Developer'},
            {'email': 'denis@test.com', 'name': 'Денис', 'surname': 'Ильин', 'about': 'DevOps инженер'},
        ]

        created_users = []
        for data in users_data:
            user, created = User.objects.get_or_create(email=data['email'], defaults={
                'name': data['name'],
                'surname': data['surname'],
                'about': data['about'],
                'password': 'pbkdf2_sha256$...' 
            })
            if created:
                user.set_password('test123')
                user.save()
            created_users.append(user)
            self.stdout.write(f'Пользователь {user.name} готов.')

    
        projects_data = [
            {'name': 'Астрономическое приложение', 'desc': 'Карта звёздного неба', 'owner_idx': 0},
            {'name': 'ML Учебник', 'desc': 'База знаний ML', 'owner_idx': 1},
            {'name': 'Libs Tools', 'desc': 'Динамические библиотеки', 'owner_idx': 2},
            {'name': 'TeamFinder v2', 'desc': 'Редизайн платформы', 'owner_idx': 0},
            {'name': 'Chatbot', 'desc': 'Чат-бот ', 'owner_idx': 1},
        ]

        for p_data in projects_data:
            owner = created_users[p_data['owner_idx']]
            proj, created = Project.objects.get_or_create(name=p_data['name'], defaults={
                'description': p_data['desc'],
                'owner': owner,
                'status': Project.STATUS_OPEN
            })
            if created:
                proj.participants.add(owner)
            self.stdout.write(f'Проект "{proj.name}" готов.')

        self.stdout.write(self.style.SUCCESS('Успешно создано 3 пользователя и 5 проектов!'))
        self.stdout.write('Пароль для всех тестовых аккаунтов: test123')
