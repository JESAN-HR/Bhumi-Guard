from copy import deepcopy
from decimal import Decimal
import pytest
from backend.app.rules import analyze, number
from backend.app.fixtures import scenarios


@pytest.mark.parametrize("s", scenarios(), ids=lambda s: s["id"])
def test_labeled_scenarios(s):
    outcome, findings = analyze(
        s["fields"], s["holding"], s["transfers"], s["mutation"], ["DEMO-RECORDS"]
    )
    assert set(f["code"] for f in findings) == set(s["expected"])
    assert outcome == (
        "conflict"
        if any(f["priority"] == "conflict" for f in findings)
        else "insufficient" if findings else "clear"
    )
    assert all(
        f["sources"] and f["explanation"]["bn"] and f["action"]["bn"] for f in findings
    )


def test_decimal_digits():
    assert number("০.১") + number("0.2") == Decimal("0.3")


@pytest.mark.parametrize(
    "n", ["NaN", "Infinity", "-1", "1.0000001", "1000000000", "bad"]
)
def test_reject_invalid_numbers(n):
    with pytest.raises(ValueError):
        number(n)


def test_same_dag_other_mouza_is_not_same_parcel():
    s = scenarios()[0]
    s["fields"]["mouza_id"] = "loc-uttar-paragao"
    s["fields"]["area"] = "200"
    _, f = analyze(s["fields"], s["holding"], [], s["mutation"], ["demo"])
    assert [x["code"] for x in f] == ["AMBIGUOUS_IDENTITY"]


def test_proposal_not_double_counted():
    s = scenarios()[0]
    s["fields"]["area"] = "100"
    s["fields"]["transfer_id"] = "proposal"
    ts = [
        dict(
            id="proposal",
            holding_id="DEMO-HOLDING",
            document_id="demo",
            area="100",
            date="2026-09-01",
            status="completed",
        )
    ]
    assert analyze(s["fields"], s["holding"], ts, s["mutation"], ["demo"])[0] == "clear"


def test_other_holding_excluded():
    s = scenarios()[0]
    ts = [
        dict(
            id="other",
            holding_id="OTHER",
            document_id="demo",
            area="999",
            date="2026-01-01",
            status="completed",
        )
    ]
    assert analyze(s["fields"], s["holding"], ts, s["mutation"], ["demo"])[0] == "clear"


def test_languages_identical():
    s = scenarios()[0]
    s["fields"]["area"] = "১০১.৫"
    a = analyze(s["fields"], s["holding"], [], s["mutation"], ["demo"])
    s["fields"]["area"] = "101.5"
    assert a == analyze(s["fields"], s["holding"], [], s["mutation"], ["demo"])
