from typing import TypedDict


class BakeObject(TypedDict):
    target: str
    sources: list[str]
