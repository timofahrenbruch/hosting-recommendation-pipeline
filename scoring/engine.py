"""Scoring-Engine der Matching-Komponente.

Regeln: docs/scoring-spezifikation.md. Eine Funktion je Stufe:
  aufbereiten        Stufe 0  Preis, Kategorie-Defaults, Feldlisten
  ausschlussgruende  Stufe 1  K.O.-Filter
  bewerten           Stufe 2  Normalisierung und gewichteter Score
  bewerte            0–3      Gesamtablauf mit Ranking und Ausgabe

Reine Funktionen: kein I/O ausser lade_config, kein LLM, keine Zufälligkeit.
"""

import json
from pathlib import Path

CONFIG_PFAD = Path(__file__).with_name("config.json")

RANG_RESSOURCENTYP = {"shared": 0, "vserver": 1, "dediziert": 2}
KOSTEN_KRITERIEN = {"preis_chf_monat"}  # tiefer = besser, alle anderen höher = besser
# Verwaltung zuerst, weil der Docker-Default von ihr abhängt.
DEFAULT_FELDER = ("verwaltung", "docker_support", "ressourcentyp", "skalierung")
# Angebotsfelder aus K.O.-Filter und Bewertung. Fehlt eines, kommt es in fehlende_felder.
WERT_FELDER = (
    "cpu_vcores", "ram_gb", "storage_gb", "bandbreite_mbit",
    "skalierung", "backup", "support",
    "docker_support", "ressourcentyp", "verwaltung",
)
# K.O.-Kriterien mit Mindestwert: Angebotsfeld, Profilfeld. Ohne Angebotswert kein Ausschluss.
KO_MINDESTWERTE = (("ram_gb", "ram_gb_min"), ("storage_gb", "storage_gb_min"), ("skalierung", "skalierung_min"))
# Profilfelder, deren null das Flag anforderung_unspezifiziert auslöst. traffic_peak darf null sein.
PROFIL_FELDER = (
    "app_typ", "traffic_normal_min", "traffic_normal_max",
    "budget_chf_monat_max", "cpu_vcores_min", "ram_gb_min", "storage_gb_min",
    "docker_erforderlich", "ressourcentyp_min", "verwaltung_min",
    "skalierung_min", "backup_min", "support_min",
)


def lade_config(pfad=CONFIG_PFAD):
    """Gewichte und Kategorie-Defaults. Die Gewichte müssen sich auf 1.0 summieren."""
    config = json.loads(Path(pfad).read_text())
    summe = sum(config["gewichte"].values())
    if abs(summe - 1.0) > 1e-9:
        raise ValueError(f"Gewichte summieren sich auf {summe}, nicht auf 1.0")
    return config


# Stufe 0 — Aufbereitung


def aufbereiten(angebot, config):
    """Kopie des Angebots mit effektivem Monatspreis, Defaults und Feldlisten.

    Preis: (Setup + 12 × Monatspreis) / 12, Fremdwährung 1:1, gerundet auf Rappen.
    Defaults: nur für Felder, die null sind, je nach Kategorie. Verwaltete Server
    (verwaltung managed) bekommen Docker nur, wenn die Seite es nennt.
    """
    a = dict(angebot)

    monatspreis = a.get("monatspreis_regulaer")
    if monatspreis is None:
        a["preis_chf_monat"] = None
    else:
        setup = a.get("setup_gebuehr") or 0
        a["preis_chf_monat"] = round((setup + 12 * monatspreis) / 12, 2)

    a["abgeleitete_felder"] = []
    defaults = config["kategorie_defaults"].get(a.get("kategorie"), {})
    for feld in DEFAULT_FELDER:
        if a.get(feld) is None and feld in defaults:
            wert = defaults[feld]
            if feld == "docker_support" and a.get("verwaltung") == "managed":
                wert = False  # kein Root-Zugang
            a[feld] = wert
            a["abgeleitete_felder"].append(feld)

    a["fehlende_felder"] = [f for f in WERT_FELDER if a.get(f) is None]
    return a


# Stufe 1 — K.O.-Filter


def _grund(kriterium, profil=None, angebot=None):
    return {"kriterium": kriterium, "profil": profil, "angebot": angebot}


def ausschlussgruende(profil, a, config):
    """Alle K.O.-Verstösse eines aufbereiteten Angebots. Leere Liste = Kandidat.

    Profilwert null = keine Anforderung, Angebotswert null = durchlassen.
    Ausnahmen: ohne gültige Kategorie oder ohne Preis wird immer ausgeschlossen.
    """
    if a.get("kategorie") not in config["kategorie_defaults"]:
        return [_grund("kategorie_fehlend", angebot=a.get("kategorie"))]

    gruende = []
    preis = a["preis_chf_monat"]
    if preis is None:
        gruende.append(_grund("preis_fehlt"))

    budget = profil.get("budget_chf_monat_max")
    if budget is not None and preis is not None and preis > budget:
        gruende.append(_grund("preis_chf_monat", budget, preis))

    for kriterium, profilfeld in KO_MINDESTWERTE:
        minimum, wert = profil.get(profilfeld), a.get(kriterium)
        if minimum is not None and wert is not None and wert < minimum:
            gruende.append(_grund(kriterium, minimum, wert))

    if profil.get("docker_erforderlich") and a.get("docker_support") is False:
        gruende.append(_grund("docker_support", True, False))

    rtyp_min, rtyp = profil.get("ressourcentyp_min"), a.get("ressourcentyp")
    if rtyp_min not in (None, "egal") and rtyp is not None:
        if RANG_RESSOURCENTYP[rtyp] < RANG_RESSOURCENTYP[rtyp_min]:
            gruende.append(_grund("ressourcentyp", rtyp_min, rtyp))

    if profil.get("verwaltung_min") == "managed" and a.get("verwaltung") == "selbst":
        gruende.append(_grund("verwaltung", "managed", "selbst"))

    return gruende


