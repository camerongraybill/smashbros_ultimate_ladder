from typing import Iterable, Tuple, Dict, NewType, cast

import smash_ladder
from .apps import RatingServiceConfig
from .apps import SmashLadderConfig

SetId = NewType('SetId', int)

RatingChange = NewType('RatingChange', float)

Rating = NewType('Rating', float)


class SetImpact(Dict[smash_ladder.models.Profile, RatingChange]):
    def __missing__(self, key: smash_ladder.models.Profile):
        return 0


class ImpactStorage(Dict[SetId, SetImpact]):
    def __missing__(self, key: SetId):
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

    def get_set_impact(self, event_id: SetId) -> SetImpact:
        return self._set_impacts[event_id]

    def add_set(self, event: smash_ladder.models.Set) -> SetImpact:
        impact = self.get_set_impact(cast(SetId, event.id))
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

    def get_rating_for(self, user: smash_ladder.models.Profile) -> Rating:
        return cast(Rating,
                    self.config.default_rating + sum(x[user] for x in self._set_impacts.values()))

    def get_ratings(self, users: Iterable[smash_ladder.models.Profile]) -> Iterable[
        Tuple[smash_ladder.models.Profile, Rating]]:
        for user in users:
            yield user, self.get_rating_for(user)


RatingService = _RatingService(SmashLadderConfig.rating_config)
