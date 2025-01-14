from race_gamble_core.schemas.odds import Odds
from race_gamble_core.schemas.order import BaseOrder
from enum import StrEnum
import pytest


class ExampleBetType(StrEnum):
    nirentan = "nirentan"
    sanrentan = "sanrentan"


class ExampleOrder(BaseOrder, frozen=True):

    bet_type: ExampleBetType

    def _validate_courses(self):
        pass

    def _format_order(self):
        if self.bet_type == ExampleBetType.nirentan:
            return f"{self.first_course}-{self.second_course}"
        elif self.bet_type == ExampleBetType.sanrentan:
            return f"{self.first_course}-{self.second_course}-{self.third_course}"
        else:
            raise ValueError


class TestOdds:
    def test_construct(self):
        _ = Odds(order=ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan), odds=1.4)

    def test_invalid_odds(self):
        with pytest.raises(ValueError):
            _ = Odds(order=ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan), odds=-1)

    def test_odds_to_prob(self):
        assert (
            Odds(
                order=ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan), odds=1.5
            ).odds_to_prob()
            == 0.5
        )

    def test_get_expected_roi(self):
        assert (
            Odds(
                order=ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan), odds=1.5
            ).get_expected_roi(estimated_prob=0.5)
            == -0.25
        )
