"""Unit-Tests der Scoring-Engine. Testfälle: docs/scoring-spezifikation.md, Abschnitt Tests."""

import json
import re
from pathlib import Path

import pytest

from scoring.engine import aufbereiten, bewerte, lade_config

ROOT = Path(__file__).resolve().parents[1]
CONFIG = lade_config()


def profil(**werte):
    """Profil ohne Anforderungen (alles null). Tests setzen nur das geprüfte Feld."""
    felder = [
        "app_typ", "traffic_normal_min", "traffic_normal_max", "traffic_peak",
        "budget_chf_monat_max", "cpu_vcores_min", "ram_gb_min", "storage_gb_min",
        "docker_erforderlich", "ressourcentyp_min", "verwaltung_min",
        "skalierung_min", "backup_min", "support_min",
    ]
    p = dict.fromkeys(felder)
    p.update(werte)
    return p


def angebot(**werte):
    """Vollständiges VPS-Angebot. Tests überschreiben nur das geprüfte Feld."""
    a = {
        "anbieter": "Test", "produkt": "A", "url": None, "kategorie": "vps",
        "monatspreis_regulaer": 10.0, "waehrung": "CHF", "setup_gebuehr": 0,
        "abrechnungsintervall": "monatlich", "vertragslaufzeit_monate": 1,
        "cpu_vcores": 2, "ram_gb": 4, "storage_gb": 50, "bandbreite_mbit": 1000,
        "skalierung": 1, "backup": 1, "support": 1,
        "docker_support": True, "ressourcentyp": "vserver", "verwaltung": "selbst",
    }
    a.update(werte)
    return a


def gruende(ergebnis):
    """Ausschlussgründe des ersten ausgeschlossenen Angebots."""
    return {g["kriterium"] for g in ergebnis["ausgeschlossen"][0]["gruende"]}


def szenario(nr):
    """Referenzprofil und Erwartungswert aus docs/szenarien/szenario-<nr>.md."""
    text = (ROOT / "docs" / "szenarien" / f"szenario-{nr}.md").read_text()
    block = lambda titel: json.loads(
        re.search(rf"## {titel}\s*```json\n(.*?)```", text, re.S).group(1)
    )
    return block("Referenzprofil"), block("Erwartungswert")


# Rechenbeispiel aus dem Proposal (Kap. 4.5): Preis, RAM, CPU, Skalierung mit 0.4 / 0.3 / 0.2 / 0.1


def test_rechenbeispiel_proposal():
    config = {
        "gewichte": {"preis_chf_monat": 0.4, "ram_gb": 0.3, "cpu_vcores": 0.2, "skalierung": 0.1},
        "kategorie_defaults": CONFIG["kategorie_defaults"],
    }
    angebote = [
        angebot(produkt="A", monatspreis_regulaer=15, ram_gb=4, cpu_vcores=2, skalierung=0),
        angebot(produkt="B", monatspreis_regulaer=25, ram_gb=8, cpu_vcores=4, skalierung=1),
        angebot(produkt="C", monatspreis_regulaer=40, ram_gb=8, cpu_vcores=4, skalierung=1),
    ]
    ergebnis = bewerte(profil(), angebote, config)

    scores = {e["produkt"]: e["score"] for e in ergebnis["ranking"]}
    assert scores == pytest.approx({"A": 0.40, "B": 0.84, "C": 0.60})
    assert ergebnis["empfehlung"]["produkt"] == "B"
    for e in ergebnis["ranking"]:
        summe = sum(b["beitrag"] for b in e["beitraege"].values())
        assert summe == pytest.approx(e["score"], abs=1e-3)


# Preisregel: Setup-Gebühr auf 12 Monate verteilt


def test_preis_mit_setup():
    a = aufbereiten(angebot(monatspreis_regulaer=10, setup_gebuehr=24), CONFIG)
    assert a["preis_chf_monat"] == 12.00


# K.O. je Kriterium: ein Verstoss schliesst aus, Grund wird protokolliert


@pytest.mark.parametrize(
    "kriterium, anforderung, wert",
    [
        ("preis_chf_monat", {"budget_chf_monat_max": 25}, {"monatspreis_regulaer": 30}),
        ("ram_gb", {"ram_gb_min": 8}, {"ram_gb": 4}),
        ("storage_gb", {"storage_gb_min": 50}, {"storage_gb": 20}),
        ("docker_support", {"docker_erforderlich": True}, {"docker_support": False}),
        ("ressourcentyp", {"ressourcentyp_min": "dediziert"}, {"ressourcentyp": "vserver"}),
        ("verwaltung", {"verwaltung_min": "managed"}, {"verwaltung": "selbst"}),
        ("skalierung", {"skalierung_min": 2}, {"skalierung": 1}),
    ],
)
def test_ko_je_kriterium(kriterium, anforderung, wert):
    ergebnis = bewerte(profil(**anforderung), [angebot(**wert)], CONFIG)

    assert ergebnis["ranking"] == []
    assert ergebnis["empfehlung"] is None
    assert gruende(ergebnis) == {kriterium}


# Kategorie-Defaults: fehlende Felder erhalten den Wert ihrer Kategorie


@pytest.mark.parametrize(
    "kategorie, docker, verwaltung, ressourcentyp",
    [
        ("shared", False, "managed", "shared"),
        ("managed", False, "managed", "shared"),
        ("vps", True, "selbst", "vserver"),
        ("cloud", True, "selbst", "vserver"),
        ("dedicated", True, "selbst", "dediziert"),
    ],
)
def test_kategorie_defaults(kategorie, docker, verwaltung, ressourcentyp):
    roh = angebot(kategorie=kategorie, docker_support=None, verwaltung=None, ressourcentyp=None)
    a = aufbereiten(roh, CONFIG)

    assert (a["docker_support"], a["verwaltung"], a["ressourcentyp"]) == (docker, verwaltung, ressourcentyp)
    assert set(a["abgeleitete_felder"]) == {"docker_support", "verwaltung", "ressourcentyp"}


