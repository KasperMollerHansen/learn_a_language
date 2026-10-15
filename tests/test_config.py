import math

from wordbank import SRC, read_json


DIFFICULTY_KEYS = {
    "roundDurationSeconds",
    "gateSpeedMultiplierPerCorrect",
    "gateSpeedMultiplierOnWrong",
}


def test_config_has_easy_and_hard_pacing() -> None:
    config = read_json(SRC / "config.json")

    assert set(config["difficulties"]) == {"easy", "hard"}
    assert not DIFFICULTY_KEYS & set(config), "per-difficulty values belong under difficulties"
    for pacing in config["difficulties"].values():
        assert set(pacing) == DIFFICULTY_KEYS
        assert all(math.isfinite(value) for value in pacing.values())
        assert isinstance(pacing["roundDurationSeconds"], int)
        assert pacing["roundDurationSeconds"] > 0
        assert pacing["gateSpeedMultiplierPerCorrect"] > 1
        assert pacing["gateSpeedMultiplierOnWrong"] > 1


def test_config_gate_interval_bounds() -> None:
    config = read_json(SRC / "config.json")

    assert (
        config["minimumGateIntervalSeconds"]
        <= config["initialGateIntervalSeconds"]
        <= config["maximumGateIntervalSeconds"]
    )
