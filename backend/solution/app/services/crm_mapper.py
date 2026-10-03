"""Maps the CRM's legacy shape into PortfolioMetadata (BRIEF.md R1, A3, A8). Pure, no I/O.

Every output field has a list of candidate paths; the first one with a value wins. A new legacy
name or nesting is one more path in the table, not new logic. Paths starting with "account." are
read from the matched account; all others from the top of the CRM response.
"""

import math
from collections.abc import Callable, Mapping
from typing import Any

from app.schemas import PortfolioMetadata
from app.services.crm_errors import CrmNotFoundError, CrmUnavailableError

ACCOUNT_LIST_PATHS: tuple[str, ...] = (
    "client_record.accounts",
    "client_record.relationships.accounts",
)
ACCOUNT_REF_PATHS: tuple[str, ...] = ("account.acct_ref",)

FIELD_PATHS: dict[str, tuple[str, ...]] = {
    "client_id": ("client_record.client_id",),
    "client_name": ("client_record.full_name",),
    "label": ("account.acct_nickname",),
    "currency": ("account.curr_val.ccy",),
    "total_market_value": ("account.curr_val.amt",),
    "day_change_amount": ("account.chg_1d.amt",),
    "day_change_percent": ("account.chg_1d.pct",),
    "total_return_since_inception": ("account.since_inception_pct",),
    "as_of": ("meta.retrieved_at",),
}

_MISSING = object()


def _lookup(source: Any, path: str) -> Any:
    value = source
    for key in path.split("."):
        if not isinstance(value, Mapping) or key not in value:
            return _MISSING
        value = value[key]
    return value


def _first(paths: tuple[str, ...], payload: Any, account: Any) -> Any:
    for path in paths:
        if path.startswith("account."):
            value = _lookup(account, path.removeprefix("account."))
        else:
            value = _lookup(payload, path)
        if value is not _MISSING and value is not None:
            return value
    return None


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        number = float(value)
    elif isinstance(value, str):
        try:
            number = float(value.strip())
        except ValueError:
            return None
    else:
        return None
    return number if math.isfinite(number) else None


def _text(value: Any) -> str | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _currency(value: Any) -> str | None:
    text = _text(value)
    return text.upper() if text else None


_CONVERTERS: dict[str, Callable[[Any], Any]] = {
    "currency": _currency,
    "total_market_value": _number,
    "day_change_amount": _number,
    "day_change_percent": _number,
    "total_return_since_inception": _number,
}


def map_portfolio(
    raw: Any,
    portfolio_id: str,
    field_paths: Mapping[str, tuple[str, ...]] = FIELD_PATHS,
) -> PortfolioMetadata:
    """Find the account whose ref is portfolio_id and map it. Missing values become None.

    Raises CrmUnavailableError if no accounts list can be found (A3) and CrmNotFoundError if the
    list has no account with this ref.
    """
    accounts = next(
        (found for path in ACCOUNT_LIST_PATHS if isinstance(found := _lookup(raw, path), list)),
        None,
    )
    if accounts is None:
        raise CrmUnavailableError("unrecognised CRM response shape")

    account = next(
        (
            acct
            for acct in accounts
            if isinstance(acct, Mapping)
            and _text(_first(ACCOUNT_REF_PATHS, raw, acct)) == portfolio_id
        ),
        None,
    )
    if account is None:
        raise CrmNotFoundError(portfolio_id)

    values = {
        field: _CONVERTERS.get(field, _text)(_first(paths, raw, account))
        for field, paths in field_paths.items()
    }
    return PortfolioMetadata(portfolio_id=portfolio_id, **values)
