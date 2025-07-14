from pydantic import BaseModel


class State(BaseModel):
    status: str = "idle"
    current_cycle: int = 0
    total_cycles: int = 0
    actuate_time: float = 0.0
    rest_time: float = 0.0
    current: float = 0.0
    current_cutoff: float = 0.0
    phase: str = "idle"
    phase_ends_at: float = 0.0
