from race_gamble_core.schemas.order import BaseOrder
from enum import StrEnum


class ExampleBetType(StrEnum):
    nirentan = "二連単"


class ExampleOrder(BaseOrder, frozen=True):

    bet_type: ExampleBetType

    def _validate_courses(self):
        pass

    def _format_order(self):
        pass


class TestBaseOrder:
    def test_keisyou(self):
        _ = ExampleOrder(first_course=1, second_course=2, bet_type=ExampleBetType.nirentan)
