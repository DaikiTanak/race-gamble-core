from race_gamble_core.schemas.order import BaseOrder
from enum import StrEnum


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


class TestBaseOrder:
    def test_keisyou(self):
        o = ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan)
        assert str(o) == "1-2"

    def test_eq(self):
        assert ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan) == ExampleOrder(
            first_course=1, second_course=2, bet_type=ExampleBetType.nirentan
        )
        assert ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan) != ExampleOrder(
            first_course=6, second_course=2, bet_type=ExampleBetType.nirentan
        )
        assert ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan) != ExampleOrder(
            first_course=1, second_course=2, bet_type=ExampleBetType.sanrentan
        )

    def test_lt(self):
        assert ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan) < ExampleOrder(
            first_course=1, second_course=3, bet_type=ExampleBetType.nirentan
        )
        assert ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan) < ExampleOrder(
            first_course=2, second_course=1, bet_type=ExampleBetType.nirentan
        )
