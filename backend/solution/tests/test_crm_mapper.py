"""Task 1 · R1: map the CRM's legacy shape into our schema (pure, no HTTP)."""

import pytest

from app.schemas import PortfolioMetadata
from app.services.crm_errors import CrmNotFoundError, CrmUnavailableError
from app.services.crm_mapper import ACCOUNT_LIST_PATHS, FIELD_PATHS, map_portfolio
from tests.crm_fakes import RETRIEVED_AT, crm_payload


def test_ok_shape_maps_all_fields():
    result = map_portfolio(crm_payload("P-9001"), "P-9001")

    assert result.model_dump() == {
        "portfolio_id": "P-9001",
        "client_id": "abc123",
        "client_name": "Jane Doe",
        "label": "Taxable Brokerage",
        "currency": "CAD",
        "total_market_value": 48930,
        "day_change_amount": 30,
        "day_change_percent": pytest.approx(30 / 48900),
        "total_return_since_inception": 0.187,
        "as_of": RETRIEVED_AT,
    }


def test_nested_shape_maps_same_as_ok():
    nested = map_portfolio(crm_payload("P-9001", "nested"), "P-9001")

    assert nested == map_portfolio(crm_payload("P-9001"), "P-9001")


def test_picks_account_by_acct_ref_not_first():
    result = map_portfolio(crm_payload("P-9002"), "P-9002")

    assert result.portfolio_id == "P-9002"
    assert result.label == "Retirement Account"
    assert result.total_market_value == 500


def test_missing_mode_maps_null_amount_and_absent_nickname_to_none():
    result = map_portfolio(crm_payload("P-9001", "missing"), "P-9001")

    assert result.total_market_value is None
    assert result.label is None
    assert result.currency == "CAD"
    assert result.day_change_amount == 30


def test_missing_or_blank_full_name_maps_to_none():
    raw = crm_payload("P-9001")
    del raw["client_record"]["full_name"]
    assert map_portfolio(raw, "P-9001").client_name is None

    raw["client_record"]["full_name"] = "   "
    assert map_portfolio(raw, "P-9001").client_name is None


def test_null_or_absent_nested_objects_map_to_none():
    raw = crm_payload("P-9001")
    account = raw["client_record"]["accounts"][0]
    account["curr_val"] = None
    del account["chg_1d"]
    del raw["meta"]

    result = map_portfolio(raw, "P-9001")

    assert result.total_market_value is None
    assert result.currency is None
    assert result.day_change_amount is None
    assert result.day_change_percent is None
    assert result.as_of is None
    assert result.label == "Taxable Brokerage"


def test_zero_values_stay_zero_not_none():
    result = map_portfolio(crm_payload("P-EMPTY"), "P-EMPTY")

    assert result.total_market_value == 0
    assert result.day_change_percent == 0


def test_field_paths_table_takes_an_alternative_name_and_first_match_wins():
    """A new legacy name is one line in the table, not new logic."""
    paths = {**FIELD_PATHS, "label": (*FIELD_PATHS["label"], "account.nickname")}
    raw = crm_payload("P-9001")
    account = raw["client_record"]["accounts"][0]
    del account["acct_nickname"]
    account["nickname"] = "Legacy Name"

    assert map_portfolio(raw, "P-9001", field_paths=paths).label == "Legacy Name"

    account["acct_nickname"] = "Taxable Brokerage"
    assert map_portfolio(raw, "P-9001", field_paths=paths).label == "Taxable Brokerage"


def test_default_table_covers_every_output_field_and_both_account_locations():
    assert set(FIELD_PATHS) == set(PortfolioMetadata.model_fields) - {"portfolio_id"}
    assert ACCOUNT_LIST_PATHS == (
        "client_record.accounts",
        "client_record.relationships.accounts",
    )


@pytest.mark.parametrize(
    ("amt", "expected"),
    [("48930.12", 48930.12), (" 48930 ", 48930.0), ("n/a", None), ("", None), (True, None)],
)
def test_numeric_strings_become_numbers_and_unreadable_values_none(amt, expected):
    raw = crm_payload("P-9001")
    raw["client_record"]["accounts"][0]["curr_val"]["amt"] = amt

    assert map_portfolio(raw, "P-9001").total_market_value == expected


def test_lowercase_currency_is_uppercased():
    raw = crm_payload("P-9001")
    raw["client_record"]["accounts"][0]["curr_val"]["ccy"] = " cad "

    assert map_portfolio(raw, "P-9001").currency == "CAD"


def test_client_found_but_no_matching_acct_ref_raises_not_found():
    with pytest.raises(CrmNotFoundError):
        map_portfolio(crm_payload("P-9001"), "P-NOPE")


@pytest.mark.parametrize(
    "raw",
    [
        {"meta": {}},
        {"client_record": None},
        {"client_record": {"client_id": "abc123"}},
        {"client_record": {"accounts": "not a list"}},
        [],
    ],
    ids=["no-record", "null-record", "no-accounts", "accounts-not-list", "not-an-object"],
)
def test_unrecognised_shape_raises_crm_unavailable(raw):
    with pytest.raises(CrmUnavailableError):
        map_portfolio(raw, "P-9001")
