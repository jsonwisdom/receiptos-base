import pytest

from economics.v0_1.replay_engine import replay_economic_outcome

pytestmark = pytest.mark.skip(reason="Agent Economics Replay Engine V0.1 implementation pending")


def test_replay_engine_stub():
    assert callable(replay_economic_outcome)
