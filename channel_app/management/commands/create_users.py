from getpass import getpass

from django.core.management import BaseCommand
from django.contrib.auth.models import User
import random

names = ['keth', 'Josh', 'owen', "Adam", 'Alice']


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--count')

    def handle(self, *args, **options):
        count = options['count']
        password = getpass('Enter the default password: ')
        for _ in range(int(count)):
            name = random.choice(names)
            if User.objects.filter(username=name).exists():
                name += str(random.randint(1, 10))
            user = User.objects.create(username=name, email=name + '@gmail.com')
            user.set_password(password)
            user.save()
            print(f'User -> {name} created successfully')
        print(f'-------created {count} new users success------------')
