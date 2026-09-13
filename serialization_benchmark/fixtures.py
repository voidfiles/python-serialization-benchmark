from __future__ import annotations

from dataclasses import dataclass

from serialization_benchmark.contracts import JsonObject, JsonValue


@dataclass
class Child:
    w: int
    x: int
    y: str
    z: int


@dataclass
class Parent:
    foo: str
    count: int
    active: bool
    ratio: float
    sub: Child
    subs: list[Child]


@dataclass(frozen=True)
class FixtureSet:
    one: Parent
    many: tuple[Parent, ...]
    one_primitive: JsonObject
    many_primitives: tuple[JsonObject, ...]


def make_child(seed: int) -> Child:
    return Child(w=100 + seed, x=20 + seed, y=f"hello-{seed}", z=10 + seed)


def make_parent(seed: int) -> Parent:
    return Parent(
        foo=f"parent-{seed}",
        count=seed,
        active=seed % 2 == 0,
        ratio=seed + 0.5,
        sub=make_child(seed),
        subs=[make_child(seed * 10 + index) for index in range(10)],
    )


def child_to_primitive(value: Child) -> JsonObject:
    return {"w": value.w, "x": value.x, "y": value.y, "z": value.z}


def parent_to_primitive(value: Parent) -> JsonObject:
    return {
        "foo": value.foo,
        "count": value.count,
        "active": value.active,
        "ratio": value.ratio,
        "sub": child_to_primitive(value.sub),
        "subs": [child_to_primitive(child) for child in value.subs],
    }


def _require_int(value: JsonValue) -> int:
    if type(value) is not int:
        raise TypeError(f"expected int, got {type(value).__name__}")
    return value


def _require_bool(value: JsonValue) -> bool:
    if type(value) is not bool:
        raise TypeError(f"expected bool, got {type(value).__name__}")
    return value


def _require_float(value: JsonValue) -> float:
    if type(value) is not float:
        raise TypeError(f"expected float, got {type(value).__name__}")
    return value


def _require_str(value: JsonValue) -> str:
    if not isinstance(value, str):
        raise TypeError(f"expected str, got {type(value).__name__}")
    return value


def _child_from_object(value: JsonValue) -> Child:
    if not isinstance(value, dict):
        raise TypeError(f"expected child dictionary, got {type(value).__name__}")
    return Child(
        w=_require_int(value["w"]),
        x=_require_int(value["x"]),
        y=_require_str(value["y"]),
        z=_require_int(value["z"]),
    )


def parent_from_primitive(value: JsonObject) -> Parent:
    raw_subs = value["subs"]
    if not isinstance(raw_subs, list):
        raise TypeError("expected subs to be a list")
    return Parent(
        foo=_require_str(value["foo"]),
        count=_require_int(value["count"]),
        active=_require_bool(value["active"]),
        ratio=_require_float(value["ratio"]),
        sub=_child_from_object(value["sub"]),
        subs=[_child_from_object(child) for child in raw_subs],
    )


def normalize_parent(value: object) -> Parent:
    if not isinstance(value, Parent):
        raise TypeError(f"expected Parent, got {type(value).__name__}")
    return value


def make_fixtures(batch_size: int = 100) -> FixtureSet:
    if batch_size != 100:
        raise ValueError("the canonical batch size is 100")
    many = tuple(make_parent(index) for index in range(batch_size))
    primitives = tuple(parent_to_primitive(parent) for parent in many)
    return FixtureSet(
        one=many[0],
        many=many,
        one_primitive=primitives[0],
        many_primitives=primitives,
    )
