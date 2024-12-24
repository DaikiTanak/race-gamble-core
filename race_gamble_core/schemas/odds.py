from typing import NewType
from pydantic import BaseModel, field_validator
from schemas.order import Order

import logging


logger = logging.getLogger(__name__)


OddsValue = NewType("OddsValue", float)

KOUJO_RATE = 0.25


class Odds(BaseModel):
    order: Order  # 着順
    odds: OddsValue  # オッズ

    @field_validator("odds")
    def validate_odds(cls, v):
        if v < 0:
            raise ValueError("odds must be positive")
        return v

    @classmethod
    def odds_to_prob(cls, odds: float) -> float:
        # オッズを確率に変換する
        # 控除率で修正を行う必要があることに注意
        if odds == 0:
            return 0
        prob = (1 / odds) * (1 - KOUJO_RATE)
        assert 0 <= prob <= 1, f"prob: {prob}, odds: {odds}"
        return prob

    @classmethod
    def get_expected_roi(cls, public_odds: float, estimated_prob: float) -> float:
        # 推定確率を元に、期待ROI倍率を計算する
        # 0よりも大きい値が返る場合、期待値がプラスになる
        # e.g. 期待リターン倍率が0.2であれば、+20%の期待値があるということ

        # 推定確率での期待リターン倍率を算出
        return estimated_prob * public_odds - 1
