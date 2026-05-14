from typing import Any

from onefactory_mcp.client import OneFactoryClient


async def list_suppliers(kw: dict[str, Any]) -> dict[str, Any]:
    """List suppliers with optional date filters."""
    filters: dict[str, Any] = {}
    for key in ("created_after", "created_before", "updated_after", "updated_before"):
        if key in kw and kw[key] is not None:
            filters[key] = kw[key]

    async with OneFactoryClient() as client:
        results = await client.paginate("sup", params=filters)
    return {"results": results, "total_fetched": len(results)}


async def get_supplier(kw: dict[str, Any]) -> dict[str, Any]:
    """Get supplier detail by supplier_id."""
    supplier_id = kw.get("supplier_id")
    if supplier_id is None:
        return {"error": "supplier_id is required"}

    async with OneFactoryClient() as client:
        data, err = await client.get(f"sup/{supplier_id}")
    if err:
        return {"error": err}
    return data if isinstance(data, dict) else {"supplier": data}
