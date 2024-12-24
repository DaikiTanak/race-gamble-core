from pydantic import BaseModel, model_validator, ConfigDict
from typing import Self
import numpy as np
from numpy.typing import NDArray


class EvaluationStatisticResults(BaseModel):
    # 買い付け戦略の評価結果の統計値
    model_config = ConfigDict(frozen=True)

    # 以下は自動計算される統計値フィールド
    total_bet_amount: int = 0  # 総賭け金
    num_bet_races: int = 0  # 参加レース数
    num_all_races: int = 0  # 全レース数
    num_bets: int = 0  # 購入回数
    num_tekityu: int = 0  # 的中回数
    tekityu_rate: float = 0  # 的中率
    bet_race_rate: float = 0  # 参加レース率
    total_profit: int = 0  # 総利益金額
    total_roi: float = 0  # 総利益率
    total_return_amount: int = 0  # 総払い戻し金額

    return_amount_average: float = 0  # 払い戻し金額の平均
    return_amount_variance: float = 0  # 払い戻し金額の分散
    return_amount_std: float = 0  # 払い戻し金額の標準偏差
    sharpe_ratio: float = 0  # シャープレシオ

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)


class EvaluationResults(BaseModel):
    # 買い付け戦略の評価結果
    model_config = ConfigDict(frozen=True)

    race_identifiers: list[str]  # レース識別子
    confirmed_odds: list[float]  # 確定オッズ. 払い戻し
    flag_ground_truth_orders: list[bool]  # 的中着順フラグ
    bet_amounts: list[int]  # 買い付け金額リスト

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
        arr_confirmed_odds: NDArray = np.array(self.confirmed_odds)

        num_bet_races = np.unique(arr_race_identifiers[arr_flag_bet_targets]).size
        num_all_races = np.unique(arr_race_identifiers).size

        flag_tekityu_orders = [self.flag_ground_truth_orders[i] and flag_bet_targets[i] for i in range(num_records)]

        list_return_amount = (
            arr_confirmed_odds[flag_tekityu_orders] * np.array(self.bet_amounts)[flag_tekityu_orders]
        ).tolist()

        num_bets = flag_bet_targets.count(True)
        num_tekityu = [1 for return_amount in list_return_amount if return_amount > 0].count(1)
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
