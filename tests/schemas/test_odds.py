from race_gamble_core import Odds, Order, BetType
import pytest


class TestOdds:
    def test_construct(self):
        _ = Odds(order=Order(first_course=1, second_course=2, bet_type=BetType.nirentan), odds=1.4)

    def test_invalid_odds(self):
        with pytest.raises(ValueError):
            _ = Odds(order=Order(first_course=1, second_course=2, bet_type=BetType.nirentan), odds=-1)

    def test_odds_to_prob(self):
        assert (
            Odds(order=Order(first_course=1, second_course=2, bet_type=BetType.nirentan), odds=1.5).odds_to_prob()
            == 0.5
        )

    def test_get_expected_roi(self):
        assert (
            Odds(order=Order(first_course=1, second_course=2, bet_type=BetType.nirentan), odds=1.5).get_expected_roi(
                estimated_prob=0.5
            )
            == -0.25
        )
