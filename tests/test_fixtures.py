from serialization_benchmark.fixtures import (
    Child,
    Parent,
    make_fixtures,
    parent_from_primitive,
    parent_to_primitive,
)


def test_fixture_set_is_deterministic_and_has_100_distinct_parents() -> None:
    first = make_fixtures()
    second = make_fixtures()

    assert first == second
    assert len(first.many) == 100
    assert len(set(parent.foo for parent in first.many)) == 100
    assert first.one == first.many[0]


def test_fixture_round_trip_is_exact() -> None:
    fixtures = make_fixtures()

    assert parent_from_primitive(parent_to_primitive(fixtures.one)) == fixtures.one
    assert fixtures.one == Parent(
        foo="parent-0",
        count=0,
        active=True,
        ratio=0.5,
        sub=Child(w=100, x=20, y="hello-0", z=10),
        subs=[
            Child(w=100 + index, x=20 + index, y=f"hello-{index}", z=10 + index)
            for index in range(10)
        ],
    )
