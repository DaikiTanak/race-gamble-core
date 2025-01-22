from pydantic import BaseModel, field_validator

from ..schemas.order import Order


class Odds(BaseModel, frozen=True):
    """オッズを表すクラス"""

    order: Order
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
        return self.convert_odds_value_to_prob(self.odds, koujo_rate)

    @classmethod
    def convert_odds_value_to_prob(cls, odds: float, koujo_rate: float = 0.25) -> float:
        # オッズを確率値に変換する

        if odds == 0:
            # 売り上げが0の場合はオッズが0になっている。その場合は確率も0とするのが適当
            return 0

        prob = (1 / odds) * (1 - koujo_rate)
        assert 0 <= prob <= 1, f"prob: {prob}, odds: {odds}"
        return prob

    def get_expected_roi(self, estimated_prob: float) -> float:
        return self.get_expected_roi_from_estimated_prob_and_public_odds(self.odds, estimated_prob)

    @classmethod
    def get_expected_roi_from_estimated_prob_and_public_odds(cls, odds: float, estimated_prob: float) -> float:
        # 推定確率を元に、期待ROI倍率を計算する
        # 0よりも大きい値が返る場合、期待値がプラスになる
        # e.g. 期待リターン倍率が0.2であれば、+20%の期待値があるということ

        # 推定確率での期待リターン倍率を算出
        return estimated_prob * odds - 1
