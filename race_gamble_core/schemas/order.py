from pydantic import BaseModel, model_serializer, field_validator, model_validator
from typing import Self
from .bet_type import BetType


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
            if not 1 <= course_number <= 9:
                raise ValueError("Invalid course number.")
        return course_number

    @model_validator(mode="after")
    def validate_courses(self) -> Self:
        match self.bet_type:
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
                sorted_courses = sorted([self.first_course, self.second_course, self.third_course])
                return f"{sorted_courses[0]}-{sorted_courses[1]}-{sorted_courses[2]}"
            case _:
                raise ValueError(f"bet_type {self.bet_type} is not supported")

    def __str__(self) -> str:
        return self._format_order()
