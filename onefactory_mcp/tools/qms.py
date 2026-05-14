from typing import Any

from onefactory_mcp.client import OneFactoryClient


_QMS_FILTERS = (
    "created_after", "created_before", "updated_after", "updated_before",
    "closed_after", "closed_before",
)


def _qms_filters(kw: dict[str, Any]) -> dict[str, Any]:
    return {k: kw[k] for k in _QMS_FILTERS if k in kw and kw[k] is not None}


async def _list_qms(path: str, kw: dict[str, Any]) -> dict[str, Any]:
    async with OneFactoryClient() as client:
        results = await client.paginate(path, params=_qms_filters(kw))
    return {"results": results, "total_fetched": len(results)}


async def list_ncrs(kw: dict[str, Any]) -> dict[str, Any]:
    """List Nonconformance Reports."""
    return await _list_qms("qms/ncrs", kw)


async def list_capas(kw: dict[str, Any]) -> dict[str, Any]:
    """List CAPAs (Corrective and Preventive Actions)."""
    return await _list_qms("qms/capas", kw)


async def list_complaints(kw: dict[str, Any]) -> dict[str, Any]:
    """List Complaints."""
    return await _list_qms("qms/complaints", kw)
