from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class ChartPoint(BaseModel):
    label: str
    value: int


class AnalyticsSnapshot(BaseModel):
    total_chats: int
    open_chats: int
    closed_chats: int
    total_orders: int
    total_revenue: Decimal
    average_response_latency_ms: int
    sentiment_breakdown: list[ChartPoint] = Field(default_factory=list)
    intent_breakdown: list[ChartPoint] = Field(default_factory=list)
    missed_opportunity_breakdown: list[ChartPoint] = Field(default_factory=list)


def _attr(item: Any, name: str, default: Any = None) -> Any:
    return getattr(item, name, default)


def _chart(counter: Counter[str]) -> list[ChartPoint]:
    return [ChartPoint(label=label, value=value) for label, value in counter.most_common()]


def aggregate_chat_statuses(chats: Iterable[Any]) -> tuple[int, int, int]:
    chat_list = list(chats)
    open_chats = sum(1 for chat in chat_list if str(_attr(chat, "status", "")) == "open")
    closed_chats = sum(1 for chat in chat_list if str(_attr(chat, "status", "")) == "closed")
    return len(chat_list), open_chats, closed_chats


def aggregate_response_latency(messages: Iterable[Any]) -> int:
    values = [
        int(latency)
        for message in messages
        if str(_attr(message, "role", "")) == "assistant"
        for latency in [_attr(message, "latency_ms")]
        if latency is not None
    ]
    if not values:
        return 0
    return sum(values) // len(values)


def aggregate_revenue(orders: Iterable[Any]) -> tuple[int, Decimal]:
    order_list = list(orders)
    revenue = sum((Decimal(str(_attr(order, "total_price", 0))) for order in order_list), start=Decimal("0"))
    return len(order_list), revenue


def aggregate_reviews(reviews: Iterable[Any]) -> tuple[list[ChartPoint], list[ChartPoint], list[ChartPoint]]:
    sentiment_counter: Counter[str] = Counter()
    intent_counter: Counter[str] = Counter()
    missed_counter: Counter[str] = Counter()

    for review in reviews:
        sentiment = str(_attr(review, "sentiment", "")).strip()
        if sentiment:
            sentiment_counter[sentiment] += 1

        intent = str(_attr(review, "customer_intent", "")).strip()
        if intent:
            intent_counter[intent] += 1

        for item in _attr(review, "missed_opportunities", []) or []:
            missed_counter[str(item)] += 1

    return _chart(sentiment_counter), _chart(intent_counter), _chart(missed_counter)


def build_analytics_snapshot(
    *,
    chats: Iterable[Any],
    messages: Iterable[Any],
    orders: Iterable[Any],
    reviews: Iterable[Any],
) -> AnalyticsSnapshot:
    total_chats, open_chats, closed_chats = aggregate_chat_statuses(chats)
    total_orders, total_revenue = aggregate_revenue(orders)
    sentiment_breakdown, intent_breakdown, missed_breakdown = aggregate_reviews(reviews)

    return AnalyticsSnapshot(
        total_chats=total_chats,
        open_chats=open_chats,
        closed_chats=closed_chats,
        total_orders=total_orders,
        total_revenue=total_revenue,
        average_response_latency_ms=aggregate_response_latency(messages),
        sentiment_breakdown=sentiment_breakdown,
        intent_breakdown=intent_breakdown,
        missed_opportunity_breakdown=missed_breakdown,
    )
