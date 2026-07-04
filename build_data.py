#!/usr/bin/env python3
"""
Vessel Gigantism Explorer - data pipeline
Pulls Eurostat mar_tf_qm ("Vessels arriving in the main ports by type and size
of vessels - quarterly data") and computes, per port and ship type, the annual
number of arrivals and the mean gross tonnage per arrival (GT/call), 1997-present.

Method
- GT/call = (sum of quarterly GT, thousands x 1000) / (sum of quarterly arrivals)
- A calendar year is included only when the port reported all four quarters
  for that ship type in BOTH units (arrivals and GT).
- tonnage dimension fixed at TOTAL (all size classes).

Output: data.json (consumed by index.html)

No API key required. Re-run at any time to refresh.
"""
import json
import urllib.request
from datetime import date

API = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/"
       "data/mar_tf_qm?format=JSON&lang=en&tonnage=TOTAL")

# rep_mar codes -> display name. Antwerpen/Antwerp-Bruges and Le Havre/HAROPA
# changed reporting entity in 2022 and are kept as separate series.
PORTS = {
    "EU27_2020": "European Union (EU-27)",
    "NL_0NLRTM": "Rotterdam",
    "BE_0BEANR": "Antwerpen (to 2021)",
    "BE_0BE003": "Antwerp-Bruges (from 2022)",
    "DE_1DEHAM": "Hamburg",
    "DE_1DEBRV": "Bremerhaven",
    "ES_2ESVLC": "Valencia",
    "ES_2ESALG": "Algeciras",
    "ES_2ESBCN": "Barcelona",
    "EL_0GRPIR": "Piraeus",
    "IT_0ITGOA": "Genova",
    "IT_0ITGIT": "Gioia Tauro",
    "FR_2FRMRS": "Marseille",
    "FR_1FRLEH": "Le Havre (to 2021)",
    "FR_1FR001": "HAROPA (from 2022)",
    "PL_0PLGDN": "Gdansk",
    "SI_0SIKOP": "Koper",
    "PT_0PTSIE": "Sines",
    "RO_0ROCND": "Constanta",
}

VESSEL_LABELS = {
    "TOTAL": "All ship types",
    "ODC_CNT": "Container ship",
    "LBK": "Liquid bulk tanker",
    "DBK": "Dry bulk carrier",
    "ODC_GEN": "General cargo",
    "ODC_SPE": "Specialised carrier",
    "ODC_PCRU": "Cruise ship",
    "ODC_PAS_XCR": "Passenger (excl. cruise)",
    "MSC_OFF": "Offshore vessel",
    "MSC_TOW": "Tug / pusher",
}


def fetch():
    url = API + "".join(f"&rep_mar={c}" for c in PORTS)
    print("Fetching", url[:110], "...")
    with urllib.request.urlopen(url, timeout=180) as r:
        return json.load(r)


def cell_getter(d):
    dims = d["id"]
    sizes = [len(d["dimension"][k]["category"]["index"]) for k in dims]
    idx = {k: d["dimension"][k]["category"]["index"] for k in dims}
    val = d["value"]

    def get(vessel, unit, rep, t):
        coord = {"freq": 0, "tonnage": 0,
                 "vessel": idx["vessel"].get(vessel),
                 "unit": idx["unit"].get(unit),
                 "rep_mar": idx["rep_mar"].get(rep),
                 "time": idx["time"].get(t)}
        if None in coord.values():
            return None
        pos = 0
        for k, s in zip(dims, sizes):
            pos = pos * s + coord[k]
        return val.get(str(pos))

    return get, list(d["dimension"]["time"]["category"]["index"].keys())


def build():
    d = fetch()
    get, times = cell_getter(d)
    years = sorted({t[:4] for t in times})
    series = {}
    for rep in PORTS:
        for vessel in VESSEL_LABELS:
            s = {}
            for y in years:
                qs = [t for t in times if t.startswith(y)]
                if len(qs) < 4:
                    continue  # current year, incomplete by definition
                nr = [get(vessel, "NR", rep, t) for t in qs]
                gt = [get(vessel, "THS_GT", rep, t) for t in qs]
                if any(v is None for v in nr + gt) or sum(nr) == 0 or sum(gt) == 0:
                    continue  # require all four quarters in both units, GT > 0
                s[y] = [sum(nr), round(sum(gt) * 1000 / sum(nr))]
            if len(s) >= 2:
                series.setdefault(rep, {})[vessel] = s

    out = {
        "meta": {
            "source": "Eurostat, dataset mar_tf_qm (tonnage class: TOTAL)",
            "dataset_url": ("https://ec.europa.eu/eurostat/databrowser/view/"
                            "mar_tf_qm/default/table?lang=en"),
            "extracted": date.today().isoformat(),
            "method": ("GT/call = annual gross tonnage / annual arrivals; "
                       "only calendar years with all four quarters reported "
                       "in both units are included."),
        },
        "ports": PORTS,
        "vessels": VESSEL_LABELS,
        "series": series,
    }
    with open("data.json", "w") as f:
        json.dump(out, f, separators=(",", ":"))
    n = sum(len(v) for p in series.values() for v in p.values())
    print(f"data.json written: {len(series)} ports, {n} port-type-year points")


if __name__ == "__main__":
    build()
