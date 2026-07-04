#!/usr/bin/env python3
"""Collecte de ponctualité de la ligne 32 depuis le GTFS-RT SNCF.

Échantillonne le flux national TripUpdates, filtre les trains de la ligne 32
(numéros extraits de line32.json, présent à la racine du dépôt), fusionne
l'observation dans history/<date>.json (clé = date de service du trip, ce qui
rend les runs idempotents et permet au run du matin de rattraper la veille),
puis recalcule stats/line32.json sur une fenêtre glissante.

Le flux est un instantané : il retient la journée de service en cours (retards
finaux des trains déjà arrivés inclus), d'où un échantillonnage 3×/jour au lieu
d'un polling continu.
"""

import json
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.transit import gtfs_realtime_pb2

ROOT = Path(__file__).resolve().parent.parent
FEED_URL = "https://proxy.transport.data.gouv.fr/resource/sncf-gtfs-rt-trip-updates"
TRAIN_RE = re.compile(r"OCESN(\d+)")
ON_TIME_S = 300  # seuil SNCF : à l'heure si retard final <= 5 min
WINDOW_DAYS = 60


def train_number(trip_id):
    m = TRAIN_RE.search(trip_id)
    return m.group(1) if m else None


def load_line32_numbers():
    data = json.loads((ROOT / "line32.json").read_text())
    return {n for t in data["trips"] if (n := train_number(t["tripId"]))}


def fetch_feed():
    feed = gtfs_realtime_pb2.FeedMessage()
    with urllib.request.urlopen(FEED_URL, timeout=60) as r:
        feed.ParseFromString(r.read())
    return feed


def observe(feed, numbers):
    """Une observation par train de la ligne, groupée par date de service."""
    obs = {}
    for e in feed.entity:
        if not e.HasField("trip_update"):
            continue
        tu = e.trip_update
        num = train_number(tu.trip.trip_id)
        if num not in numbers or not tu.trip.start_date:
            continue
        cancelled = tu.trip.schedule_relationship == tu.trip.CANCELED
        final_delay, max_delay, skipped = None, 0, 0
        for stu in tu.stop_time_update:
            if stu.schedule_relationship == stu.SKIPPED:
                skipped += 1
                continue
            ev = stu.arrival if stu.HasField("arrival") else stu.departure
            if ev.HasField("delay"):
                final_delay = ev.delay  # les STU sont ordonnés : le dernier = terminus
                max_delay = max(max_delay, ev.delay)
        obs.setdefault(tu.trip.start_date, {})[num] = {
            "finalDelayS": final_delay,
            "maxDelayS": max_delay,
            "skippedStops": skipped,
            "cancelled": cancelled,
        }
    return obs


def merge_history(obs, now_iso):
    hist = ROOT / "history"
    hist.mkdir(exist_ok=True)
    for date, trains in obs.items():
        iso = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        path = hist / f"{iso}.json"
        day = (
            json.loads(path.read_text())
            if path.exists()
            else {"date": iso, "samples": [], "trains": {}}
        )
        day["samples"].append(now_iso)
        for num, rec in trains.items():
            old = day["trains"].get(num)
            if old:
                # Le sample le plus tardif a vu le train plus avancé : son retard
                # final prime s'il existe ; les autres champs se cumulent.
                rec = {
                    "finalDelayS": rec["finalDelayS"] if rec["finalDelayS"] is not None else old["finalDelayS"],
                    "maxDelayS": max(old["maxDelayS"], rec["maxDelayS"]),
                    "skippedStops": max(old["skippedStops"], rec["skippedStops"]),
                    "cancelled": old["cancelled"] or rec["cancelled"],
                }
            day["trains"][num] = rec
        path.write_text(json.dumps(day, indent=1, sort_keys=True) + "\n")


def compute_stats(now_iso):
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=WINDOW_DAYS)
    per_train, days = {}, 0
    for path in sorted((ROOT / "history").glob("*.json")):
        if datetime.strptime(path.stem, "%Y-%m-%d").date() < cutoff:
            continue
        days += 1
        for num, rec in json.loads(path.read_text())["trains"].items():
            per_train.setdefault(num, []).append(rec)

    trains = {}
    for num, recs in sorted(per_train.items()):
        cancelled = sum(1 for r in recs if r["cancelled"])
        delays = sorted(
            r["finalDelayS"] for r in recs if r["finalDelayS"] is not None and not r["cancelled"]
        )
        entry = {"obs": len(recs), "cancelledPct": round(100 * cancelled / len(recs))}
        if delays:
            entry["onTimePct"] = round(100 * sum(1 for d in delays if d <= ON_TIME_S) / len(delays))
            entry["medianDelayMin"] = round(delays[len(delays) // 2] / 60)
            entry["maxDelayMin"] = round(max(delays) / 60)
        trains[num] = entry

    stats_dir = ROOT / "stats"
    stats_dir.mkdir(exist_ok=True)
    (stats_dir / "line32.json").write_text(
        json.dumps(
            {
                "meta": {
                    "updatedAt": now_iso,
                    "windowDays": WINDOW_DAYS,
                    "daysWithData": days,
                    "onTimeThresholdMin": ON_TIME_S // 60,
                },
                "trains": trains,
            },
            indent=1,
            sort_keys=True,
        )
        + "\n"
    )


def main():
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    numbers = load_line32_numbers()
    obs = observe(fetch_feed(), numbers)
    seen = sum(len(t) for t in obs.values())
    print(f"trains ligne 32 dans le flux : {seen} (dates de service : {sorted(obs)})")
    merge_history(obs, now_iso)
    compute_stats(now_iso)
    print("history/ et stats/line32.json à jour")


if __name__ == "__main__":
    main()
