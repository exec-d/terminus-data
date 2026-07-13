"""Agrégations pures de ponctualité (sans dépendance GTFS-RT/protobuf).

Isolé de collect.py pour être testable sans le flux : trend quotidien honnête,
agrégat par gare, fusion des arrêts, extraction du code UIC.
"""

import re

ON_TIME_S = 300  # seuil SNCF : à l'heure si retard final <= 5 min

_UIC_RE = re.compile(r"(\d{7,8})")


def uic_of(raw_id):
    """Code UIC (7-8 chiffres) d'un identifiant d'arrêt/gare, ou None."""
    if not raw_id:
        return None
    m = _UIC_RE.search(raw_id)
    return m.group(1) if m else None


def daily_trend_point(day):
    """Point de tendance honnête pour une journée d'historique.

    Une suppression compte comme non-à-l'heure (jamais exclue du dénominateur).
    onTimePct = trains ayant circulé avec finalDelayS <= 300, sur TOUS les trains.
    """
    trains = day.get("trains", {})
    obs = len(trains)
    if not obs:
        return {"date": day["date"], "obs": 0, "onTimePct": 0, "cancelledPct": 0}
    cancelled = sum(1 for r in trains.values() if r.get("cancelled"))
    on_time = sum(
        1
        for r in trains.values()
        if not r.get("cancelled")
        and r.get("finalDelayS") is not None
        and r["finalDelayS"] <= ON_TIME_S
    )
    return {
        "date": day["date"],
        "obs": obs,
        "onTimePct": round(100 * on_time / obs),
        "cancelledPct": round(100 * cancelled / obs),
    }


def merge_stops(a, b):
    """Fusionne deux listes d'arrêts {uic, delayS, skipped} par uic (idempotent)."""
    merged = {}
    for s in list(a) + list(b):
        cur = merged.get(s["uic"])
        if cur is None:
            merged[s["uic"]] = {"uic": s["uic"], "delayS": s.get("delayS"), "skipped": bool(s.get("skipped"))}
        else:
            if s.get("delayS") is not None:
                cur["delayS"] = s["delayS"]
            cur["skipped"] = cur["skipped"] or bool(s.get("skipped"))
    return [merged[k] for k in sorted(merged)]


def _median(values):
    vs = sorted(values)
    return vs[len(vs) // 2] if vs else None


def _mean(values):
    return round(sum(values) / len(values)) if values else None


def station_order(line32):
    """Ordre géographique {uic: index} le long de la ligne, d'après le trajet ALLER
    (bebToLyon) le plus complet de line32.json — ses arrêts sont dans l'ordre `seq`.
    Le tableau `stations` de line32.json n'est PAS trié géographiquement, d'où ce calcul."""
    best = []
    for t in line32.get("trips", []):
        if t.get("direction") == "bebToLyon":
            stops = sorted(t.get("stops", []), key=lambda s: s.get("seq", 0))
            if len(stops) > len(best):
                best = stops
    order = {}
    for s in best:
        u = uic_of(s.get("stationId"))
        if u and u not in order:
            order[u] = len(order)
    return order


def aggregate_stations(days, station_ref, order_by_uic):
    """Agrège le retard par gare, rangé par ordre géographique (`order_by_uic`, cf.
    station_order). Retard médian ET moyen : la médiane reste souvent à 0 (majorité de
    passages à l'heure) alors que la moyenne capte les à-coups (retards de la queue)."""
    delays, skips, obs = {}, {}, {}
    for day in days:
        for rec in day.get("trains", {}).values():
            for s in rec.get("stops", []):
                u = s["uic"]
                obs[u] = obs.get(u, 0) + 1
                if s.get("skipped"):
                    skips[u] = skips.get(u, 0) + 1
                elif s.get("delayS") is not None:
                    delays.setdefault(u, []).append(s["delayS"])
    end = len(order_by_uic)
    rows = []
    for station in station_ref:
        u = uic_of(station["id"])
        n = obs.get(u, 0)
        rows.append({
            "uic": u,
            "name": station["name"],
            "order": order_by_uic.get(u, end),  # gares hors trajet retenu → en fin
            "obs": n,
            "medianDelayS": _median(delays.get(u, [])),
            "meanDelayS": _mean(delays.get(u, [])),
            "skippedPct": round(100 * skips.get(u, 0) / n) if n else 0,
        })
    rows.sort(key=lambda r: (r["order"], r["name"]))
    for i, r in enumerate(rows):  # ordre final propre 0..N après tri géographique
        r["order"] = i
    return rows
