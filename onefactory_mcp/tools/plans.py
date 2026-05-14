from typing import Any

from onefactory_mcp.client import OneFactoryClient


_DOMAINS = ("mfg", "rec", "sup", "cus")

# NOTE: `is_tablulated` is spelled this way in the upstream 1Factory OpenAPI spec
# (typo present on /{mfg,rec,sup,cus}/plans). Do not "fix" the spelling — the API
# only accepts the typo'd form. We also accept the correct spelling `is_tabulated`
# from callers and forward it under the typo'd name.
_PLAN_FILTERS_BY_DOMAIN: dict[str, set[str]] = {
    "mfg": {
        "part_number", "rev", "operation", "status", "version_status",
        "approval_status", "customer", "is_tablulated", "is_spec_lib",
        "created_after", "created_before", "updated_after", "updated_before",
        "closed_after", "closed_before",
    },
    "rec": {
        "part_number", "rev", "status", "version_status", "approval_status",
        "supplier", "is_tablulated", "is_spec_lib",
        "created_after", "created_before", "updated_after", "updated_before",
        "closed_after", "closed_before",
    },
    "sup": {
        "part_number", "rev", "status", "supplier", "is_tablulated",
        "created_after", "created_before", "updated_after", "updated_before",
        "closed_after", "closed_before",
    },
    "cus": {
        "part_number", "rev", "status", "approval_status", "customer",
        "is_tablulated", "created_after", "created_before",
        "updated_after", "updated_before", "closed_after", "closed_before",
    },
}


async def list_plans(kw: dict[str, Any]) -> dict[str, Any]:
    """List inspection plans for a given domain."""
    domain = (kw.get("domain") or "").lower()
    if domain not in _DOMAINS:
        return {"error": f"domain must be one of {_DOMAINS}"}

    # Accept the correct spelling from callers; forward under the API's typo.
    if kw.get("is_tabulated") is not None and kw.get("is_tablulated") is None:
        kw = {**kw, "is_tablulated": kw["is_tabulated"]}

    allowed = _PLAN_FILTERS_BY_DOMAIN[domain]
    filters: dict[str, Any] = {}
    for key in allowed:
        if key in kw and kw[key] is not None:
            val = kw[key]
            if isinstance(val, bool):
                val = str(val).lower()
            filters[key] = val

    async with OneFactoryClient() as client:
        results = await client.paginate(f"{domain}/plans", params=filters)
    return {"results": results, "total_fetched": len(results)}


async def get_plan(kw: dict[str, Any]) -> dict[str, Any]:
    """Get detailed inspection plan by domain and plan_id."""
    domain = (kw.get("domain") or "").lower()
    plan_id = kw.get("plan_id")

    if domain not in _DOMAINS:
        return {"error": f"domain must be one of {_DOMAINS}"}
    if plan_id is None:
        return {"error": "plan_id is required"}

    async with OneFactoryClient() as client:
        data, err = await client.get(f"{domain}/plans/{plan_id}")
    if err:
        return {"error": err}
    return data if isinstance(data, dict) else {"plan": data}
