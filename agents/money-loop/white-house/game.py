from __future__ import annotations

from dataclasses import asdict, dataclass

GAME_ID = "WHITE_HOUSE_REPLAY_ARENA_V0_1"
MECHANIC_FIELDS = (
    "source_pointer_bound",
    "source_bytes_replayed",
    "identity_provenance_replayed",
    "delta_classified",
    "semantic_rendering_bounded",
    "exact_head_executed",
    "bypass_surfaces_blocked",
)


@dataclass(frozen=True)
class ReplayRound:
    round_id: str
    source_pointer_bound: bool
    source_bytes_replayed: bool
    identity_provenance_replayed: bool
    delta_classified: bool
    semantic_rendering_bounded: bool
    exact_head_executed: bool
    bypass_surfaces_blocked: bool
    claim_truth_proven: bool = False
    human_guilt_determined: bool = False
    authority_created: bool = False

    def validate(self) -> None:
        if not self.round_id.strip():
            raise ValueError("round_id required")
        if self.claim_truth_proven:
            raise ValueError("game mechanics cannot prove claim truth")
        if self.human_guilt_determined:
            raise ValueError("game mechanics cannot determine human guilt")
        if self.authority_created:
            raise ValueError("game mechanics cannot create authority")

    @property
    def mechanics_points(self) -> int:
        self.validate()
        return sum(bool(getattr(self, name)) for name in MECHANIC_FIELDS)

    @property
    def max_mechanics_points(self) -> int:
        return len(MECHANIC_FIELDS)

    @property
    def round_state(self) -> str:
        return "REPLAY_READY" if self.mechanics_points == self.max_mechanics_points else "HOLD"

    @property
    def badges(self) -> list[str]:
        return [name.upper() for name in MECHANIC_FIELDS if getattr(self, name)]

    def to_receipt(self) -> dict[str, object]:
        self.validate()
        payload = asdict(self)
        payload.update(
            {
                "game": GAME_ID,
                "mechanics_points": self.mechanics_points,
                "max_mechanics_points": self.max_mechanics_points,
                "round_state": self.round_state,
                "badges": self.badges,
                "score_proves_truth": False,
                "win_determines_guilt": False,
                "authority_created": False,
            }
        )
        return payload
