from pydantic import BaseModel, model_serializer
from ..schemas.bet_type import BetType
from typing import Self


class Order(BaseModel, frozen=True):
    # 着順や買い目でボートの順番を表現するクラス
    # strやdump時には"1-2-3"のようにフォーマットされる

    bet_type: BetType
    first_course: int
    second_course: int | None = None
    third_course: int | None = None

    def __hash__(self) -> int:
        return hash((self.bet_type, self.__str__()))

    def __eq__(self, other: Self) -> bool:
        return self.bet_type == other.bet_type and self.__str__() == other.__str__()

    def __post_init__(self):
        self._validate_courses()

    def __str__(self) -> str:
        return self._format_order()

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
            return cls(bet_type=bet_type, first_course=int(courses[0]), second_course=int(courses[1]))
        elif len(courses) == 3:
            return cls(
                bet_type=bet_type,
                first_course=int(courses[0]),
                second_course=int(courses[1]),
                third_course=int(courses[2]),
            )
        else:
            raise ValueError("order_str must be 1-3 courses")

    def get_first_course(self) -> int:
        # 並び替え後の1着目のコースを返す
        return int(self.__str__().split("-")[0])

    def get_second_course(self) -> int:
        # 並び替え後の2着目のコースを返す
        if self.second_course is None:
            raise ValueError("second_course is None")
        return int(self.__str__().split("-")[1])

    def get_third_course(self) -> int:
        # 並び替え後の3着目のコースを返す
        if self.third_course is None:
            raise ValueError("third_course is None")
        return int(self.__str__().split("-")[2])

    def _validate_courses(self):
        match self.bet_type:
            case BetType.nirentan | BetType.nirenpuku:
                # 二連系: 2コースが必要
                if self.second_course is None:
                    raise ValueError("二連系では2コースを指定し、3コースは不要です。")
            case BetType.sanrentan | BetType.sanrenpuku:
                # 三連系: 3コースが必要
                if self.second_course is None or self.third_course is None:
                    raise ValueError("三連系では3コースを指定する必要があります。")
            case _:
                raise ValueError(f"bet_type {self.bet_type} is not supported")

    def _format_order(self) -> str:
        """コースをフォーマットして返す"""
        match self.bet_type:
            case BetType.tansyou:
                return f"{self.first_course}"
            case BetType.nirentan:
                return f"{self.first_course}-{self.second_course}"
            case BetType.nirenpuku:
                sorted_courses = sorted([self.first_course, self.second_course])  # type: ignore
                return f"{sorted_courses[0]}-{sorted_courses[1]}"
            case BetType.sanrentan:
                return f"{self.first_course}-{self.second_course}-{self.third_course}"
            case BetType.sanrenpuku:
                sorted_courses = sorted([self.first_course, self.second_course, self.third_course])  # type: ignore
                return f"{sorted_courses[0]}-{sorted_courses[1]}-{sorted_courses[2]}"
            case _:
                raise ValueError(f"bet_type {self.bet_type} is not supported")