# Stufe 2 — Bewertung


def _norm(kriterium, x, spanne):
    """Min-Max-Normalisierung auf 0–1. Alle Werte gleich → 1."""
    tief, hoch = spanne
    if hoch == tief:
        return 1.0
    if kriterium in KOSTEN_KRITERIEN:
        return (hoch - x) / (hoch - tief)
    return (x - tief) / (hoch - tief)


def bewerten(kandidaten, gewichte):
    """Setzt score und beitraege je Kandidat.

    min/max je Kriterium über die Kandidaten mit Wert. Fehlt einem Angebot ein Wert,
    entfällt das Kriterium und die übrigen Gewichte werden auf Summe 1 hochskaliert.
    """
    spannen = {}
    for k in gewichte:
        werte = [a[k] for a in kandidaten if a.get(k) is not None]
        if werte:
            spannen[k] = (min(werte), max(werte))

    for a in kandidaten:
        vorhanden = {k: w for k, w in gewichte.items() if a.get(k) is not None}
        summe = sum(vorhanden.values())
        a["beitraege"] = {}
        a["score"] = 0.0
        for k, w in vorhanden.items():
            norm = _norm(k, a[k], spannen[k])
            gewicht = w / summe
            a["beitraege"][k] = {"wert": a[k], "norm": norm, "gewicht": gewicht, "beitrag": gewicht * norm}
            a["score"] += gewicht * norm


# Stufe 3 — Ranking & Ausgabe


def _r(x):
    return round(x, 4)


def _ausgabe(a, flags):
    """Ranking-Eintrag, Zahlen auf 4 Stellen gerundet."""
    return {
        "anbieter": a.get("anbieter"),
        "produkt": a.get("produkt"),
        "url": a.get("url"),
        "kategorie": a.get("kategorie"),
        "score": _r(a["score"]),
        "beitraege": {
            k: {"wert": b["wert"], "norm": _r(b["norm"]), "gewicht": _r(b["gewicht"]), "beitrag": _r(b["beitrag"])}
            for k, b in a["beitraege"].items()
        },
        "vertragslaufzeit_monate": a.get("vertragslaufzeit_monate"),
        "abgeleitete_felder": a["abgeleitete_felder"],
        "fehlende_felder": a["fehlende_felder"],
        "flags": flags,
    }


def bewerte(profil, angebote, config):
    """Einstiegspunkt: Profil und Angebote rein, Empfehlung mit Ranking raus.

    Ranking: zuerst Angebote, deren geprüfte K.O.-Werte belegt sind, dann nach Score
    absteigend. Tie-Break tieferer Preis, dann Anbieter und Produkt.
    Ausgeschlossene alphabetisch nach Anbieter und Produkt. Das Ergebnis hängt so nicht
    von der Reihenfolge der Eingabe ab.
    """
    kandidaten, ausgeschlossen = [], []
    for roh in angebote:
        a = aufbereiten(roh, config)
        gruende = ausschlussgruende(profil, a, config)
        if gruende:
            ausgeschlossen.append({"anbieter": a.get("anbieter"), "produkt": a.get("produkt"), "gruende": gruende})
        else:
            kandidaten.append(a)

    ausgeschlossen.sort(key=lambda x: (x["anbieter"] or "", x["produkt"] or ""))
    bewerten(kandidaten, config["gewichte"])
    for a in kandidaten:
        # Ein K.O.-Wert, den das Profil prüft, aber die Seite nicht nennt.
        a["ko_unbelegt"] = [k for k, pf in KO_MINDESTWERTE if profil.get(pf) is not None and a.get(k) is None]
    kandidaten.sort(key=lambda a: (bool(a["ko_unbelegt"]), -a["score"], a["preis_chf_monat"],
                                   a.get("anbieter") or "", a.get("produkt") or ""))

    profil_unvollstaendig = any(profil.get(f) is None for f in PROFIL_FELDER)
    ranking = []
    for a in kandidaten:
        flags = []
        if a["fehlende_felder"]:
            flags.append("unvollstaendige_datenbasis")
        if a["ko_unbelegt"]:
            flags.append("ko_wert_unbelegt")
        if profil_unvollstaendig:
            flags.append("anforderung_unspezifiziert")
        ranking.append(_ausgabe(a, flags))

    empfehlung = None
    if ranking:
        empfehlung = {k: ranking[0][k] for k in ("anbieter", "produkt", "kategorie", "score")}

    unvollstaendig = sum("unvollstaendige_datenbasis" in e["flags"] for e in ranking)
    return {
        "empfehlung": empfehlung,
        "ranking": ranking,
        "ausgeschlossen": ausgeschlossen,
        "metriken": {
            "kandidaten": len(ranking),
            "ausgeschlossen": len(ausgeschlossen),
            "anteil_unvollstaendig": round(unvollstaendig / len(ranking), 2) if ranking else 0.0,
        },
    }
