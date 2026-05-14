"""1Factory MCP server — exposes 19 tools for quality management data.

Note on a known typo: the upstream 1Factory OpenAPI spec spells the
inspection-plan "is tabulated" filter as `is_tablulated` (extra 'l'). The plan
tool accepts both `is_tabulated` (correct) and `is_tablulated` (typo) and
forwards under the typo'd name that the API actually accepts.
"""

import json

from mcp.server import Server
from mcp.types import TextContent, Tool

import onefactory_mcp.tools.fais as fais_mod
import onefactory_mcp.tools.inspections as insp_mod
import onefactory_mcp.tools.part_masters as parts_mod
import onefactory_mcp.tools.plans as plans_mod
import onefactory_mcp.tools.qms as qms_mod
import onefactory_mcp.tools.suppliers as sup_mod
import onefactory_mcp.tools.work_orders as wo_mod

APP_NAME = "1factory-mcp"

TOOL_DEFINITIONS: dict[str, dict] = {
    # Part Masters
    "list_parts": {
        "description": "List part masters with optional filters (part_number, rev, status, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "part_number": {"type": "string", "description": "Filter by part number"},
                "rev": {"type": "string", "description": "Filter by revision"},
                "status": {"type": "string", "description": "Filter by status"},
                "type": {"type": "string", "description": "Filter by type"},
                "is_assembly": {"type": "boolean", "description": "Filter by assembly flag"},
                "is_itar": {"type": "boolean", "description": "Filter by ITAR flag"},
                "has_ppap": {"type": "boolean", "description": "Filter by PPAP flag"},
                "project_identifier": {"type": "string", "description": "Filter by project identifier"},
                "is_library": {"type": "boolean", "description": "Filter by library flag"},
                "parent_part_number": {"type": "string", "description": "Filter by parent part number"},
                "parent_rev": {"type": "string", "description": "Filter by parent revision"},
                "created_after": {"type": "string", "description": "ISO date filter"},
                "created_before": {"type": "string", "description": "ISO date filter"},
                "updated_after": {"type": "string", "description": "ISO date filter"},
                "updated_before": {"type": "string", "description": "ISO date filter"},
            },
        },
        "handler": parts_mod.list_parts,
    },
    "update_part": {
        "description": "Create or upsert a part master entry. part_number is required.",
        "inputSchema": {
            "type": "object",
            "required": ["part_number"],
            "properties": {
                "part_number": {"type": "string"},
                "rev": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string"},
                "alt_part_number": {"type": "string"},
                "alt_rev": {"type": "string"},
                "alt_part_number2": {"type": "string"},
                "alt_rev2": {"type": "string"},
                "project_identifier": {"type": "string"},
                "cost": {"type": "number"},
                "unit": {"type": "string"},
                "is_assembly": {"type": "boolean"},
                "is_itar": {"type": "boolean"},
                "is_buy": {"type": "boolean"},
                "comments": {"type": "string"},
            },
        },
        "handler": parts_mod.update_part,
    },
    "update_assemblies": {
        "description": "Define or replace assembly sub-parts for a part.",
        "inputSchema": {
            "type": "object",
            "required": ["part_number", "rev", "sub_parts"],
            "properties": {
                "part_number": {"type": "string"},
                "rev": {"type": "string"},
                "sub_parts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "part_number": {"type": "string"},
                            "quantity": {"type": "number"},
                            "rev": {"type": "string"},
                        },
                        "required": ["part_number", "rev", "quantity"],
                    },
                },
            },
        },
        "handler": parts_mod.update_assemblies,
    },
    # Plans
    "list_plans": {
        "description": "List inspection plans for a domain (mfg, rec, sup, cus).",
        "inputSchema": {
            "type": "object",
            "required": ["domain"],
            "properties": {
                "domain": {"type": "string", "enum": ["mfg", "rec", "sup", "cus"]},
                "part_number": {"type": "string"},
                "rev": {"type": "string"},
                "status": {"type": "string"},
                "version_status": {"type": "string"},
                "approval_status": {"type": "string"},
                "customer": {"type": "string"},
                "supplier": {"type": "string"},
                "operation": {"type": "string"},
                "is_tabulated": {
                    "type": "boolean",
                    "description": "Filter by tabulated flag (forwarded to the API as is_tablulated due to an upstream typo)",
                },
                "is_tablulated": {
                    "type": "boolean",
                    "description": "Raw API parameter name (preserves the upstream typo). Prefer is_tabulated.",
                },
                "is_spec_lib": {"type": "boolean"},
                "created_after": {"type": "string"},
                "created_before": {"type": "string"},
                "updated_after": {"type": "string"},
                "updated_before": {"type": "string"},
                "closed_after": {"type": "string"},
                "closed_before": {"type": "string"},
            },
        },
        "handler": plans_mod.list_plans,
    },
    "get_plan": {
        "description": "Get detailed inspection plan by domain and plan_id.",
        "inputSchema": {
            "type": "object",
            "required": ["domain", "plan_id"],
            "properties": {
                "domain": {"type": "string", "enum": ["mfg", "rec", "sup", "cus"]},
                "plan_id": {"type": "integer"},
            },
        },
        "handler": plans_mod.get_plan,
    },
    # Inspections
    "list_inspections": {
        "description": "List inspections for a domain (mfg, rec, sup, cus).",
        "inputSchema": {
            "type": "object",
            "required": ["domain"],
            "properties": {
                "domain": {"type": "string", "enum": ["mfg", "rec", "sup", "cus"]},
                "part_number": {"type": "string"},
                "rev": {"type": "string"},
                "insp_ident_1": {"type": "string"},
                "insp_ident_2": {"type": "string"},
                "customer": {"type": "string"},
                "supplier": {"type": "string"},
                "project_identifier": {"type": "string"},
                "operation": {"type": "string"},
                "site": {"type": "string"},
                "type": {"type": "string", "description": "Inspection type"},
                "insp_status": {"type": "string"},
                "review_status": {"type": "string"},
                "created_after": {"type": "string"},
                "created_before": {"type": "string"},
                "updated_after": {"type": "string"},
                "updated_before": {"type": "string"},
                "closed_after": {"type": "string"},
                "closed_before": {"type": "string"},
            },
        },
        "handler": insp_mod.list_inspections,
    },
    "get_inspection": {
        "description": "Get detailed inspection by domain and inspection_id.",
        "inputSchema": {
            "type": "object",
            "required": ["domain", "inspection_id"],
            "properties": {
                "domain": {"type": "string", "enum": ["mfg", "rec", "sup", "cus"]},
                "inspection_id": {"type": "integer"},
            },
        },
        "handler": insp_mod.get_inspection,
    },
    "create_mfg_inspection": {
        "description": "Create a manufacturing inspection.",
        "inputSchema": {
            "type": "object",
            "required": ["insp_ident_1", "part_number", "inspection_type"],
            "properties": {
                "insp_ident_1": {"type": "string"},
                "part_number": {"type": "string"},
                "inspection_type": {"type": "string"},
                "insp_ident_2": {"type": "string"},
                "insp_ident_3": {"type": "string"},
                "rev": {"type": "string"},
                "customer_name": {"type": "string"},
                "machines": {"type": "string"},
                "operation": {"type": "string"},
                "lot_size": {"type": "integer"},
            },
        },
        "handler": insp_mod.create_mfg_inspection,
    },
    "create_rec_inspection": {
        "description": "Create a receiving inspection.",
        "inputSchema": {
            "type": "object",
            "required": ["insp_ident_1", "part_number", "inspection_type"],
            "properties": {
                "insp_ident_1": {"type": "string"},
                "part_number": {"type": "string"},
                "inspection_type": {"type": "string"},
                "insp_ident_2": {"type": "string"},
                "insp_ident_3": {"type": "string"},
                "rev": {"type": "string"},
                "supplier_name": {"type": "string"},
                "lot_size": {"type": "integer"},
            },
        },
        "handler": insp_mod.create_rec_inspection,
    },
    # FAIs
    "list_fais": {
        "description": "List First-Article Inspections for a domain (mfg, rec, sup, cus).",
        "inputSchema": {
            "type": "object",
            "required": ["domain"],
            "properties": {
                "domain": {"type": "string", "enum": ["mfg", "rec", "sup", "cus"]},
                "part_number": {"type": "string"},
                "rev": {"type": "string"},
                "insp_ident_1": {"type": "string"},
                "insp_ident_2": {"type": "string"},
                "customer": {"type": "string"},
                "supplier": {"type": "string"},
                "project_identifier": {"type": "string"},
                "operation": {"type": "string"},
                "site": {"type": "string"},
                "type": {"type": "string", "description": "FAI type (Standard/AS9102)"},
                "insp_status": {"type": "string"},
                "review_status": {"type": "string"},
                "closed_after": {
                    "type": "string",
                    "description": "ISO date. Note: closed_after is the only date filter supported on FAI list endpoints.",
                },
            },
        },
        "handler": fais_mod.list_fais,
    },
    "get_fai": {
        "description": "Get detailed FAI by domain and inspection_id.",
        "inputSchema": {
            "type": "object",
            "required": ["domain", "inspection_id"],
            "properties": {
                "domain": {"type": "string", "enum": ["mfg", "rec", "sup", "cus"]},
                "inspection_id": {"type": "integer"},
            },
        },
        "handler": fais_mod.get_fai,
    },
    "create_fai": {
        "description": "Create an FAI (domain: mfg or rec).",
        "inputSchema": {
            "type": "object",
            "required": ["domain", "insp_ident_1", "part_number", "fai_type", "number_of_parts"],
            "properties": {
                "domain": {"type": "string", "enum": ["mfg", "rec"]},
                "insp_ident_1": {"type": "string"},
                "part_number": {"type": "string"},
                "fai_type": {"type": "string", "description": "e.g. Standard or AS9102"},
                "number_of_parts": {"type": "integer"},
                "insp_ident_2": {"type": "string"},
                "rev": {"type": "string"},
                "customer_name": {"type": "string"},
                "supplier_name": {"type": "string"},
            },
        },
        "handler": fais_mod.create_fai,
    },
    # Suppliers
    "list_suppliers": {
        "description": "List suppliers with optional date filters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "created_after": {"type": "string"},
                "created_before": {"type": "string"},
                "updated_after": {"type": "string"},
                "updated_before": {"type": "string"},
            },
        },
        "handler": sup_mod.list_suppliers,
    },
    "get_supplier": {
        "description": "Get supplier detail by supplier_id.",
        "inputSchema": {
            "type": "object",
            "required": ["supplier_id"],
            "properties": {
                "supplier_id": {"type": "integer"},
            },
        },
        "handler": sup_mod.get_supplier,
    },
    # QMS
    "list_ncrs": {
        "description": "List Nonconformance Reports (NCRs) with optional date filters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "created_after": {"type": "string"},
                "created_before": {"type": "string"},
                "updated_after": {"type": "string"},
                "updated_before": {"type": "string"},
                "closed_after": {"type": "string"},
                "closed_before": {"type": "string"},
            },
        },
        "handler": qms_mod.list_ncrs,
    },
    "list_capas": {
        "description": "List CAPAs (Corrective and Preventive Actions) with optional date filters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "created_after": {"type": "string"},
                "created_before": {"type": "string"},
                "updated_after": {"type": "string"},
                "updated_before": {"type": "string"},
                "closed_after": {"type": "string"},
                "closed_before": {"type": "string"},
            },
        },
        "handler": qms_mod.list_capas,
    },
    "list_complaints": {
        "description": "List Complaints with optional date filters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "created_after": {"type": "string"},
                "created_before": {"type": "string"},
                "updated_after": {"type": "string"},
                "updated_before": {"type": "string"},
                "closed_after": {"type": "string"},
                "closed_before": {"type": "string"},
            },
        },
        "handler": qms_mod.list_complaints,
    },
    # Work Orders
    "update_mfg_work_orders": {
        "description": "Update (overwrite) manufacturing work order list.",
        "inputSchema": {
            "type": "object",
            "required": ["work_orders"],
            "properties": {
                "work_orders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "insp_ident_1": {"type": "string"},
                            "insp_ident_2": {"type": "string"},
                            "lot_size": {"type": "integer"},
                        },
                    },
                },
            },
        },
        "handler": wo_mod.update_mfg_work_orders,
    },
    "update_rec_work_orders": {
        "description": "Update (overwrite) receiving work order list.",
        "inputSchema": {
            "type": "object",
            "required": ["work_orders"],
            "properties": {
                "work_orders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "insp_ident_1": {"type": "string"},
                            "insp_ident_2": {"type": "string"},
                            "lot_size": {"type": "integer"},
                        },
                    },
                },
            },
        },
        "handler": wo_mod.update_rec_work_orders,
    },
}


def _register_tools(server: Server, definitions: dict[str, dict]) -> None:
    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name=name,
                description=d["description"],
                inputSchema=d["inputSchema"],
            )
            for name, d in definitions.items()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        tool = definitions.get(name)
        if not tool:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        try:
            result = await tool["handler"](arguments)
        except Exception as exc:
            return [TextContent(type="text", text=f"Error: {exc}")]
        return [TextContent(type="text", text=json.dumps(result))]


def create_starlette_app() -> "Starlette":
    """Build the SSE-backed Starlette app."""
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import Response
    from starlette.routing import Mount, Route

    from mcp.server.sse import SseServerTransport

    server = Server(APP_NAME)
    _register_tools(server, TOOL_DEFINITIONS)

    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )
        return Response()

    return Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


app = create_starlette_app()


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)


if __name__ == "__main__":
    main()
