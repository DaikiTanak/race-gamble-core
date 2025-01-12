from pydantic import BaseModel, field_validator
from ..schemas.order import BaseOrder


class BaseOdds(BaseModel, frozen=True):
    """オッズに関する基底クラス
    利用する際には `order`をメンバーに追加する

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

    order: BaseOrder  # 実際の利用時にはBaseOrderを継承したクラスのインスタンスを渡す
    odds: float

    @field_validator("odds")
    @classmethod
    def validate_odds(cls, v):
        # オッズを確率に変換する
        # 控除率で修正を行う必要があることに注意
        if v < 0:
            raise ValueError("odds must be positive")
        return v

    def odds_to_prob(self, koujo_rate: float = 0.25) -> float:
        # オッズを確率値に変換する
        prob = (1 / self.odds) * (1 - koujo_rate)
        assert 0 <= prob <= 1, f"prob: {prob}, odds: {self.odds}"
        return prob

    def get_expected_roi(self, estimated_prob: float) -> float:
        # 推定確率を元に、期待ROI倍率を計算する
        # 0よりも大きい値が返る場合、期待値がプラスになる
        # e.g. 期待リターン倍率が0.2であれば、+20%の期待値があるということ

        # 推定確率での期待リターン倍率を算出
        return estimated_prob * self.odds - 1
