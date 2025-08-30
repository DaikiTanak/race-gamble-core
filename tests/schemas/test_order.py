import pytest

from race_gamble_core import BetType, Order


class TestBaseOrder:
    def test_keisyou(self):
        o = Order(first_course=1, second_course=2, bet_type=BetType.nirentan)
        assert str(o) == "1-2"

    def test_eq(self):
        assert Order(
            first_course=1, second_course=2, bet_type=BetType.nirentan
        ) == Order(first_course=1, second_course=2, bet_type=BetType.nirentan)
        assert Order(
            first_course=1, second_course=2, bet_type=BetType.nirentan
        ) != Order(first_course=6, second_course=2, bet_type=BetType.nirentan)
        assert Order(
            first_course=1, second_course=2, bet_type=BetType.nirentan
        ) != Order(
            first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrentan
        )

    def test_lt(self):
        assert Order(
            first_course=1, second_course=2, bet_type=BetType.nirentan
        ) < Order(first_course=1, second_course=3, bet_type=BetType.nirentan)
        assert Order(
            first_course=1, second_course=2, bet_type=BetType.nirentan
        ) < Order(first_course=2, second_course=1, bet_type=BetType.nirentan)

    def test_format_order(self):
        o = Order(first_course=1, second_course=2, bet_type=BetType.nirentan)
        assert o._format_order() == "1-2"

        o = Order(first_course=6, second_course=1, bet_type=BetType.nirenpuku)
        assert o._format_order() == "1-6"

        o = Order(
            first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrentan
        )
        assert o._format_order() == "1-2-3"

        o = Order(
            first_course=6, second_course=4, third_course=3, bet_type=BetType.sanrenpuku
        )
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

        o = Order(
            first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrentan
        )
        assert o.get_first_course() == 1
        assert o.get_second_course() == 2
        assert o.get_third_course() == 3

        o = Order(
            first_course=6, second_course=4, third_course=3, bet_type=BetType.sanrenpuku
        )
        assert o.get_first_course() == 3
        assert o.get_second_course() == 4
        assert o.get_third_course() == 6

    def test_create_rentan_orders_from_renpuku(self):
        orders = Order.create_rentan_orders_from_renpuku("2-3")
        assert len(orders) == 2
        assert orders[0] == Order(
            first_course=2, second_course=3, bet_type=BetType.nirentan
        )
        assert orders[1] == Order(
            first_course=3, second_course=2, bet_type=BetType.nirentan
        )

        orders = Order.create_rentan_orders_from_renpuku("1-2-3")
        assert len(orders) == 6
        assert orders[0] == Order(
            first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrentan
        )
        assert orders[1] == Order(
            first_course=1, second_course=3, third_course=2, bet_type=BetType.sanrentan
        )
        assert orders[2] == Order(
            first_course=2, second_course=1, third_course=3, bet_type=BetType.sanrentan
        )
        assert orders[3] == Order(
            first_course=2, second_course=3, third_course=1, bet_type=BetType.sanrentan
        )
        assert orders[4] == Order(
            first_course=3, second_course=1, third_course=2, bet_type=BetType.sanrentan
        )
        assert orders[5] == Order(
            first_course=3, second_course=2, third_course=1, bet_type=BetType.sanrentan
        )

    def test_to_order_idx(self):
        # 単勝
        o = Order(first_course=1, bet_type=BetType.tansyou)
        assert o.to_order_idx() == 0

        o = Order(first_course=6, bet_type=BetType.tansyou)
        assert o.to_order_idx() == 5

        # 2連単
        o = Order(first_course=1, second_course=2, bet_type=BetType.nirentan)
        assert o.to_order_idx() == 0

        o = Order(first_course=2, second_course=1, bet_type=BetType.nirentan)
        assert o.to_order_idx() == 5

        # 2連複
        o = Order(first_course=1, second_course=2, bet_type=BetType.nirenpuku)
        assert o.to_order_idx() == 0

        o = Order(first_course=3, second_course=2, bet_type=BetType.nirenpuku)
        assert o.to_order_idx() == 5

        # 3連単
        o = Order(
            first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrentan
        )
        assert o.to_order_idx() == 0

        o = Order(
            first_course=6, second_course=5, third_course=4, bet_type=BetType.sanrentan
        )
        assert o.to_order_idx() == 119

        # 3連複
        o = Order(
            first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrenpuku
        )
        assert o.to_order_idx() == 0

        o = Order(
            first_course=6, second_course=5, third_course=4, bet_type=BetType.sanrenpuku
        )
        assert o.to_order_idx() == 19

    def test_idx_to_order(self):
        # 単勝
        o = Order.idx_to_order(0, num_racers=6, bet_type=BetType.tansyou)
        assert o == Order(first_course=1, bet_type=BetType.tansyou)

        o = Order.idx_to_order(5, num_racers=6, bet_type=BetType.tansyou)
        assert o == Order(first_course=6, bet_type=BetType.tansyou)

        with pytest.raises(ValueError):
            Order.idx_to_order(6, num_racers=6, bet_type=BetType.tansyou)

        # 2連単
        o = Order.idx_to_order(0, num_racers=6, bet_type=BetType.nirentan)
        assert o == Order(first_course=1, second_course=2, bet_type=BetType.nirentan)

        o = Order.idx_to_order(5, num_racers=6, bet_type=BetType.nirentan)
        assert o == Order(first_course=2, second_course=1, bet_type=BetType.nirentan)

        o = Order.idx_to_order(29, num_racers=6, bet_type=BetType.nirentan)
        assert o == Order(first_course=6, second_course=5, bet_type=BetType.nirentan)

        with pytest.raises(ValueError):
            Order.idx_to_order(30, num_racers=6, bet_type=BetType.nirentan)

        # 2連複
        o = Order.idx_to_order(0, num_racers=6, bet_type=BetType.nirenpuku)
        assert o == Order(first_course=1, second_course=2, bet_type=BetType.nirenpuku)

        o = Order.idx_to_order(5, num_racers=6, bet_type=BetType.nirenpuku)
        assert o == Order(first_course=3, second_course=2, bet_type=BetType.nirenpuku)

        o = Order.idx_to_order(14, num_racers=6, bet_type=BetType.nirenpuku)
        assert o == Order(first_course=5, second_course=6, bet_type=BetType.nirenpuku)

        with pytest.raises(ValueError):
            Order.idx_to_order(15, num_racers=6, bet_type=BetType.nirenpuku)

        # 3連単
        o = Order.idx_to_order(0, num_racers=6, bet_type=BetType.sanrentan)
        assert o == Order(
            first_course=1, second_course=2, third_course=3, bet_type=BetType.sanrentan
        )

        o = Order.idx_to_order(119, num_racers=6, bet_type=BetType.sanrentan)
        assert o == Order(
            first_course=6, second_course=5, third_course=4, bet_type=BetType.sanrentan
        )
