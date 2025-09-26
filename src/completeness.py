# completeness.py
# Identify variable-year gaps and visualize coverage as a Plotly heatmap.

from typing import Dict, Iterable, Optional, Tuple
import numpy as np
import pandas as pd
import plotly.express as px

# ---------------- Core helpers ----------------

def _territory_col_for(level: str) -> str:
    if level not in {"province", "region"}:
        raise ValueError("level must be 'province' or 'region'")
    return "province_std" if level == "province" else "region_std"

def _apply_filters(df: pd.DataFrame, filters: Optional[Dict[str, Iterable]] = None) -> pd.DataFrame:
    if not filters:
        return df
    out = df.copy()
    for col, allowed in filters.items():
        if col in out.columns:
            out = out[out[col].isin(allowed)]
    return out

# ---------------- Coverage & gaps ----------------

def compute_coverage(
    df: pd.DataFrame,
    level: str = "province",
    filters: Optional[Dict[str, Iterable]] = None,
    expected: str = "all",
) -> pd.DataFrame:
    """
    Coverage per variable×year at the chosen territorial level.

    df columns needed:
      ['year','variable','value','level','province_std','region_std', ...]
    level     : 'province' or 'region'
    filters   : e.g. {'sex': ['Totale', None], 'age': ['Totale']}
    expected  : 'all' (all territories in filtered df) | 'by_year' (territories present in that year)

    Returns:
      ['level','variable','year','present_count','expected_count','missing_count','coverage']
    """
    territory_col = _territory_col_for(level)
    d = df.copy()

    d = d[d["level"] == level]
    d = _apply_filters(d, filters)
    d["year"] = pd.to_numeric(d["year"], errors="coerce").astype("Int64")

    if expected == "all":
        universe = set(d[territory_col].dropna().unique().tolist())
        expected_by_year = None
    elif expected == "by_year":
        expected_by_year = (
            d.groupby("year")[territory_col]
             .nunique(dropna=True)
             .rename("exp_in_year")
             .to_dict()
        )
        universe = set(d[territory_col].dropna().unique().tolist())
    else:
        raise ValueError("expected must be 'all' or 'by_year'")

    presence = (
        d.assign(has_value=d["value"].notna())
         .groupby(["variable", "year", territory_col], as_index=False)["has_value"]
         .max()
    )

    present = (
        presence.groupby(["variable", "year"])["has_value"]
                .sum(min_count=0)
                .rename("present_count")
                .reset_index()
    )

    if expected == "all":
        present["expected_count"] = len(universe)
    else:
        present["expected_count"] = present["year"].map(expected_by_year).fillna(0).astype(int)

    present["coverage"] = (
        present["present_count"] / present["expected_count"].replace({0: np.nan})
    ).clip(0, 1)
    present["missing_count"] = present["expected_count"] - present["present_count"]
    present["level"] = level

    cols = ["level","variable","year","present_count","expected_count","missing_count","coverage"]
    return present[cols].sort_values(["variable", "year"]).reset_index(drop=True)

def find_gaps(coverage: pd.DataFrame, threshold: float = 1.0) -> pd.DataFrame:
    """
    Return variable-year rows where coverage < threshold (default: any gap).
    """
    return (coverage[coverage["coverage"] < threshold]
            .sort_values(["variable","year"])
            .reset_index(drop=True))

def list_missing_territories(
    df: pd.DataFrame,
    variable: str,
    year: int,
    level: str = "province",
    filters: Optional[Dict[str, Iterable]] = None,
    expected: str = "all",
) -> Tuple[str, int, str, list]:
    """
    Explicit list of missing territories for a given variable-year.
    Returns: (variable, year, level, missing_list)
    """
    territory_col = _territory_col_for(level)
    d = df.copy()
    d = d[d["level"] == level]
    d = _apply_filters(d, filters)

    if expected == "all":
        universe = set(d[territory_col].dropna().unique().tolist())
    else:
        universe = set(d.loc[d["year"] == year, territory_col].dropna().unique().tolist())

    obs = (
        d[(d["variable"] == variable) & (d["year"] == year)]
         .assign(has_value=d["value"].notna())
         .groupby(territory_col, as_index=False)["has_value"]
         .max()
    )
    present = set(obs.loc[obs["has_value"], territory_col].tolist())
    missing = sorted(universe - present)
    return variable, int(year), level, missing

# ---------------- Plotly heatmap ----------------

def plot_coverage_heatmap_plotly(
    coverage: pd.DataFrame,
    level: str = "province",
    variables: Optional[Iterable[str]] = None,
    title: Optional[str] = None,
    annotate: bool = False,
    height: Optional[int] = None,
):
    """
    Plotly heatmap (variables × years) with coverage in [0,1].

    coverage : output of compute_coverage(...)
    variables: optional subset of variable names
    annotate : show % labels in cells
    height   : figure height; width is auto
    """
    cov = coverage.copy()
    if variables is not None:
        cov = cov[cov["variable"].isin(variables)]
    if cov.empty:
        raise ValueError("No data to plot after filtering.")

    # Pivot to 2D matrix
    pivot = (cov.pivot(index="variable", columns="year", values="coverage")
                .sort_index()
                .sort_index(axis=1))
    fig = px.imshow(
        pivot,
        aspect="auto",
        zmin=0, zmax=1,
        color_continuous_scale="Viridis",
        labels=dict(x="Year", y="Variable", color="Coverage"),
    )

    fig.update_layout(
        title=title or f"Coverage by variable × year ({level})",
        xaxis_title="Year",
        yaxis_title="Variable",
        coloraxis_colorbar=dict(title="Coverage"),
        height=height,
        margin=dict(l=60, r=20, t=60, b=60),
    )
    fig.update_xaxes(tickangle=45)

    if annotate:
        # Show percentages in cells
        fig.update_traces(texttemplate="%{z:.0%}", text=pivot.values, textfont_size=10)

    return fig
