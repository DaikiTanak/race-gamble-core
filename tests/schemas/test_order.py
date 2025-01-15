from race_gamble_core import Order, BetType
import pytest


class TestBaseOrder:
    def test_keisyou(self):
        o = Order(first_course=1, second_course=2, bet_type=BetType.nirentan)
        assert str(o) == "1-2"

    def test_eq(self):
        assert Order(first_course=1, second_course=2, bet_type=BetType.nirentan) == Order(
            first_course=1, second_course=2, bet_type=BetType.nirentan
        )
        assert Order(first_course=1, second_course=2, bet_type=BetType.nirentan) != Order(
            first_course=6, second_course=2, bet_type=BetType.nirentan
        )
        assert Order(first_course=1, second_course=2, bet_type=BetType.nirentan) != Order(
            first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrentan
        )

    def test_lt(self):
        assert Order(first_course=1, second_course=2, bet_type=BetType.nirentan) < Order(
            first_course=1, second_course=3, bet_type=BetType.nirentan
        )
        assert Order(first_course=1, second_course=2, bet_type=BetType.nirentan) < Order(
            first_course=2, second_course=1, bet_type=BetType.nirentan
        )

    def test_format_order(self):
        o = Order(first_course=1, second_course=2, bet_type=BetType.nirentan)
        assert o._format_order() == "1-2"

        o = Order(first_course=6, second_course=1, bet_type=BetType.nirenpuku)
        assert o._format_order() == "1-6"

        o = Order(first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrentan)
        assert o._format_order() == "1-2-3"

        o = Order(first_course=6, second_course=4, third_course=3, bet_type=BetType.sanrenpuku)
        assert o._format_order() == "3-4-6"

    def test_get_courses(self):
        o = Order(first_course=1, second_course=2, bet_type=BetType.nirentan)
        assert o.get_first_course() == 1
        assert o.get_second_course() == 2
        with pytest.raises(Exception):
            o.get_third_course()

        o = Order(first_course=6, second_course=1, bet_type=BetType.nirenpuku)
        assert o.get_first_course() == 1
        assert o.get_second_course() == 6
        with pytest.raises(Exception):
            o.get_third_course()

        o = Order(first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrentan)
        assert o.get_first_course() == 1
        assert o.get_second_course() == 2
        assert o.get_third_course() == 3

        o = Order(first_course=6, second_course=4, third_course=3, bet_type=BetType.sanrenpuku)
        assert o.get_first_course() == 3
        assert o.get_second_course() == 4
        assert o.get_third_course() == 6
