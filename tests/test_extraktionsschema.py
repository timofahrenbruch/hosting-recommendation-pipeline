"""Extraktionsschema gegen Fixtures und Engine prüfen. Schema: scraping/extraction_schema.json."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scoring.engine import WERT_FELDER

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "scraping" / "extraction_schema.json").read_text())
FIXTURES = json.loads((ROOT / "tests" / "fixtures" / "angebote.json").read_text())["angebote"]


def validator(definition=None):
    """Validator für das ganze Schema oder eine Definition daraus (paket, angebot)."""
    if definition is None:
        schema = SCHEMA
    else:
        schema = {"$schema": SCHEMA["$schema"], "$defs": SCHEMA["$defs"], "$ref": f"#/$defs/{definition}"}
    return Draft202012Validator(schema)


def test_schema_ist_gueltig():
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda a: f"{a['anbieter']} {a['produkt']}")
def test_fixture_entspricht_schema(fixture):
    validator("angebot").validate(fixture)


def test_extraktionsausgabe_ohne_pipeline_felder():
    # Die Extraktion liefert anbieter und url nicht, die Pipeline ergänzt sie.
    pakete = [{k: v for k, v in a.items() if k not in ("anbieter", "url")} for a in FIXTURES]
    validator().validate({"angebote": pakete})


def test_engine_felder_im_schema():
    # Jedes Feld, das die Engine liest, muss die Extraktion liefern.
    gelesen = set(WERT_FELDER) | {"kategorie", "monatspreis_regulaer", "setup_gebuehr", "vertragslaufzeit_monate"}
    assert gelesen <= set(SCHEMA["$defs"]["paket"]["properties"])
