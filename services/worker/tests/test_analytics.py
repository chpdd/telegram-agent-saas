import sys
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

WORKER_SRC = str(Path(__file__).parents[1] / "src")
if WORKER_SRC in sys.path:
    sys.path.remove(WORKER_SRC)
sys.path.insert(0, WORKER_SRC)

for module_name in ["analytics"]:
    sys.modules.pop(module_name, None)

from analytics import (  # noqa: E402
    aggregate_response_latency,
    aggregate_reviews,
    build_analytics_snapshot,
)


def test_aggregate_response_latency_uses_assistant_messages_only():
    latency = aggregate_response_latency(
        [
            SimpleNamespace(role="assistant", latency_ms=200),
            SimpleNamespace(role="assistant", latency_ms=400),
            SimpleNamespace(role="user", latency_ms=50),
        ]
    )

    assert latency == 300


def test_aggregate_reviews_counts_sentiment_intent_and_missed_sales():
    sentiment, intent, missed = aggregate_reviews(
        [
            SimpleNamespace(
                sentiment="positive",
                customer_intent="buy sofa",
                missed_opportunities=["delivery", "assembly"],
            ),
            SimpleNamespace(
                sentiment="negative",
                customer_intent="buy sofa",
                missed_opportunities=["delivery"],
            ),
        ]
    )

    assert [(point.label, point.value) for point in sentiment] == [("positive", 1), ("negative", 1)]
    assert [(point.label, point.value) for point in intent] == [("buy sofa", 2)]
    assert [(point.label, point.value) for point in missed] == [("delivery", 2), ("assembly", 1)]


def test_build_analytics_snapshot_returns_chart_ready_metrics():
    snapshot = build_analytics_snapshot(
        chats=[
            SimpleNamespace(status="open"),
            SimpleNamespace(status="closed"),
            SimpleNamespace(status="closed"),
        ],
        messages=[
            SimpleNamespace(role="assistant", latency_ms=100),
            SimpleNamespace(role="assistant", latency_ms=300),
        ],
        orders=[
            SimpleNamespace(total_price=Decimal("10.50")),
            SimpleNamespace(total_price=Decimal("5.00")),
        ],
        reviews=[
            SimpleNamespace(
                sentiment="neutral",
                customer_intent="check stock",
                missed_opportunities=["upsell"],
            )
        ],
    )

    assert snapshot.total_chats == 3
    assert snapshot.open_chats == 1
    assert snapshot.closed_chats == 2
    assert snapshot.total_orders == 2
    assert snapshot.total_revenue == Decimal("15.50")
    assert snapshot.average_response_latency_ms == 200
    assert [(point.label, point.value) for point in snapshot.sentiment_breakdown] == [("neutral", 1)]
