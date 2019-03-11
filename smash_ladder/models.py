from collections import Counter, OrderedDict, defaultdict
from itertools import chain
from typing import Set as Set_T, Dict, DefaultDict, List, Optional
from typing import TYPE_CHECKING

from django.conf import settings
from django.db.models import Model, CharField, ForeignKey, CASCADE, DateTimeField, OneToOneField, ImageField

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class School(Model):
    mascot = CharField(max_length=100)
    name = CharField(max_length=100)
    location = CharField(max_length=100)
    photo = ImageField(null=True, upload_to="static/data/school_photos/")

    def __str__(self):
        return self.name


class Character(Model):
    name = CharField(max_length=100)
    photo = ImageField(upload_to="static/data/character_photos/")

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

    @property
    def games(self) -> "List[Game]":
        return list(self.wins.all()) + list(self.losses.all())

    @property
    def rating(self) -> float:
        from smash_ladder.services import RatingService
        return RatingService.get_rating_for(self)

    @property
    def get_played_stats(self) -> DefaultDict[Character, int]:
        fake_counter = defaultdict(int)
        for game in self.games:
            fake_counter[game.get_played_as(self)] += 1
        return fake_counter

    @property
    def favorite_character(self) -> Optional[Character]:
        c = Counter(self.get_played_stats)
        if len(c) == 0:
            return None
        return c.most_common(1)[0][0]

    @property
    def win_rate(self) -> Optional[float]:
        if len(self.games) == 0:
            return None
        return self.wins.count() / len(self.games)


class Set(Model):
    happened_at = DateTimeField()

    @property
    def players(self) -> Set_T[Profile]:
        return {*chain.from_iterable(x.players for x in self.games.all())}

    @property
    def win_counts(self) -> Dict[Profile, int]:
        counter = Counter(x.winner for x in self.games.all())
        if len(counter) == 0:
            return OrderedDict()
        d = dict(counter)
        for player in self.players:
            if player not in d:
                d[player] = 0
        return d

    @property
    def winner(self) -> Profile:
        curr_max, player = -1, None
        for iter_player, wins in self.win_counts.items():
            if wins > curr_max:
                curr_max = wins
                player = iter_player
        return player

    @property
    def loser(self) -> Profile:
        curr_min, player = float('inf'), None
        for iter_player, wins in self.win_counts.items():
            if wins < curr_min:
                curr_min = wins
                player = iter_player
        return player


class Game(Model):
    set = ForeignKey(Set, on_delete=CASCADE, related_name='games')
    winner = ForeignKey(Profile, on_delete=CASCADE, related_name='wins')
    loser = ForeignKey(Profile, on_delete=CASCADE, related_name='losses')
    winner_char = ForeignKey(Character, on_delete=CASCADE, related_name='+')
    loser_char = ForeignKey(Character, on_delete=CASCADE, related_name='+')

    @property
    def players(self) -> Set_T[Profile]:
        return {*(self.winner, self.loser)}

    def get_played_as(self, user: Profile) -> Character:
        if user == self.winner:
            return self.winner_char
        elif user == self.loser:
            return self.loser_char
        else:
            raise KeyError()
