import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parents[1] / "src"))

from catalog_crud import (  # noqa: E402
    create_catalog_product,
    delete_catalog_product,
    normalize_product_payload,
    update_catalog_product,
)


def test_normalize_product_payload_validates_required_fields():
    payload = normalize_product_payload(
        "11111111-1111-1111-1111-111111111111",
        name="Штукатурка",
        category="Сухие смеси",
        measure="мешок",
        price=350,
        description="Гипсовая",
    )

    assert payload["name"] == "Штукатурка"
    assert payload["category"] == "Сухие смеси"
    assert payload["measure"] == "мешок"
    assert payload["price"] == 350.0

    with pytest.raises(ValueError, match="название"):
        normalize_product_payload(
            "11111111-1111-1111-1111-111111111111",
            name="",
            category="cat",
            measure="m",
            price=1,
        )


@pytest.mark.asyncio
async def test_create_catalog_product_inserts_row(mocker):
    session = mocker.AsyncMock()

    created = await create_catalog_product(
        session,
        tenant_id="11111111-1111-1111-1111-111111111111",
        name="Штукатурка",
        description="Гипсовая",
        category="Сухие смеси",
        measure="мешок",
        price=350,
    )

    assert created["name"] == "Штукатурка"
    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_catalog_product_requires_existing_row(mocker):
    session = mocker.AsyncMock()
    session.execute.return_value.rowcount = 0

    with pytest.raises(ValueError, match="Товар не найден"):
        await update_catalog_product(
            session,
            tenant_id="11111111-1111-1111-1111-111111111111",
            product_id="22222222-2222-2222-2222-222222222222",
            name="Штукатурка",
            description="Гипсовая",
            category="Сухие смеси",
            measure="мешок",
            price=350,
        )


@pytest.mark.asyncio
async def test_delete_catalog_product_deletes_row(mocker):
    session = mocker.AsyncMock()
    session.execute.return_value.rowcount = 1

    await delete_catalog_product(
        session,
        tenant_id="11111111-1111-1111-1111-111111111111",
        product_id="22222222-2222-2222-2222-222222222222",
    )

    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()
