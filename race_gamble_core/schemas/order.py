import itertools
from functools import lru_cache
from typing import Self

from pydantic import BaseModel, field_validator, model_serializer, model_validator

from .bet_type import BetType


@lru_cache(maxsize=None)
def _prepare_order_idx_map(num_racers: int, bet_type: BetType) -> dict[str, int]:
    """Orderを0-indexedのラベルに変換するためのマッピングを準備する"""
    mapping = {}
    idx = 0
    match bet_type:
        case BetType.tansyou:
            return {str(i): i - 1 for i in range(1, num_racers + 1)}
        case BetType.nirentan:
            for i in range(1, num_racers + 1):
                for j in range(1, num_racers + 1):
                    if i != j:
                        mapping[f"{i}-{j}"] = idx
                        idx += 1
            return mapping
        case BetType.nirenpuku:
            for i in range(1, num_racers + 1):
                for j in range(1, num_racers + 1):
                    if i < j:
                        mapping[f"{i}-{j}"] = idx
                        idx += 1
            return mapping
        case BetType.sanrentan:
            for i in range(1, num_racers + 1):
                for j in range(1, num_racers + 1):
                    for k in range(1, num_racers + 1):
                        if i != j and j != k and i != k:
                            mapping[f"{i}-{j}-{k}"] = idx
                            idx += 1
            return mapping
        case BetType.sanrenpuku:
            for i in range(1, num_racers + 1):
                for j in range(1, num_racers + 1):
                    for k in range(1, num_racers + 1):
                        if i < j and j < k:
                            mapping[f"{i}-{j}-{k}"] = idx
                            idx += 1
            return mapping
        case _:
            raise ValueError(f"bet_type {bet_type} is not supported")


