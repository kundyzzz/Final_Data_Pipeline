
"""Exploratory Data Analysis for the Product Data Pipeline.

Creates presentation-ready visualizations and analytical CSV tables.
Does not modify the original ETL pipeline, source data, or database.
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ============================================================
# VISUAL STYLE — VIBRANT ANALYTICS
# ============================================================

NAVY = "#14213D"
BLUE = "#4361EE"
PURPLE = "#7B2FF7"
CYAN = "#00C2D1"
PINK = "#F72585"
INDIGO = "#3A0CA3"

MUTED = "#53627A"
GRID = "#E7ECF5"
BACKGROUND = "#FFFFFF"

PALETTE = [
    "#4361EE",
    "#7B2FF7",
    "#00C2D1",
    "#F72585",
    "#3A0CA3",
    "#4895EF",
    "#00A896",
    "#9D4EDD",
    "#4CC9F0",
    "#7209B7",
    "#4361EE",
    "#7B2FF7",
    "#00C2D1",
    "#F72585",
    "#3A0CA3",
]

plt.rcParams.update({
    "figure.facecolor": BACKGROUND,
    "axes.facecolor": BACKGROUND,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "text.color": NAVY,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 18,
    "axes.titleweight": "bold",
    "savefig.facecolor": BACKGROUND,
})


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def style_axes(ax, axis="x"):
    """Apply a consistent clean style to charts."""

    ax.set_axisbelow(True)

    ax.grid(
        axis=axis,
        color=GRID,
        linewidth=0.9,
    )

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(
        length=0,
        pad=8,
    )


def save_chart(fig, path):
    """Save a chart as a high-resolution PNG."""

    fig.savefig(
        path,
        dpi=220,
        bbox_inches="tight",
        facecolor=BACKGROUND,
    )

    plt.close(fig)


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze(
    input_path="data/cleaned.csv",
    figures_dir="figures",
    results_dir="results",
):

    # --------------------------------------------------------
    # 1. LOAD DATA
    # --------------------------------------------------------

    source = Path(input_path)

    if not source.is_file():
        raise FileNotFoundError(source)

    df = pd.read_csv(source)

    required = {
        "sku",
        "name",
        "brand",
        "category",
        "price",
        "rating",
        "availability",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    if df.empty:
        raise ValueError("Dataset is empty")

    # --------------------------------------------------------
    # 2. PREPARE DATA FOR ANALYSIS
    # --------------------------------------------------------

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce",
    )

    df["rating"] = pd.to_numeric(
        df["rating"],
        errors="coerce",
    )

    df["category"] = (
        df["category"]
        .fillna("Unknown")
        .astype(str)
    )

    df["brand"] = (
        df["brand"]
        .fillna("Unknown")
        .astype(str)
    )

    df["availability"] = (
        df["availability"]
        .fillna("unknown")
        .astype(str)
    )

    figures = Path(figures_dir)
    results = Path(results_dir)

    figures.mkdir(
        parents=True,
        exist_ok=True,
    )

    results.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # 3. DATASET OVERVIEW
    # --------------------------------------------------------

    overview = pd.DataFrame([{
        "total_products": len(df),
        "unique_skus": df["sku"].nunique(),
        "unique_brands": df["brand"].nunique(),
        "unique_categories": df["category"].nunique(),
        "average_price": df["price"].mean(),
        "median_price": df["price"].median(),
        "minimum_price": df["price"].min(),
        "maximum_price": df["price"].max(),
        "average_rating": df["rating"].mean(),
        "in_stock_pct": (
            df["availability"]
            .eq("in_stock")
            .mean() * 100
        ),
    }])

    overview.to_csv(
        results / "dataset_overview.csv",
        index=False,
        float_format="%.2f",
    )

    # --------------------------------------------------------
    # 4. GROUPED CATEGORY ANALYSIS
    # --------------------------------------------------------

    summary = (
        df.groupby("category")
        .agg(
            products=("sku", "count"),
            average_price=("price", "mean"),
            median_price=("price", "median"),
            average_rating=("rating", "mean"),
            in_stock=(
                "availability",
                lambda values: int(
                    values.eq("in_stock").sum()
                ),
            ),
        )
        .reset_index()
    )

    summary["in_stock_pct"] = (
        summary["in_stock"]
        / summary["products"]
        * 100
    )

    summary = (
        summary
        .sort_values(
            "products",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    summary.to_csv(
        results / "category_summary.csv",
        index=False,
        float_format="%.2f",
    )

    # ========================================================
    # CHART 1: PRODUCT DISTRIBUTION BY CATEGORY
    # ========================================================

    category_counts = (
        df["category"]
        .value_counts()
        .sort_values()
    )

    fig, ax = plt.subplots(
        figsize=(11, 7.5)
    )

    colors = [
        PALETTE[i % len(PALETTE)]
        for i in range(len(category_counts))
    ]

    bars = ax.barh(
        category_counts.index,
        category_counts.values,
        color=colors,
        height=0.70,
    )

    for bar, value in zip(
        bars,
        category_counts.values,
    ):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            str(value),
            va="center",
            fontsize=11,
            fontweight="bold",
            color=NAVY,
        )

    ax.set_xlim(
        0,
        category_counts.max() * 1.16,
    )

    ax.set_title(
        "Product Distribution by Category",
        loc="left",
        pad=22,
    )

    ax.set_xlabel(
        "Number of Products",
        labelpad=12,
    )

    ax.set_ylabel("")

    style_axes(ax)

    fig.tight_layout()

    save_chart(
        fig,
        figures / "01_products_by_category.png",
    )

    # ========================================================
    # CHART 2: PRODUCT PRICE DISTRIBUTION
    # ========================================================

    prices = (
        df.loc[df["price"] > 0, "price"]
        .dropna()
    )

    if prices.empty:
        raise ValueError(
            "No valid positive prices found"
        )

    mean_price = prices.mean()
    median_price = prices.median()

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    counts, bins, patches = ax.hist(
        prices,
        bins=12,
        edgecolor=BACKGROUND,
        linewidth=2,
    )

    for i, patch in enumerate(patches):
        patch.set_facecolor(
            BLUE if i % 2 == 0 else CYAN
        )
        patch.set_alpha(1.0)

    ax.axvline(
        median_price,
        color=PURPLE,
        linewidth=2.8,
        linestyle="--",
        label=f"Median: {median_price:.2f}",
    )

    ax.axvline(
        mean_price,
        color=PINK,
        linewidth=2.5,
        linestyle=":",
        label=f"Mean: {mean_price:.2f}",
    )

    ax.set_title(
        "Product Price Distribution",
        loc="left",
        pad=20,
    )

    ax.set_xlabel(
        "Product Price (source units)",
        labelpad=12,
    )

    ax.set_ylabel(
        "Number of Products",
        labelpad=12,
    )

    ax.legend(
        frameon=False,
        loc="upper right",
        fontsize=11,
    )

    style_axes(
        ax,
        axis="y",
    )

    fig.tight_layout()

    save_chart(
        fig,
        figures / "02_price_distribution.png",
    )

    # ========================================================
    # CHART 3: AVERAGE PRICE BY CATEGORY — LOLLIPOP
    # ========================================================

    price_by_category = (
        summary[
            ["category", "average_price"]
        ]
        .dropna()
        .sort_values("average_price")
    )

    fig, ax = plt.subplots(
        figsize=(10, 7)
    )

    y = np.arange(
        len(price_by_category)
    )

    values = (
        price_by_category["average_price"]
        .to_numpy()
    )

    labels = (
        price_by_category["category"]
        .tolist()
    )

    colors = [
        PALETTE[i % len(PALETTE)]
        for i in range(len(values))
    ]

    ax.hlines(
        y=y,
        xmin=0,
        xmax=values,
        color=colors,
        linewidth=3.5,
        alpha=0.95,
    )

    ax.scatter(
        values,
        y,
        s=160,
        c=colors,
        zorder=3,
        edgecolors=BACKGROUND,
        linewidth=1.5,
    )

    for i, value in enumerate(values):
        ax.text(
            value + 1.5,
            i,
            f"{value:.1f}",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=NAVY,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(labels)

    if len(values):
        ax.set_xlim(
            0,
            max(values) * 1.18,
        )

    ax.set_title(
        "Average Product Price by Category",
        loc="left",
        pad=20,
    )

    ax.set_xlabel(
        "Average Price (source units)",
        labelpad=12,
    )

    ax.set_ylabel("")

    style_axes(ax)

    fig.tight_layout()

    save_chart(
        fig,
        figures / "03_average_price_by_category.png",
    )

    # ========================================================
    # PRINT ANALYSIS RESULTS
    # ========================================================

    print("\n=== DATASET DIMENSIONS ===")
    print(df.shape)

    print("\n=== DATA TYPES ===")
    print(df.dtypes)

    print("\n=== DESCRIPTIVE STATISTICS ===")
    print(
        df[["price", "rating"]]
        .describe()
        .round(2)
    )

    print("\n=== DATASET OVERVIEW ===")
    print(
        overview
        .round(2)
        .to_string(index=False)
    )

    print("\n=== CATEGORY SUMMARY ===")
    print(
        summary
        .round(2)
        .to_string(index=False)
    )

    print("\nEDA completed successfully!")
    print("Charts saved to:", figures.resolve())
    print("Tables saved to:", results.resolve())


# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="data/cleaned.csv",
    )

    parser.add_argument(
        "--figures-dir",
        default="figures",
    )

    parser.add_argument(
        "--results-dir",
        default="results",
    )

    args = parser.parse_args()

    analyze(
        input_path=args.input,
        figures_dir=args.figures_dir,
        results_dir=args.results_dir,
    )
