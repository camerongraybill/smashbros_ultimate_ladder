from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, URLField, ForeignKey, CASCADE, DateTimeField, OneToOneField, ImageField


class School(Model):
    mascot = CharField(max_length=100)
    name = CharField(max_length=100)
    location = ImageField(null=True, upload_to="static/data/school_photos/")
    photo = URLField()

    def __str__(self):
        return self.name


class Profile(Model):
    school = ForeignKey(School, on_delete=CASCADE, null=True)
    profile_picture = ImageField(null=True, upload_to="static/data/profile_pictures/")
    user = OneToOneField(
        settings.AUTH_USER_MODEL,
        CASCADE
    )

    def __str__(self):
        return self.user.username


class Character(Model):
    name = CharField(max_length=100)
    photo = ImageField(upload_to="static/data/character_photos/")

    def __str__(self):
        return self.name


class Game(Model):
    player_one = ForeignKey(Profile, on_delete=CASCADE, related_name='+')
    player_two = ForeignKey(Profile, on_delete=CASCADE, related_name='+')
    player_one_char = ForeignKey(Character, on_delete=CASCADE, related_name='+')
    player_two_char = ForeignKey(Character, on_delete=CASCADE, related_name='+')
    winner = ForeignKey(Profile, on_delete=CASCADE, related_name='+')


class Set(Model):
    game_one = ForeignKey(Game, on_delete=CASCADE, related_name='+')
    game_two = ForeignKey(Game, on_delete=CASCADE, related_name='+')
    game_three = ForeignKey(Game, on_delete=CASCADE, related_name='+', null=True)
    happened_at = DateTimeField()
