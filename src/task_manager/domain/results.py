"""Command results. A refusal is returned without writing rows."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Refusal:
    code: int
    message: str

    @property
    def body(self) -> dict[str, object]:
        return {"refused": True, "message": self.message}


def bad_request(message: str) -> Refusal:
    return Refusal(400, message)


def missing(message: str) -> Refusal:
    return Refusal(404, message)


def conflict(message: str) -> Refusal:
    return Refusal(409, message)
