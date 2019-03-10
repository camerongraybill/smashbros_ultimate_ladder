from dataclasses import dataclass

from django.apps import AppConfig


@dataclass(frozen=True)
class RatingServiceConfig:
    default_rating: int
    k_factor: int


class SmashLadderConfig(AppConfig):
    name = 'smash_ladder'
    rating_config = RatingServiceConfig(
        default_rating=1200,
        k_factor=30
    )
