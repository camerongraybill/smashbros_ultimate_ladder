from dataclasses import dataclass

from django.apps import AppConfig


@dataclass(frozen=True)
class RatingServiceConfig:
    default_rating: float
    k_factor: float


class SmashLadderConfig(AppConfig):
    name = 'smash_ladder'
    rating_config = RatingServiceConfig(
        default_rating=1200.0,
        k_factor=30.0
    )
