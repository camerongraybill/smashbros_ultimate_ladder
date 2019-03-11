from collections import Counter, OrderedDict, defaultdict
from itertools import chain
from typing import Set as Set_T, Dict, DefaultDict, List, Optional, Tuple
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
    description = CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

    def matches(self) -> List["Set"]:
        all_sets = set(x[0] for x in (chain.from_iterable(x.sets for x in self.players.all())))
        return list(sorted(all_sets, key=lambda x: x.happened_at, reverse=True))


class Character(Model):
    name = CharField(max_length=100)
    photo = ImageField(upload_to="static/data/character_photos/", default="static/data/character_photos/default.png")
    description = CharField(max_length=256, default="")

    def __str__(self):
        return self.name

    @property
    def games(self) -> List["Game"]:
        return sorted(set(list(self.where_winner.all()) + list(self.where_loser.all())),
                      key=lambda x: x.set.happened_at, reverse=True)

    @property
    def most_active_user(self) -> Optional["Profile"]:
        c = Counter([x.winner for x in self.where_winner.all()] + [x.loser for x in self.where_loser.all()])
        if len(c) == 0:
            return None
        return c.most_common(1)[0][0]


class Profile(Model):
    school = ForeignKey(School, on_delete=CASCADE, null=True, related_name='players')
    profile_picture = ImageField(null=True, upload_to="static/data/profile_pictures/",
                                 default="static/data/profile_pictures/default.png")
    first_name = CharField(null=True, max_length=30, default="")
    last_name = CharField(null=True, max_length=30, default="")

    user: "User" = OneToOneField(
        settings.AUTH_USER_MODEL,
        CASCADE
    )

    def __str__(self):
        return self.display_name

    @property
    def games(self) -> "List[Game]":
        return list(self.wins.all()) + list(self.losses.all())

    @property
    def sets(self) -> "List[Tuple[Set, float]]":
        from smash_ladder import services
        all_sets = {x.set for x in self.games}
        ordered = sorted(all_sets, key=lambda x: x.happened_at, reverse=True)

        return list((x, services.RatingService.get_set_impact(x)[self]) for x in ordered)

    @property
    def rating(self) -> float:
        from smash_ladder.services import RatingService
        return RatingService.get_rating_for(self)

    @property
    def ranking(self) -> float:
        from smash_ladder.services import RatingService
        return RatingService.get_ranking_for(self)

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

    @property
    def display_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.user.username})"
        elif self.first_name:
            return f"{self.first_name} ({self.user.username})"
        elif self.last_name:
            return f"{self.last_name} ({self.user.username})"
        return self.user.username


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

    @property
    def winner_rating_change(self):
        from smash_ladder.services import RatingService
        return RatingService.get_set_impact(self)[self.winner]

    @property
    def loser_rating_change(self):
        from smash_ladder.services import RatingService
        return RatingService.get_set_impact(self)[self.loser]


class Game(Model):
    set = ForeignKey(Set, on_delete=CASCADE, related_name='games')
    winner = ForeignKey(Profile, on_delete=CASCADE, related_name='wins')
    loser = ForeignKey(Profile, on_delete=CASCADE, related_name='losses')
    winner_char = ForeignKey(Character, on_delete=CASCADE, related_name='where_winner')
    loser_char = ForeignKey(Character, on_delete=CASCADE, related_name='where_loser')

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
