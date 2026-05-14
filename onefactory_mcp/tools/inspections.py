from typing import Any

from onefactory_mcp.client import OneFactoryClient


_DOMAINS = ("mfg", "rec", "sup", "cus")

_INSPECTION_FILTERS_BY_DOMAIN: dict[str, set[str]] = {
    "mfg": {
        "part_number", "rev", "insp_ident_1", "insp_ident_2", "customer",
        "project_identifier", "operation", "site", "type", "insp_status",
        "review_status", "created_after", "created_before",
        "updated_after", "updated_before", "closed_after", "closed_before",
    },
    "rec": {
        "part_number", "rev", "insp_ident_1", "insp_ident_2", "supplier",
        "project_identifier", "site", "type", "insp_status", "review_status",
        "created_after", "created_before", "updated_after", "updated_before",
        "closed_after", "closed_before",
    },
    "sup": {
        "part_number", "rev", "insp_ident_1", "insp_ident_2", "supplier",
        "insp_status", "review_status",
        "created_after", "created_before", "updated_after", "updated_before",
        "closed_after", "closed_before",
    },
    "cus": {
        "part_number", "rev", "insp_ident_1", "insp_ident_2", "customer",
        "insp_status", "review_status", "closed_after",
    },
}


async def list_inspections(kw: dict[str, Any]) -> dict[str, Any]:
    """List inspections for a given domain."""
    domain = (kw.get("domain") or "").lower()
    if domain not in _DOMAINS:
        return {"error": f"domain must be one of {_DOMAINS}"}

    allowed = _INSPECTION_FILTERS_BY_DOMAIN[domain]
    filters: dict[str, Any] = {}
    for key in allowed:
        if key in kw and kw[key] is not None:
            filters[key] = kw[key]

    async with OneFactoryClient() as client:
        results = await client.paginate(f"{domain}/inspections", params=filters)
    return {"results": results, "total_fetched": len(results)}


async def get_inspection(kw: dict[str, Any]) -> dict[str, Any]:
    """Get detailed inspection by domain and inspection_id."""
    domain = (kw.get("domain") or "").lower()
    inspection_id = kw.get("inspection_id")

    if domain not in _DOMAINS:
        return {"error": f"domain must be one of {_DOMAINS}"}
    if inspection_id is None:
        return {"error": "inspection_id is required"}

    async with OneFactoryClient() as client:
        data, err = await client.get(f"{domain}/inspections/{inspection_id}")
    if err:
        return {"error": err}
    return data if isinstance(data, dict) else {"inspection": data}


async def create_mfg_inspection(kw: dict[str, Any]) -> dict[str, Any]:
    """Create a manufacturing inspection."""
    for required in ("insp_ident_1", "part_number", "inspection_type"):
        if not kw.get(required):
            return {"error": f"{required} is required"}

    body: dict[str, Any] = {
        "insp_ident_1": kw["insp_ident_1"],
        "part_number": kw["part_number"],
        "inspection_type": kw["inspection_type"],
    }
    for field in [
        "insp_ident_2", "insp_ident_3", "rev", "customer_name",
        "machines", "operation", "lot_size",
    ]:
        if field in kw and kw[field] is not None:
            body[field] = kw[field]

    async with OneFactoryClient() as client:
        data, err = await client.post("mfg/inspections", body)
    if err:
        return {"error": err}
    return {"created": data}


async def create_rec_inspection(kw: dict[str, Any]) -> dict[str, Any]:
    """Create a receiving inspection."""
    for required in ("insp_ident_1", "part_number", "inspection_type"):
        if not kw.get(required):
            return {"error": f"{required} is required"}

    body: dict[str, Any] = {
        "insp_ident_1": kw["insp_ident_1"],
        "part_number": kw["part_number"],
        "inspection_type": kw["inspection_type"],
    }
    for field in ["insp_ident_2", "insp_ident_3", "rev", "supplier_name", "lot_size"]:
        if field in kw and kw[field] is not None:
            body[field] = kw[field]

    async with OneFactoryClient() as client:
        data, err = await client.post("rec/inspections", body)
    if err:
        return {"error": err}
    return {"created": data}
