# Vessel Gigantism · Three decades of growing ships

Interactive explorer of **average vessel size per port call** at major European ports,
1997 → present, by ship type. Built on official **Eurostat** maritime statistics
(dataset `mar_tf_qm`, "Vessels arriving in the main ports by type and size of vessels",
quarterly at source, aggregated to calendar years). No backend, no API key, no build
step at deploy time: one HTML file, one JSON file, Chart.js from CDN.

## The story

- EU-27 container arrivals **fell 19%** between 2005 and 2024 while the average
  container ship per call **more than doubled** (16,892 → 38,575 GT): fewer ships,
  bigger ships.
- The effect is heterogeneous: Gdansk grew **×11.8** (feeder to deep-water hub),
  Algeciras ×5.4, Hamburg ×4.2 with 43% fewer container calls.
- Cruise is the counter-example: EU arrivals nearly doubled **and** the average ship
  grew ×2.9. Container consolidates, cruise multiplies.

## What you can do

- **Automatic highlights** computed live from the data
- **GT per call time series** for any combination of 18 ports + the EU-27 aggregate,
  by ship type (container, tanker, dry bulk, cruise…)
- **Fewer ships, bigger ships**: arrivals (bars) against average size (line) for a
  focus port
- **Who grew the most**: ranking of growth multiples, earliest complete year → latest
- **Container vs cruise** indexed contrast for the EU-27
- **Thirty-year ledger table**: size then and now, growth multiple, arrivals change

## Files

| File | Purpose |
|---|---|
| `index.html` | The app (single file) |
| `data.json` | Annual arrivals and GT/call per port and ship type |
| `build_data.py` | Reproducible pipeline: Eurostat API → `data.json` |

## Method

Average vessel size per call = annual gross tonnage (thousand GT × 1000) ÷ annual
arrivals, per port and ship type, all size classes. A calendar year is included only
when the port reported **all four quarters in both units**. GT measures ship volume,
not cargo carried. Antwerpen/Antwerp-Bruges and Le Havre/HAROPA are kept as separate
series because the reporting perimeter changed in 2022.

## Refresh the data

```bash
python3 build_data.py   # rewrites data.json from the live Eurostat API
```

## Deploy

Static site: push to GitHub and import in Vercel (or `vercel --prod`). No settings needed.

## Citation

See `CITATION.cff`. Data © European Union, Eurostat, reused under the
[Eurostat open data policy](https://ec.europa.eu/eurostat/about-us/policies/copyright).

Developed by [Darliane Ribeiro Cunha, PhD](https://cunha-data-science.vercel.app/).
