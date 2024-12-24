from pydantic import BaseModel, model_validator, ConfigDict, field_serializer
from typing import Self
import numpy as np
from numpy.typing import NDArray


class EvaluationStatisticResults(BaseModel):
    # 買い付け戦略の評価結果の統計値
    model_config = ConfigDict(frozen=True)

    # 以下は自動計算される統計値フィールド
    num_bet_races: int  # 参加レース数
    num_all_races: int  # 全レース数
    num_bets: int  # 購入回数
    num_tekityu: int  # 的中回数
    tekityu_rate: float  # 的中率
    bet_race_rate: float  # 参加レース率

    total_bet_amount: int  # 総賭け金
    total_return_amount: int  # 総払い戻し金額
    total_profit: int  # 総利益金額
    total_roi: float  # 総利益率

    return_amount_average: float  # 払い戻し金額の平均
    return_amount_variance: float  # 払い戻し金額の分散
    return_amount_std: float  # 払い戻し金額の標準偏差
    sharpe_ratio: float  # シャープレシオ

    @field_serializer(
        "tekityu_rate",
        "bet_race_rate",
        "total_roi",
        "return_amount_average",
        "return_amount_variance",
        "return_amount_std",
        "sharpe_ratio",
    )
    def round_float(self, value: float) -> float:
        return round(value, 3)

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)


class EvaluationResults(BaseModel):
    # 買い付け戦略の評価結果
    model_config = ConfigDict(frozen=True)

    race_identifiers: list[str]  # レース識別子
    confirmed_odds: list[float]  # 確定オッズ. 払い戻し倍率
    flag_ground_truth_orders: list[bool]  # 的中着順フラグ
    bet_amounts: list[int]  # 買い付け金額リスト。0は買い付けなしを表す

    @staticmethod
    def _check_equal_lengths(*lists):
        """
        可変個のリストを受け取り、それらの長さがすべて等しいかを確認する関数。

        Parameters:
            *lists: 可変個のリスト

        Returns:
            bool: すべてのリストの長さが等しい場合はTrue、それ以外はFalse
        """
        if not lists:
            return True  # リストが渡されない場合はTrueとする（特に問題がないケースとして）

        # 最初のリストの長さを取得
        first_length = len(lists[0])

        # 他のリストの長さと比較
        return all(len(lst) == first_length for lst in lists)

    @model_validator(mode="after")
    def check_list_length(self) -> Self:
        assert self._check_equal_lengths(
            self.race_identifiers,
            self.confirmed_odds,
            self.flag_ground_truth_orders,
            self.bet_amounts,
        ), "length of input lists must be the same"
        return self

    def calc_statistic_results(self) -> EvaluationStatisticResults:

        num_records = len(self.race_identifiers)

        flag_bet_targets = [True if bet_amount > 0 else False for bet_amount in self.bet_amounts]

        arr_race_identifiers: NDArray = np.array(self.race_identifiers)
        arr_flag_bet_targets: NDArray = np.array(flag_bet_targets)

        num_bet_races = np.unique(arr_race_identifiers[arr_flag_bet_targets]).size
        num_all_races = np.unique(arr_race_identifiers).size

        num_bets = flag_bet_targets.count(True)

        # ベット対象のオッズに対する払い戻し金額のリストを作成(ハズレは0払い戻しとして含む)
        list_return_amount = []
        for i in range(num_records):
            if flag_bet_targets[i]:  # ベット対象
                if self.flag_ground_truth_orders[i]:
                    # あたり
                    return_amount = self.bet_amounts[i] * self.confirmed_odds[i]
                else:
                    # ハズレ
                    return_amount = 0
                list_return_amount.append(return_amount)
        assert len(list_return_amount) == num_bets, "購入回数と払い戻し金額リストの長さが一致しません"

        # ベット対象かつ的中かを表すフラグlist
        flag_tekityu_orders = [self.flag_ground_truth_orders[i] and flag_bet_targets[i] for i in range(num_records)]
        num_tekityu = [1 for return_amount in flag_tekityu_orders if return_amount].count(1)
        assert (
            0 < num_bet_races <= num_bets
        ), f"参加レース数は購入回数よりも少ないはずです: {num_bet_races} < {num_bets}"

        tekityu_rate = num_tekityu / num_bets if num_bets > 0 else 0
        bet_race_rate = num_bet_races / num_all_races if num_all_races > 0 else 0

        total_return_amount = sum(list_return_amount)
        total_bet_amount = sum(self.bet_amounts)
        total_profit = total_return_amount - total_bet_amount
        total_roi = total_profit / total_bet_amount if total_bet_amount > 0 else 0

        return_amount_average = float(np.mean(list_return_amount))
        return_amount_variance = float(np.var(list_return_amount))
        return_amount_std = float(np.std(list_return_amount))
        sharpe_ratio = total_profit / return_amount_std if return_amount_std > 0 else 0

        return EvaluationStatisticResults(
            num_bet_races=num_bet_races,
            num_all_races=num_all_races,
            total_bet_amount=total_bet_amount,
            num_bets=num_bets,
            num_tekityu=num_tekityu,
            tekityu_rate=tekityu_rate,
            bet_race_rate=bet_race_rate,
            total_profit=total_profit,
            total_roi=total_roi,
            total_return_amount=total_return_amount,
            return_amount_average=return_amount_average,
            return_amount_variance=return_amount_variance,
            return_amount_std=return_amount_std,
            sharpe_ratio=sharpe_ratio,
        )
