# 1Factory MCP Server — Plan

## Overview

 MCP server for the 1Factory API (v24.31), exposing manufacturing quality management data (part masters, inspection plans, inspections, FAIs, suppliers, and QMS records) as tools for AI agents.

## Tech Stack

- **Language:** Python
- **MCP SDK:** `mcp` package
- **Transport:** SSE via Starlette / uvicorn
- **HTTP Client:** `httpx` (async, gzip support, rate limit headers)

## Project Structure

```
1factory-mcp/
├── pyproject.toml
├── onefactory_mcp/
│   ├── __init__.py
│   ├── server.py           # MCP server + tool registration
│   ├── client.py           # 1Factory HTTP client (auth, rate limiting)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── part_masters.py
│   │   ├── plans.py
│   │   ├── inspections.py
│   │   ├── fais.py
│   │   ├── suppliers.py
│   │   ├── qms.py
│   │   └── work_orders.py
│   └── config.py           # Settings: ONEFACTORY_KEY, ONEFACTORY_ORG, ONEFACTORY_ENV
└── README.md
```

## Configuration

Environment variables or MCP client config:

| Variable | Required | Default | Description |
|--- |--- |--- |--- |
| `ONEFACTORY_KEY` | Yes | -- | API key (`x-1factory-key` header) |
| `ONEFACTORY_ORG` | Yes | -- | Organization ID (`x-1factory-org` header) |
| `ONEFACTORY_ENV` | No | `prod` | `prod`, `sandbox`, `val-prod`, `val-sandbox`, `local` |

Base URLs:
- `prod` → `https://www.1factory.com/api/v1`
- `sandbox` → `https://www.1factory.co/api/v1`
- `val-prod` → `https://val.1factory.com/api/v1`
- `val-sandbox` → `https://val.1factory.co/api/v1`
- `local` → `http://localhost:3000/api/v1` (dev convenience for pointing at a locally running API)

## Pagination & Rate Limits

- API limits: **60 requests/min**, **1000 requests/day**
- Max page size: 500
- Each list tool auto-paginates at `page_size=500` until no more results remain
- Results capped at ~5000 total to prevent runaway memory on large datasets
- Client monitors `x-ratelimit-*` response headers; backs off on 429 with exponential retry
- Responses include `total_fetched` count

## MCP Tools (19 total)

Grouped by domain rather than raw endpoint. List tools combine list + detail where appropriate.

### Part Master (3 tools)

| Tool | Description |
|--- |--- |
| `list_parts` | Lists part masters. Filters: `part_number`, `rev`, `status`, `type`, `is_assembly`, `is_itar`, `has_ppap`, `project_identifier`, `is_library`, `parent_part_number`, `parent_rev`, created/updated date ranges |
| `update_part` | Create or upsert a part master entry. `part_number` required. Optional: `rev`, `description`, `status`, `alt_part_number`, `alt_rev`, `alt_part_number2`, `alt_rev2`, `project_identifier`, `cost`, `unit`, `is_assembly`, `is_itar`, `is_buy`, `comments` |
| `update_assemblies` | Define/replace assembly sub-parts for a part. Body: `part_number`, `rev`, `sub_parts` array |

### Plans (2 tools)

| Tool | Description |
|--- |--- |
| `list_plans` | Lists inspection plans. Param: `domain` (`mfg`, `rec`, `sup`, `cus`). Filters: `part_number`, `rev`, `status`, `version_status`, `approval_status`, `customer`, `supplier`, `operation`, `is_tabulated` (forwarded as `is_tablulated` to match an upstream typo in the 1Factory API; both spellings accepted), `is_spec_lib`, date ranges. Filter availability varies by domain — unsupported filters are dropped per-domain. |
| `get_plan` | Gets detailed plan by `domain` + `plan_id`. Returns full plan with specifications and per-specification inspection types |

### Inspections (4 tools)

| Tool | Description |
|--- |--- |
| `list_inspections` | Lists inspections. Param: `domain` (`mfg`, `rec`, `sup`, `cus`). Filters: `part_number`, `rev`, `insp_ident_1`, `insp_ident_2`, `customer`, `supplier`, `project_identifier`, `operation`, `site`, `type` (inspection type), `insp_status`, `review_status`, date ranges. Filter availability varies by domain — unsupported filters are dropped per-domain. |
| `get_inspection` | Gets detailed inspection by `domain` + `inspection_id`. Returns specs, part_data, attachments |
| `create_mfg_inspection` | Creates manufacturing inspection. Requires: `insp_ident_1`, `part_number`, `inspection_type`. Optional: `insp_ident_2`, `insp_ident_3`, `rev`, `customer_name`, `machines`, `operation`, `lot_size` |
| `create_rec_inspection` | Creates receiving inspection. Requires: `insp_ident_1`, `part_number`, `inspection_type`. Optional: `insp_ident_2`, `insp_ident_3`, `rev`, `supplier_name`, `lot_size` |

### First-Article Inspections (3 tools)

| Tool | Description |
|--- |--- |
| `list_fais` | Lists FAIs. Param: `domain` (`mfg`, `rec`, `sup`, `cus`). Filters: `part_number`, `rev`, `insp_ident_1`, `insp_ident_2`, `customer`, `supplier`, `project_identifier`, `operation`, `site`, `type` (fai_type: Standard/AS9102), `insp_status`, `review_status`, `closed_after`. The 1Factory FAI list endpoints only support `closed_after` for date filtering — no `created_*`, `updated_*`, or `closed_before`. Other filters vary by domain. |
| `get_fai` | Gets detailed FAI by `domain` + `inspection_id`. Returns specs, part_data |
| `create_fai` | Creates FAI. Param: `domain` (`mfg` or `rec`). Requires: `insp_ident_1`, `part_number`, `fai_type`, `number_of_parts`. Optional: `insp_ident_2`, `rev`, `customer_name` (mfg), `supplier_name` (rec) |

### Suppliers (2 tools)

| Tool | Description |
|--- |--- |
| `list_suppliers` | Lists suppliers. Filters: created/updated date ranges |
| `get_supplier` | Gets supplier detail by `supplier_id`. Returns qualifications, certifications, contacts, addresses |

### QMS — Quality Management (3 tools)

| Tool | Description |
|--- |--- |
| `list_ncrs` | Lists Nonconformance Reports. Filters: created/updated/closed date ranges |
| `list_capas` | Lists CAPAs. Filters: created/updated/closed date ranges |
| `list_complaints` | Lists Complaints. Filters: created/updated/closed date ranges |

### Work Orders (2 tools)

| Tool | Description |
|--- |--- |
| `update_mfg_work_orders` | Updates manufacturing work order list (overwrites). Each entry: `insp_ident_1`, optional `insp_ident_2`, optional `lot_size` |
| `update_rec_work_orders` | Updates receiving work order list (overwrites). Same structure as mfg |

## Error Handling

- API errors return `{ "code": "...", "message": "..." }` — surfaced in tool result `error` field
- Rate limit (429): client auto-retries with exponential backoff; after max retries, returns error with remaining rate limit info
- Auth failures (401): returns clear message about missing/invalid key or org ID