# Fehlende Werte: Preis und Kategorie schliessen aus, alle anderen nicht


def test_ohne_preis_ausschluss():
    ergebnis = bewerte(profil(), [angebot(monatspreis_regulaer=None)], CONFIG)
    assert gruende(ergebnis) == {"preis_fehlt"}


def test_ohne_kategorie_ausschluss():
    ergebnis = bewerte(profil(), [angebot(kategorie=None)], CONFIG)
    assert gruende(ergebnis) == {"kategorie_fehlend"}


def test_fehlender_wert_umverteilt():
    angebote = [angebot(produkt="A", cpu_vcores=None), angebot(produkt="B")]
    ergebnis = bewerte(profil(), angebote, CONFIG)
    a = next(e for e in ergebnis["ranking"] if e["produkt"] == "A")

    assert "cpu_vcores" in a["fehlende_felder"]
    assert "cpu_vcores" not in a["beitraege"]
    assert sum(b["gewicht"] for b in a["beitraege"].values()) == pytest.approx(1.0, abs=1e-3)
    assert "unvollstaendige_datenbasis" in a["flags"]


# Docker, Verwaltung und Ressourcentyp sind nach Stufe 0 nie null (Kategorie-Defaults).
@pytest.mark.parametrize(
    "feld, anforderung",
    [("ram_gb", {"ram_gb_min": 8}), ("storage_gb", {"storage_gb_min": 50}), ("skalierung", {"skalierung_min": 2})],
)
def test_fehlender_ko_wert_kein_ausschluss(feld, anforderung):
    ergebnis = bewerte(profil(**anforderung), [angebot(**{feld: None})], CONFIG)
    a = ergebnis["ranking"][0]

    assert feld in a["fehlende_felder"]
    assert "unvollstaendige_datenbasis" in a["flags"]


# Profilwert null (Variante B): keine Prüfung, Flag anforderung_unspezifiziert


def test_profil_null_keine_anforderung():
    verletzt_alles = angebot(monatspreis_regulaer=999, ram_gb=1, storage_gb=1, skalierung=0,
                             docker_support=False, ressourcentyp="shared", verwaltung="selbst")
    ergebnis = bewerte(profil(), [verletzt_alles], CONFIG)

    assert len(ergebnis["ranking"]) == 1
    assert "anforderung_unspezifiziert" in ergebnis["ranking"][0]["flags"]


def test_vollstaendiges_profil_ohne_flag():
    referenzprofil, _ = szenario(3)
    ergebnis = bewerte(referenzprofil, [angebot(ram_gb=8, storage_gb=50, backup=2)], CONFIG)

    assert "anforderung_unspezifiziert" not in ergebnis["ranking"][0]["flags"]


# Gleiche Werte: alle erhalten norm 1


def test_gleiche_werte_norm_1():
    angebote = [angebot(produkt=p, ram_gb=8) for p in ("A", "B", "C")]
    ergebnis = bewerte(profil(), angebote, CONFIG)

    assert all(e["beitraege"]["ram_gb"]["norm"] == 1 for e in ergebnis["ranking"])


# Ranking: Tie-Break und leeres Ergebnis


def test_tiebreak_preis_dann_anbieter():
    # Nur RAM gewichtet: alle Scores gleich, die Reihenfolge entscheidet allein der Tie-Break.
    config = {"gewichte": {"ram_gb": 1.0}, "kategorie_defaults": CONFIG["kategorie_defaults"]}
    angebote = [
        angebot(anbieter="B", monatspreis_regulaer=10),
        angebot(anbieter="A", monatspreis_regulaer=10),
        angebot(anbieter="C", monatspreis_regulaer=5),
    ]
    ergebnis = bewerte(profil(), angebote, config)

    assert [e["anbieter"] for e in ergebnis["ranking"]] == ["C", "A", "B"]


def test_kein_kandidat():
    angebote = [angebot(produkt="A"), angebot(produkt="B")]
    ergebnis = bewerte(profil(budget_chf_monat_max=5), angebote, CONFIG)

    assert ergebnis["empfehlung"] is None
    assert ergebnis["ranking"] == []
    assert len(ergebnis["ausgeschlossen"]) == 2


# Metrik: Anteil der Kandidaten mit unvollständiger Datenbasis


def test_anteil_unvollstaendig():
    angebote = [angebot(produkt="A", cpu_vcores=None), angebot(produkt="B")]
    ergebnis = bewerte(profil(), angebote, CONFIG)

    assert ergebnis["metriken"] == {"kandidaten": 2, "ausgeschlossen": 0, "anteil_unvollstaendig": 0.5}


# Basisszenarien: Referenzprofile S1–S3 gegen das Fixture-Set


@pytest.mark.parametrize("nr", [1, 2, 3])
def test_basisszenario(nr):
    referenzprofil, erwartung = szenario(nr)
    angebote = json.loads((ROOT / "tests" / "fixtures" / "angebote.json").read_text())["angebote"]
    ergebnis = bewerte(referenzprofil, angebote, CONFIG)

    assert ergebnis["empfehlung"]["kategorie"] in erwartung["kategorie_erwartet"]
    for e in ergebnis["ranking"]:
        assert e["kategorie"] not in erwartung["kategorien_ausgeschlossen"]
