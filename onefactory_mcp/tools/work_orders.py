from typing import Any

from onefactory_mcp.client import OneFactoryClient


def _normalize_work_orders(work_orders: list[Any]) -> list[dict[str, Any]]:
    return [
        {k: v for k, v in entry.items() if v is not None}
        for entry in work_orders
        if isinstance(entry, dict)
    ]


async def _put_work_orders(path: str, kw: dict[str, Any]) -> dict[str, Any]:
    work_orders = kw.get("work_orders")
    if not work_orders or not isinstance(work_orders, list):
        return {"error": "work_orders list is required"}

    body = _normalize_work_orders(work_orders)

    async with OneFactoryClient() as client:
        data, err = await client.put(path, body)
    if err:
        return {"error": err}
    return {"updated": data}


async def update_mfg_work_orders(kw: dict[str, Any]) -> dict[str, Any]:
    """Update (overwrite) manufacturing work order list."""
    return await _put_work_orders("mfg/workOrderList", kw)


async def update_rec_work_orders(kw: dict[str, Any]) -> dict[str, Any]:
    """Update (overwrite) receiving work order list."""
    return await _put_work_orders("rec/workOrderList", kw)
