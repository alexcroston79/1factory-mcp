from typing import Any

from onefactory_mcp.client import OneFactoryClient


_DOMAINS = ("mfg", "rec", "sup", "cus")
_CREATE_DOMAINS = ("mfg", "rec")

# FAI list endpoints only support `closed_after` for date filtering — no created_*,
# updated_*, or closed_before. Other filters vary by domain.
_FAI_FILTERS_BY_DOMAIN: dict[str, set[str]] = {
    "mfg": {
        "part_number", "rev", "operation", "insp_ident_1", "insp_ident_2",
        "customer", "project_identifier", "site", "type", "insp_status",
        "review_status", "closed_after",
    },
    "rec": {
        "part_number", "rev", "insp_ident_1", "insp_ident_2", "supplier",
        "project_identifier", "site", "type", "insp_status", "review_status",
        "closed_after",
    },
    "sup": {
        "part_number", "rev", "insp_ident_1", "insp_ident_2", "supplier",
        "type", "insp_status", "review_status", "closed_after",
    },
    "cus": {
        "part_number", "rev", "insp_ident_1", "insp_ident_2", "customer",
        "type", "insp_status", "review_status", "closed_after",
    },
}


async def list_fais(kw: dict[str, Any]) -> dict[str, Any]:
    """List First-Article Inspections for a given domain."""
    domain = (kw.get("domain") or "").lower()
    if domain not in _DOMAINS:
        return {"error": f"domain must be one of {_DOMAINS}"}

    allowed = _FAI_FILTERS_BY_DOMAIN[domain]
    filters: dict[str, Any] = {}
    for key in allowed:
        if key in kw and kw[key] is not None:
            filters[key] = kw[key]

    async with OneFactoryClient() as client:
        results = await client.paginate(f"{domain}/fais", params=filters)
    return {"results": results, "total_fetched": len(results)}


async def get_fai(kw: dict[str, Any]) -> dict[str, Any]:
    """Get detailed FAI by domain and inspection_id."""
    domain = (kw.get("domain") or "").lower()
    inspection_id = kw.get("inspection_id")

    if domain not in _DOMAINS:
        return {"error": f"domain must be one of {_DOMAINS}"}
    if inspection_id is None:
        return {"error": "inspection_id is required"}

    async with OneFactoryClient() as client:
        data, err = await client.get(f"{domain}/fais/{inspection_id}")
    if err:
        return {"error": err}
    return data if isinstance(data, dict) else {"fai": data}


async def create_fai(kw: dict[str, Any]) -> dict[str, Any]:
    """Create an FAI (manufacturing or receiving)."""
    domain = (kw.get("domain") or "mfg").lower()
    if domain not in _CREATE_DOMAINS:
        return {"error": f"domain must be one of {_CREATE_DOMAINS} for creating FAIs"}

    for required in ("insp_ident_1", "part_number", "fai_type", "number_of_parts"):
        if kw.get(required) is None:
            return {"error": f"{required} is required"}

    body: dict[str, Any] = {
        "insp_ident_1": kw["insp_ident_1"],
        "part_number": kw["part_number"],
        "fai_type": kw["fai_type"],
        "number_of_parts": kw["number_of_parts"],
    }

    for field in ["insp_ident_2", "rev"]:
        if field in kw and kw[field] is not None:
            body[field] = kw[field]

    if domain == "mfg" and kw.get("customer_name"):
        body["customer_name"] = kw["customer_name"]
    if domain == "rec" and kw.get("supplier_name"):
        body["supplier_name"] = kw["supplier_name"]

    async with OneFactoryClient() as client:
        data, err = await client.post(f"{domain}/fais", body)
    if err:
        return {"error": err}
    return {"created": data}
