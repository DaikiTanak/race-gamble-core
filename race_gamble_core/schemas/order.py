from pydantic import BaseModel, model_serializer
from typing import Self
from abc import abstractmethod


class BaseOrder(BaseModel, frozen=True):
    """着順(Order)に関する基底クラス。連複での順番ソートなどのロジックを内包する
    利用する際には 2連単や3連単などの`bet_type`をメンバーに追加する

    e.g.

    class ExampleBetType(StrEnum):
        nirentan = "nirentan"
        sanrentan = "sanrentan"

    Args:
        BaseModel (_type_): _description_
        frozen (bool, optional): _description_. Defaults to True.

    Raises:
        NotImplementedError: _description_
        NotImplementedError: _description_

    Returns:
        _type_: _description_
    """

    first_course: int
    second_course: int | None = None
    third_course: int | None = None

    def __hash__(self) -> int:
        return hash((self.__class__, self.__str__()))

    def __eq__(self, other: Self) -> bool:
        return self.__class__ == other.__class__ and self.__str__() == other.__str__()

    def __str__(self) -> str:
        return self._format_order()

    def __post_init__(self):
        self._validate_courses()

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

    @abstractmethod
    def _validate_courses(self) -> None:
        """派生クラスで実装。コースの組み合わせのバリデーションを実装する。無効な着順の場合は例外を投げる

        主に人数の面でのバリデーションを行うとよい

        e.g.

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

        """
        raise NotImplementedError

    @abstractmethod
    def _format_order(self) -> str:
        """派生クラスで実装。着順を文字列として表現する。連複系は小さい順にソートして表示する"""
        raise NotImplementedError
