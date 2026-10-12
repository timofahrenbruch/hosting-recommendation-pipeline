"""Anbieterliste gegen Proposal-Scope und Fixtures prüfen. Liste: scraping/provider_list.json."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTE = json.loads((ROOT / "scraping" / "provider_list.json").read_text())["anbieter"]
FIXTURES = json.loads((ROOT / "tests" / "fixtures" / "angebote.json").read_text())["angebote"]
SCOPE = {"Hostpoint", "Infomaniak", "cyon", "IONOS", "STRATO", "All-Inkl", "Hetzner", "netcup", "Contabo", "DigitalOcean"}


def test_zehn_anbieter_laut_proposal():
    assert {a["name"] for a in LISTE} == SCOPE


def test_fixture_stammt_von_einer_seite_der_liste():
    # Jedes Fixture-Angebot stammt von einer Seite seines Anbieters mit derselben Kategorie und Verwaltung.
    seiten = {(a["name"], s["url"], s["kategorie"], s["verwaltung"]) for a in LISTE for s in a["seiten"]}
    for f in FIXTURES:
        assert (f["anbieter"], f["url"], f["kategorie"], f["verwaltung"]) in seiten, f"{f['anbieter']} {f['produkt']}"


def test_zwei_pakete_je_seite():
    # Auswahlregel: günstigstes und teuerstes Paket je Anbieter, Kategorie und Verwaltung.
    anzahl = Counter((f["anbieter"], f["kategorie"], f["verwaltung"]) for f in FIXTURES)
    assert all(n == 2 for n in anzahl.values()), {k: n for k, n in anzahl.items() if n != 2}
