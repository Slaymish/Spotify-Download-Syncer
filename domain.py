from dataclasses import dataclass

@dataclass(frozen=True)
class Track:
    id: str
    uri: str
    name: str
    artist: str
