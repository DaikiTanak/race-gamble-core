# race-gamble-core

![Python Version](https://img.shields.io/badge/python-3.11%20-blue)
![Test Status](https://github.com/DaikiTanak/race-gamble-core/actions/workflows/run_unit_tests.yml/badge.svg)

レース系公営ギャンブルに共通する処理をまとめるコアライブラリ


## Usage/Examples

```python
from race_gamble_core.odds_prob import OddsProbCalculator

# map public odds to its probability
public_odds = 1.5
OddsProbCalculator().odds_to_prob(public_odds)
```
