from race_gamble_core.schemas.evaluation_results import BetStrategyResults
import numpy as np
import pytest


class TestEvaluationResults:
    def test_construct(self):
        eval_results = BetStrategyResults(
            race_identifiers=[f"race{i}" for i in range(10)],
            confirmed_odds=[15, 5, 2, 3, 4, 5, 6, 7, 8, 9],
            flag_ground_truth_orders=[True, True, False, False, False, False, False, False, False, False],
            bet_amounts=[100, 100, 100, 300, 0, 0, 0, 0, 0, 0],
        )

        assert len(eval_results.race_identifiers) == 10

    def test_construct_invalid_bets(self):
        with pytest.raises(ValueError):
            _ = BetStrategyResults(
                race_identifiers=[f"race{i}" for i in range(1)],
                confirmed_odds=[15],
                flag_ground_truth_orders=[True],
                bet_amounts=[110],
            )

    def test_construct_diff_lengths(self):
        with pytest.raises(ValueError):
            _ = BetStrategyResults(
                race_identifiers=[f"race{i}" for i in range(10000)],
                confirmed_odds=[15],
                flag_ground_truth_orders=[True],
                bet_amounts=[110],
            )

    def test_calc_statistic_results(self):
        eval_results = BetStrategyResults(
            race_identifiers=[f"race{i}" for i in range(10)],
            confirmed_odds=[15, 5, 2, 3, 4, 5, 6, 7, 8, 9],
            flag_ground_truth_orders=[True, True, False, False, False, False, False, False, False, False],
            bet_amounts=[100, 100, 100, 300, 0, 0, 0, 0, 0, 0],
        ).calc_statistic_results()

        assert eval_results.num_bet_races == 4
        assert eval_results.num_all_races == 10
        assert eval_results.num_bets == 4
        assert eval_results.num_tekityu == 2
        assert eval_results.tekityu_rate == 0.5
        assert eval_results.bet_race_rate == 0.4

        assert eval_results.total_bet_amount == 600
        assert eval_results.total_return_amount == 2000
        assert eval_results.total_profit == 1400
        assert np.isclose(eval_results.total_roi, 2.3333333333333335)

        assert np.isclose(eval_results.return_amount_average, 500)
        assert np.isclose(eval_results.return_amount_variance, 375000)  # 1000000+0+250000+250000/4
