from pydantic import BaseModel, model_serializer
from typing import Self
from abc import abstractmethod
from typing import Any


class BaseOrder(BaseModel, frozen=True):
    """着順に関する基底クラス
    利用する際には `bet_type`をメンバーに追加する

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

    @model_serializer
    def serialize_order(self) -> str:
        return self.__str__()

    def _validate_courses(self):
        """派生クラスで実装"""
        raise NotImplementedError

    def _format_order(self) -> str:
        """派生クラスで実装"""
        raise NotImplementedError
