from schemas.evaluation_results import EvaluationResults


class TestEvaluationResults:
    def test_construct(self):
        eval_results = EvaluationResults(
            race_identifiers=[f"race{i}" for i in range(10)],
            confirmed_odds=[15, 5, 2, 3, 4, 5, 6, 7, 8, 9],
            flag_ground_truth_orders=[True, True, False, False, False, False, False, False, False, False],
            bet_amounts=[100, 100, 100, 300, 0, 0, 0, 0, 0, 0],
        )

        assert len(eval_results.race_identifiers) == 10

    def test_calc_statistic_results(self):
        eval_results = EvaluationResults(
            race_identifiers=[f"race{i}" for i in range(10)],
            confirmed_odds=[15, 5, 2, 3, 4, 5, 6, 7, 8, 9],
            flag_ground_truth_orders=[True, True, False, False, False, False, False, False, False, False],
            bet_amounts=[100, 100, 100, 300, 0, 0, 0, 0, 0, 0],
        ).calc_statistic_results()

        assert eval_results.total_bet_amount == 600
