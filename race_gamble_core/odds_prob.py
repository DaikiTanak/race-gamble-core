class OddsProbCalculator:
    """オッズと確率値の数学的な変換を行うクラス"""

    def __init__(self, koujo_rate: float = 0.25):
        self.koujo_rate = koujo_rate  # 控除率

    def odds_to_prob(self, odds_value: float) -> float:
        """オッズを確率値に変換"""
        # オッズを確率に変換する
        # 控除率で修正を行う必要があることに注意
        if odds_value == 0:
            return 0
        prob = (1 / odds_value) * (1 - self.koujo_rate)
        assert 0 <= prob <= 1, f"prob: {prob}, odds: {odds_value}"
        return prob

    def get_expected_roi(self, public_odds: float, estimated_prob: float) -> float:
        # 推定確率を元に、期待ROI倍率を計算する
        # 0よりも大きい値が返る場合、期待値がプラスになる
        # e.g. 期待リターン倍率が0.2であれば、+20%の期待値があるということ

        # 推定確率での期待リターン倍率を算出
        return estimated_prob * public_odds - 1
