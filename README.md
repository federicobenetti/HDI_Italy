# Italian Provincial HDI Toolkit

A compact toolkit to build an HDI-style index for Italian **provinces** and **regions**: 
from wide Excel tables → tidy data → standardized territory names → coverage/gap diagnostics with a Plotly heatmap.

## Features
- Convert multi-sheet Excel workbooks with multi-row headers (e.g., **year / sex / age**) to **tidy** rows.
- Robust **standardization** of territory names (province/region/macro), with aliases and light fuzziness.
- **Coverage** analysis for variable × year at province/region level.
- **Plotly heatmap** to visualize missingness.

## Files
```
aliases_helper.py                 # Canonical mappings (regions, provinces, macros, aliases)
standardize_italy_admin_names.py  # Normalization + standardization logic (imports aliases_helper)
completeness.py                   # Coverage/gap computation + Plotly heatmap
tidy_province_wide_to_long.py     # Wide/multi-header → tidy rows
example_usage.py                  # Minimal end-to-end usage
```
> Note: If you adopt Sardegna’s 2025 reorg, update mappings in `aliases_helper.py`.

## Install
```bash
pip install pandas numpy plotly openpyxl xlrd
```
- `openpyxl` for `.xlsx`; `xlrd` for `.xls`.

## Quickstart
1) **Tidy conversion**
```bash
python tidy_province_wide_to_long.py
```
Creates: `italy_provincial_tidy.csv` and `.xlsx`.

2) **Standardize territories**
```python
import pandas as pd
from standardize_italy_admin_names import standardize_territory

df = pd.read_csv("italy_provincial_tidy.csv")
std = df["province"].apply(standardize_territory).apply(pd.Series)
df = pd.concat([df, std], axis=1)
```

3) **Coverage + heatmap**
```python
from completeness import compute_coverage, find_gaps, list_missing_territories, plot_coverage_heatmap_plotly

filters = {"sex": ["Totale", None]}  # optional slice to avoid duplicates
cov_prov = compute_coverage(df, level="province", filters=filters, expected="all")
print(find_gaps(cov_prov).head())    # variable-years with gaps

fig = plot_coverage_heatmap_plotly(cov_prov, level="province", annotate=False, height=700)
fig.show()
```

## Expected columns (tidy)
```
year | province | variable | value | [sex] | [age] | level | province_std | region_std | macro_std
```
- `level` ∈ {`"province"`, `"region"`}.  
- `province_std` / `region_std` are canonical names produced by `standardize_territory`.

## Troubleshooting
- **Import errors** with `src/` layout → run with `PYTHONPATH=src` or append to `sys.path`.
- **.xls read error** → install `xlrd`. For `.xlsx` use `openpyxl`.
- **Unknown labels** → extend `CANONICAL_TO_ALIASES` in `aliases_helper.py`.
- **Busy heatmap** → set `annotate=False` or subset variables.

