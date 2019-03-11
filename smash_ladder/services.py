from typing import Iterable, Tuple, Dict, NewType, cast, TYPE_CHECKING

import smash_ladder
from .apps import RatingServiceConfig
from .apps import SmashLadderConfig

if TYPE_CHECKING:
    from .models import Set, Profile

RatingChange = NewType('RatingChange', float)

Rating = NewType('Rating', float)


class SetImpact(Dict["Profile", RatingChange]):
    def __missing__(self, key: "Profile"):
        return 0


class ImpactStorage(Dict["Set", SetImpact]):
    def __missing__(self, key: "Set"):
        self[key] = SetImpact()
        return self[key]


class _RatingService:
    def __init__(self, config: RatingServiceConfig):
        self._set_impacts = ImpactStorage()
        self.config = config
        self._build_ratings()

    def _build_ratings(self):
        for match in smash_ladder.models.Set.objects.order_by("happened_at"):
            self.add_set(match)

    def invalidate(self):
        self._set_impacts.clear()
        self._build_ratings()

    def get_set_impact(self, event: "Set") -> SetImpact:
        return self._set_impacts[event]

    def add_set(self, event: "Set") -> SetImpact:
        impact = self.get_set_impact(event)
        p1, p2 = event.winner, event.loser
        p1_before, p2_before = self.get_rating_for(p1), self.get_rating_for(p2)
        p1_expected = p1_before / (p1_before + p2_before)
        p2_expected = 1 - p1_expected
        win_counts = event.win_counts
        amount_played = len(event.games.all())
        p1_actual, p2_actual = win_counts[p1] / amount_played, win_counts[p2] / amount_played
        impact[p1], impact[p2] = self.config.k_factor * (p1_actual - p1_expected), \
                                 self.config.k_factor * (p2_actual - p2_expected)
        return impact

    def get_rating_for(self, user: "Profile") -> Rating:
        return cast(Rating,
                    self.config.default_rating + sum(x[user] for x in self._set_impacts.values()))

    def get_ranking_for(self, user: "Profile"):
        all_ratings = list(self.get_ratings(smash_ladder.models.Profile.objects.all()))
        sorted_ratings = sorted(all_ratings, key=lambda x: x[1], reverse=True)
        just_players = list(x[0] for x in sorted_ratings)
        return just_players.index(user) + 1

    def get_ratings(self, users: Iterable["Profile"]) -> Iterable[
        Tuple["Profile", Rating]]:
        for user in users:
            yield user, self.get_rating_for(user)


RatingService = _RatingService(SmashLadderConfig.rating_config)
