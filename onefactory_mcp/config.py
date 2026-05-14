import os


ENV_BASE_URLS = {
    "prod": "https://www.1factory.com/api/v1",
    "sandbox": "https://www.1factory.co/api/v1",
    "val-prod": "https://val.1factory.com/api/v1",
    "val-sandbox": "https://val.1factory.co/api/v1",
    "local": "http://localhost:3000/api/v1",
}


def get_api_key() -> str:
    key = os.environ.get("ONEFACTORY_KEY", "")
    if not key:
        raise ValueError("ONEFACTORY_KEY environment variable is required")
    return key


def get_org_id() -> str:
    org = os.environ.get("ONEFACTORY_ORG", "")
    if not org:
        raise ValueError("ONEFACTORY_ORG environment variable is required")
    return org


def get_base_url() -> str:
    env = os.environ.get("ONEFACTORY_ENV", "prod")
    if env not in ENV_BASE_URLS:
        valid = ", ".join(sorted(ENV_BASE_URLS))
        raise ValueError(
            f"ONEFACTORY_ENV={env!r} is not valid; must be one of: {valid}"
        )
    return ENV_BASE_URLS[env]


def get_headers() -> dict[str, str]:
    return {
        "x-1factory-key": get_api_key(),
        "x-1factory-org": get_org_id(),
        "Accept-Encoding": "gzip, deflate",
    }
