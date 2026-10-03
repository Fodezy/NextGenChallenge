"""Fake CRM payloads and transports, shaped exactly like backend/crm-service.mjs."""

import asyncio
import copy
from collections.abc import Callable

import httpx

RETRIEVED_AT = "2026-10-03T10:00:00.000Z"

_ACCOUNTS = {
    "abc123": [
        {
            "acct_ref": "P-9001",
            "acct_nickname": "Taxable Brokerage",
            "curr_val": {"amt": 48930, "ccy": "CAD"},
            "chg_1d": {"amt": 30, "pct": 30 / 48900},
            "since_inception_pct": 0.187,
        },
        {
            "acct_ref": "P-9002",
            "acct_nickname": "Retirement Account",
            "curr_val": {"amt": 500, "ccy": "CAD"},
            "chg_1d": {"amt": 500, "pct": 0},
            "since_inception_pct": 0.25,
        },
        {
            "acct_ref": "P-EMPTY",
            "acct_nickname": "Empty Account",
            "curr_val": {"amt": 0, "ccy": "CAD"},
            "chg_1d": {"amt": 0, "pct": 0},
            "since_inception_pct": 0,
        },
    ],
}
_CLIENT_OF = {"P-9001": "abc123", "P-9002": "abc123", "P-EMPTY": "abc123"}


def crm_payload(portfolio_id: str, mode: str = "ok") -> dict:
    """A successful CRM body for a known id, in mode ok, nested or missing."""
    client_id = _CLIENT_OF[portfolio_id]
    accounts = copy.deepcopy(_ACCOUNTS[client_id])
    record: dict = {"client_id": client_id, "full_name": "Jane Doe", "accounts": accounts}
    if mode == "missing":
        account = next(a for a in accounts if a["acct_ref"] == portfolio_id)
        account["curr_val"]["amt"] = None
        del account["acct_nickname"]
    if mode == "nested":
        del record["accounts"]
        record["relationships"] = {"accounts": accounts}
    return {
        "client_record": record,
        "meta": {"retrieved_at": RETRIEVED_AT, "source": "legacy-crm-v2"},
    }


Handler = Callable[[httpx.Request], httpx.Response]


def ok_handler(mode: str = "ok") -> Handler:
    """Behaves like the mock: known ids → payload, unknown → 404."""

    def handle(request: httpx.Request) -> httpx.Response:
        portfolio_id = request.url.path.rsplit("/", 1)[-1]
        if portfolio_id not in _CLIENT_OF:
            body = {"error": "unknown_account", "message": "No CRM account has this reference."}
            return httpx.Response(404, json=body)
        return httpx.Response(200, json=crm_payload(portfolio_id, mode))

    return handle


def status_handler(status: int) -> Handler:
    def handle(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": "legacy_unavailable", "message": "Simulated"})

    return handle


def slow_handler(seconds: float = 10.0):
    """Like the mock's timeout mode: waits, then 504."""

    async def handle(_: httpx.Request) -> httpx.Response:
        await asyncio.sleep(seconds)
        return httpx.Response(504, json={"error": "legacy_timeout", "message": "Too slow"})

    return handle


def fake_http(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url="http://crm.test", transport=httpx.MockTransport(handler))
