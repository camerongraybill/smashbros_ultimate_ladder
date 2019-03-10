from collections import Counter
from typing import Counter as Counter_T, Set as Set_T
from itertools import chain

from django.conf import settings
from django.db.models import Model, CharField, ForeignKey, CASCADE, DateTimeField, OneToOneField, ImageField
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from django.contrib.auth.models import User


class School(Model):
    mascot = CharField(max_length=100)
    name = CharField(max_length=100)
    location = CharField(max_length=100)
    photo = ImageField(null=True, upload_to="static/data/school_photos/")

    def __str__(self):
        return self.name


class Profile(Model):
    school = ForeignKey(School, on_delete=CASCADE, null=True)
    profile_picture = ImageField(null=True, upload_to="static/data/profile_pictures/")
    user: "User" = OneToOneField(
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


class Set(Model):
    happened_at = DateTimeField()

    @property
    def players(self) -> Set_T[Profile]:
        return {*chain.from_iterable(x.players for x in self.games.all())}

    @property
    def win_counts(self) -> Counter_T[Profile]:
        return Counter(x.winner for x in self.games.all())

    @property
    def winner(self) -> Profile:
        return self.win_counts.most_common(1)[0][0]

    @property
    def loser(self) -> Profile:
        return self.win_counts.most_common(2)[1][0]


class Game(Model):
    set = ForeignKey(Set, on_delete=CASCADE, related_name='games')
    winner = ForeignKey(Profile, on_delete=CASCADE, related_name='wins')
    loser = ForeignKey(Profile, on_delete=CASCADE, related_name='losses')
    winner_char = ForeignKey(Character, on_delete=CASCADE, related_name='+')
    loser_char = ForeignKey(Character, on_delete=CASCADE, related_name='+')

    @property
    def players(self) -> Set_T[Profile]:
        return {*(self.winner, self.loser)}
