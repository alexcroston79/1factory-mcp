# 1Factory MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An [MCP](https://modelcontextprotocol.io/) server for the [1Factory API](https://www.1factory.com/api/v1/1factory-api.json) (v24.31), exposing manufacturing quality management data — part masters, inspection plans, inspections, FAIs, suppliers, and QMS records — as tools for AI agents.

## Tools (19)

| Domain | Tools |
|---|---|
| **Part Masters** | `list_parts`, `update_part`, `update_assemblies` |
| **Plans** | `list_plans`, `get_plan` |
| **Inspections** | `list_inspections`, `get_inspection`, `create_mfg_inspection`, `create_rec_inspection` |
| **FAIs** | `list_fais`, `get_fai`, `create_fai` |
| **Suppliers** | `list_suppliers`, `get_supplier` |
| **QMS** | `list_ncrs`, `list_capas`, `list_complaints` |
| **Work Orders** | `update_mfg_work_orders`, `update_rec_work_orders` |

List tools auto-paginate at `page_size=500` up to ~5000 results and back off on 429s using the API's `x-ratelimit-minute-reset` / `x-ratelimit-day-reset` headers.

## Install

```bash
pip install -e .
```

## Configuration

| Variable | Required | Description |
|---|---|---|
| `ONEFACTORY_KEY` | Yes | API key (sent as `x-1factory-key`) |
| `ONEFACTORY_ORG` | Yes | Organization ID (sent as `x-1factory-org`) |
| `ONEFACTORY_ENV` | No | `prod` (default), `sandbox`, `val-prod`, `val-sandbox`, or `local` |

## Run

```bash
export ONEFACTORY_KEY="your-api-key"
export ONEFACTORY_ORG="your-org-id"
1factory-mcp
```

Serves MCP over SSE on `http://0.0.0.0:8765/sse`.

## MCP Client Config

```jsonc
{
  "mcpServers": {
    "1factory": {
      "command": "1factory-mcp",
      "env": {
        "ONEFACTORY_KEY": "your-api-key",
        "ONEFACTORY_ORG": "your-org-id"
      }
    }
  }
}
```

## Design Notes

See [`docs/PLAN.md`](docs/PLAN.md) for the architecture overview, per-tool filter sets, and pagination/rate-limit strategy.

The upstream OpenAPI spec spells the inspection-plan `is_tabulated` filter as `is_tablulated` (extra `l`). This server accepts both spellings from callers and forwards under the typo'd name the API actually requires.

## License

[MIT](LICENSE)