class Order(BaseModel, frozen=True):
    """着順(Order)に関する基底クラス。連複での順番ソートなどのロジックを内包する
    利用する際には 2連単や3連単などの`bet_type`をメンバーに追加する

    Args:
        BaseModel (_type_): _description_
        frozen (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """

    first_course: int
    second_course: int | None = None
    third_course: int | None = None
    bet_type: BetType

    @field_validator("first_course", "second_course", "third_course")
    @classmethod
    def validate_course_number(cls, course_number: int | None) -> int | None:
        if course_number is not None:
            if course_number <= 0:
                raise ValueError("Invalid course number.")
        return course_number

    @model_validator(mode="after")
    def validate_courses(self) -> Self:
        """コンストラクタでは連複系のコースがソートされて渡されているかはチェックしない"""
        match self.bet_type:
            case BetType.tansyou:
                # 単勝: 1コースが必要
                if self.second_course is not None or self.third_course is not None:
                    raise ValueError("単勝では2コース、3コースは不要です。")

            case BetType.nirentan | BetType.nirenpuku:
                # 二連系: 2コースが必要
                if self.second_course is None or self.third_course is not None:
                    raise ValueError("2連系では2コースを指定し、3コースは不要です。")

            case BetType.sanrentan | BetType.sanrenpuku:
                # 三連系: 3コースが必要
                if self.second_course is None or self.third_course is None:
                    raise ValueError("3連系では3コースを指定する必要があります。")

            case _:
                raise ValueError(f"bet_type {self.bet_type} is not supported")

        return self

    def __hash__(self) -> int:
        return hash((self.__class__, self.__str__()))

    def __eq__(self, other: Self) -> bool:
        return self.__class__ == other.__class__ and self.__str__() == other.__str__()

    def __lt__(self, other):
        return self.__str__() < other.__str__()

    def get_first_course(self) -> int:
        # ソート済み着順の1着のコース番号を取得する
        return int(self._format_order().split("-")[0])

    def get_second_course(self) -> int:
        # ソート済み着順の2着のコース番号を取得する
        return int(self._format_order().split("-")[1])

    def get_third_course(self) -> int:
        # ソート済み着順の3着のコース番号を取得する
        return int(self._format_order().split("-")[2])

    @model_serializer
    def serialize_order(self) -> str:
        return self.__str__()

    @classmethod
    def create_from_str_order(cls, order_str: str, bet_type: BetType) -> Self:
        # "1-2-3"のような文字列からOrderを生成
        courses = order_str.split("-")
        if len(courses) == 1:
            return cls(bet_type=bet_type, first_course=int(courses[0]))
        elif len(courses) == 2:
            return cls(
                bet_type=bet_type,
                first_course=int(courses[0]),
                second_course=int(courses[1]),
            )
        elif len(courses) == 3:
            return cls(
                bet_type=bet_type,
                first_course=int(courses[0]),
                second_course=int(courses[1]),
                third_course=int(courses[2]),
            )
        else:
            raise ValueError("order_str must be 1-3 courses")

    def _format_order(self) -> str:
        """コースをフォーマットして返す. 連複系の場合は昇順ソートして返す"""
        match self.bet_type:
            case BetType.tansyou:
                return f"{self.first_course}"

            case BetType.nirentan:
                return f"{self.first_course}-{self.second_course}"

            case BetType.nirenpuku:
                assert self.second_course is not None
                sorted_courses = sorted([self.first_course, self.second_course])
                return f"{sorted_courses[0]}-{sorted_courses[1]}"

            case BetType.sanrentan:
                return f"{self.first_course}-{self.second_course}-{self.third_course}"

            case BetType.sanrenpuku:
                assert self.second_course is not None and self.third_course is not None
                sorted_courses = sorted(
                    [self.first_course, self.second_course, self.third_course]
                )
                return f"{sorted_courses[0]}-{sorted_courses[1]}-{sorted_courses[2]}"
            case _:
                raise ValueError(f"bet_type {self.bet_type} is not supported")

    def __str__(self) -> str:
        return self._format_order()

    @classmethod
    def create_rentan_orders_from_renpuku(cls, order_str: str) -> list[Self]:
        # 連複のオーダーから連単のオーダーを生成する
        courses = order_str.split("-")

        if len(courses) == 2:
            bet_type = BetType.nirentan

            try:
                cls.create_from_str_order(
                    bet_type=BetType.nirenpuku, order_str=order_str
                )
            except ValueError:
                raise ValueError("invalid order for nirenpuku")

        elif len(courses) == 3:
            bet_type = BetType.sanrentan

            try:
                cls.create_from_str_order(
                    bet_type=BetType.sanrenpuku, order_str=order_str
                )
            except ValueError:
                raise ValueError("invalid order for sanrenpuku")

        else:
            raise ValueError("order_str must be 2-3 courses")

        rentan_perm = list(itertools.permutations(courses))

        list_rentan_orders = []
        for p in rentan_perm:
            order = cls.create_from_str_order(bet_type=bet_type, order_str="-".join(p))
            list_rentan_orders.append(order)

        return list_rentan_orders

    @classmethod
    def get_all_order_patterns(cls, bet_type: BetType, num_racers: int) -> list[Self]:
        match bet_type:
            case BetType.tansyou:
                return sorted(
                    list(
                        set(
                            cls(bet_type=BetType.tansyou, first_course=i)
                            for i in range(1, num_racers + 1)
                        )
                    )
                )

            case BetType.nirentan:
                return sorted(
                    list(
                        set(
                            cls(
                                bet_type=BetType.nirentan,
                                first_course=i,
                                second_course=j,
                            )
                            for i in range(1, num_racers + 1)
                            for j in range(1, num_racers + 1)
                            if i != j
                        )
                    )
                )

            case BetType.nirenpuku:
                return sorted(
                    list(
                        set(
                            cls(
                                bet_type=BetType.nirenpuku,
                                first_course=i,
                                second_course=j,
                            )
                            for i in range(1, num_racers + 1)
                            for j in range(1, num_racers + 1)
                            if i != j
                        )
                    )
                )

            case BetType.sanrentan:
                return sorted(
                    list(
                        set(
                            cls(
                                bet_type=BetType.sanrentan,
                                first_course=i,
                                second_course=j,
                                third_course=k,
                            )
                            for i in range(1, num_racers + 1)
                            for j in range(1, num_racers + 1)
                            for k in range(1, num_racers + 1)
                            if i != j and j != k and i != k
                        )
                    )
                )

            case BetType.sanrenpuku:
                return sorted(
                    list(
                        set(
                            cls(
                                bet_type=BetType.sanrenpuku,
                                first_course=i,
                                second_course=j,
                                third_course=k,
                            )
                            for i in range(1, num_racers + 1)
                            for j in range(1, num_racers + 1)
                            for k in range(1, num_racers + 1)
                            if i != j and j != k and i != k
                        )
                    )
                )

            case _:
                raise ValueError(f"bet_type {bet_type} is not supported")

    def to_order_idx(self, num_racers: int = 6) -> int:
        """Orderを0-indexedのラベルに変換する"""

        order_str = self._format_order()
        order_idx_map = _prepare_order_idx_map(num_racers, self.bet_type)

        if order_str not in order_idx_map:
            raise ValueError(
                f"Order {order_str} is not valid for bet_type {self.bet_type}"
            )

        return order_idx_map[order_str]

    @classmethod
    def idx_to_order(
        cls, order_idx: int, bet_type: BetType, num_racers: int = 6
    ) -> Self:
        """0-indexedのラベルからOrderに変換する"""

        order_idx_map = _prepare_order_idx_map(num_racers, bet_type)
        reverse_map = {v: k for k, v in order_idx_map.items()}

        if order_idx not in reverse_map:
            raise ValueError(
                f"Order index {order_idx} is not valid for bet_type {bet_type}"
            )
        try:
            order_str = reverse_map[order_idx]
        except KeyError:
            raise ValueError(
                f"Order index {order_idx} is not valid for bet_type {bet_type}"
            )
        return cls.create_from_str_order(order_str=order_str, bet_type=bet_type)
