from typing import Any

from onefactory_mcp.client import OneFactoryClient


_PART_FILTERS = {
    "part_number", "rev", "status", "type", "is_assembly", "is_itar",
    "has_ppap", "project_identifier", "is_library", "parent_part_number",
    "parent_rev", "created_after", "created_before", "updated_after", "updated_before",
}


async def list_parts(kw: dict[str, Any]) -> dict[str, Any]:
    """List part masters with optional filters."""
    filters: dict[str, Any] = {}
    for key in _PART_FILTERS:
        if key in kw and kw[key] is not None:
            val = kw[key]
            if isinstance(val, bool):
                val = str(val).lower()
            filters[key] = val

    async with OneFactoryClient() as client:
        results = await client.paginate("partMasters", params=filters)
    return {"results": results, "total_fetched": len(results)}


async def update_part(kw: dict[str, Any]) -> dict[str, Any]:
    """Create or upsert a part master entry."""
    if not kw.get("part_number"):
        return {"error": "part_number is required"}

    body: dict[str, Any] = {"part_number": kw["part_number"]}
    for field in [
        "rev", "description", "status", "alt_part_number", "alt_rev",
        "alt_part_number2", "alt_rev2", "project_identifier", "cost", "unit",
        "is_assembly", "is_itar", "is_buy", "comments",
    ]:
        if field in kw and kw[field] is not None:
            body[field] = kw[field]

    async with OneFactoryClient() as client:
        data, err = await client.put("partMasters", body)
    if err:
        return {"error": err}
    return {"updated": data}


async def update_assemblies(kw: dict[str, Any]) -> dict[str, Any]:
    """Define or replace assembly sub-parts for a part."""
    if not kw.get("part_number"):
        return {"error": "part_number is required"}
    if not kw.get("rev"):
        return {"error": "rev is required"}

    sub_parts = kw.get("sub_parts")
    if not sub_parts or not isinstance(sub_parts, list):
        return {"error": "sub_parts list is required"}

    body: dict[str, Any] = {
        "part_number": kw["part_number"],
        "rev": kw["rev"],
        "sub_parts": sub_parts,
    }

    async with OneFactoryClient() as client:
        data, err = await client.put("partMasters/assemblies", body)
    if err:
        return {"error": err}
    return {"updated": data}
