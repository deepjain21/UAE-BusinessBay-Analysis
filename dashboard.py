from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

CSV_PATH = Path("dataset/properties.csv")

st.set_page_config(page_title="Business Bay Property Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- Styling ---
pio.templates.default = "plotly_white"
PLOTLY_LAYOUT = dict(
    margin=dict(l=10, r=10, t=40, b=10),
    font=dict(family="-apple-system, BlinkMacSystemFont, sans-serif", size=12, color="#334155"),
    title=dict(font=dict(size=14, color="#0F172A")),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(gridcolor="#E2E8F0", zeroline=False),
    plot_bgcolor="white",
    paper_bgcolor="white",
)
PRIMARY = "#2563EB"
ACCENT = "#F59E0B"
SUCCESS = "#10B981"
DANGER = "#EF4444"

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }
    h1 { font-size: 1.75rem !important; font-weight: 700; margin-bottom: 0.25rem !important; }
    h2 { font-size: 1.15rem !important; font-weight: 600; color: #0F172A; margin-top: 1.5rem !important; }
    h3 { font-size: 1rem !important; font-weight: 600; color: #334155; }
    [data-testid="stMetric"] {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 16px;
    }
    [data-testid="stMetricLabel"] { font-size: 0.8rem; color: #64748B; }
    [data-testid="stMetricValue"] { font-size: 1.4rem; font-weight: 700; color: #0F172A; }
    [data-testid="stSidebar"] { background: #F8FAFC; }
    [data-testid="stSidebar"] h2 { font-size: 1rem !important; margin-top: 0 !important; color: #0F172A; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; }
    div[data-testid="stCaptionContainer"] p { color: #64748B; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"permit_number": str})
    df["listed_dt"] = pd.to_datetime(df["listed_on"], errors="coerce", utc=True).dt.tz_localize(None)
    df["listed_month"] = df["listed_dt"].dt.to_period("M").dt.to_timestamp()
    return df


def multiselect_all(label, options, key):
    sel = st.sidebar.multiselect(label, options, default=[], key=key, placeholder="All")
    return options if not sel else sel


df = load_data(CSV_PATH)

# --- Sidebar filters ---
st.sidebar.markdown("## Filters")
st.sidebar.caption("Empty = include all")

bedroom_order = ["Studio", "1", "2", "3", "4", "5", "6", "7"]
bedroom_options = [b for b in bedroom_order if b in df["bedrooms"].dropna().unique()]
bedrooms_sel = multiselect_all("Bedrooms", bedroom_options, "f_bed")

communities = sorted(df["community"].dropna().unique())
community_sel = multiselect_all(f"Community ({len(communities)})", communities, "f_comm")

zones = sorted(df["zone"].dropna().unique())
zone_sel = multiselect_all("Zone", zones, "f_zone")

statuses = sorted(df["status"].dropna().unique())
status_sel = multiselect_all("Status", statuses, "f_status")

furn_options = sorted(df["furnishing"].dropna().unique())
furn_sel = multiselect_all("Furnishing", furn_options, "f_furn")

st.sidebar.markdown("---")

bath_min, bath_max = int(df["bathrooms"].min()), int(df["bathrooms"].max())
bath_range = st.sidebar.slider("Bathrooms", bath_min, bath_max, (bath_min, bath_max))

# Price slider in millions for readability
price_min_m = round(df["price_aed"].min() / 1e6, 2)
price_max_m = round(df["price_aed"].max() / 1e6, 2)
price_p99_m = round(df["price_aed"].quantile(0.99) / 1e6, 2)
price_range_m = st.sidebar.slider(
    "Price (AED)",
    min_value=price_min_m, max_value=price_max_m,
    value=(price_min_m, price_p99_m),
    step=0.1, format="%.1fM",
)
price_range = (price_range_m[0] * 1e6, price_range_m[1] * 1e6)

size_min = int(df["size_sqft"].min())
size_max = int(df["size_sqft"].max())
size_p99 = int(df["size_sqft"].quantile(0.99))
size_range = st.sidebar.slider(
    "Size", size_min, size_max, (size_min, size_p99),
    step=50, format="%d sqft",
)

pps_min = int(df["price_per_sqft_aed"].min())
pps_max = int(df["price_per_sqft_aed"].max())
pps_p99 = int(df["price_per_sqft_aed"].quantile(0.99))
pps_range = st.sidebar.slider(
    "Price per sqft", pps_min, pps_max, (pps_min, pps_p99),
    step=50, format="%d AED",
)

date_min = df["listed_dt"].min().date()
date_max = df["listed_dt"].max().date()
date_range = st.sidebar.date_input("Listed between", value=(date_min, date_max), min_value=date_min, max_value=date_max)
if isinstance(date_range, tuple) and len(date_range) == 2:
    d_from, d_to = date_range
else:
    d_from, d_to = date_min, date_max

mask = (
    df["bedrooms"].isin(bedrooms_sel)
    & df["community"].isin(community_sel)
    & df["zone"].isin(zone_sel)
    & df["status"].isin(status_sel)
    & df["furnishing"].isin(furn_sel)
    & df["bathrooms"].between(*bath_range)
    & df["price_aed"].between(*price_range)
    & df["size_sqft"].between(*size_range)
    & df["price_per_sqft_aed"].between(*pps_range)
    & df["listed_dt"].dt.date.between(d_from, d_to)
)
fdf = df[mask].copy()

# --- Header ---
st.markdown("# Business Bay — Property Listings")
st.caption(f"{len(fdf):,} listings shown of {len(df):,} total · Source: dataset/properties.csv")

if fdf.empty:
    st.warning("No listings match the current filters. Try loosening them in the sidebar.")
    st.stop()

# Outlier flag (per community Z-score)
fdf["community_mean"] = fdf.groupby("community")["price_aed"].transform("mean")
fdf["community_std"] = fdf.groupby("community")["price_aed"].transform("std")
fdf["price_z"] = (fdf["price_aed"] - fdf["community_mean"]) / fdf["community_std"]
fdf["is_outlier"] = fdf["price_z"].abs() > 2

# --- KPIs (5 columns instead of 6 to avoid truncation) ---
def fmt_aed(x):
    if x >= 1e6: return f"{x/1e6:.2f}M"
    if x >= 1e3: return f"{x/1e3:.0f}K"
    return f"{x:.0f}"

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Listings", f"{len(fdf):,}")
c2.metric("Median price", f"AED {fmt_aed(fdf['price_aed'].median())}")
c3.metric("Mean price", f"AED {fmt_aed(fdf['price_aed'].mean())}")
c4.metric("Median AED/sqft", f"{fdf['price_per_sqft_aed'].median():,.0f}")
_n_out = int(fdf["is_outlier"].sum())
_pct_out = fdf["is_outlier"].mean() * 100
c5.metric("Outliers", f"{_n_out}  ·  {_pct_out:.1f}%")

st.markdown("")

tab_pricing, tab_timeline, tab_map, tab_data = st.tabs(["📊 Pricing", "📈 Timeline", "🗺️ Map", "📋 Data"])

with tab_pricing:
    left, right = st.columns(2)

    with left:
        st.markdown("##### Price distribution")
        mean_v, median_v = fdf["price_aed"].mean(), fdf["price_aed"].median()
        fig = px.histogram(fdf, x="price_aed", nbins=50, color_discrete_sequence=[PRIMARY])
        fig.add_vline(x=mean_v, line_dash="dash", line_color=ACCENT, line_width=2,
                      annotation_text=f"Mean {fmt_aed(mean_v)}", annotation_position="top right",
                      annotation=dict(font_color=ACCENT, font_size=11))
        fig.add_vline(x=median_v, line_dash="dash", line_color=SUCCESS, line_width=2,
                      annotation_text=f"Median {fmt_aed(median_v)}", annotation_position="top left",
                      annotation=dict(font_color=SUCCESS, font_size=11))
        fig.update_layout(xaxis_title="Price (AED)", yaxis_title="Listings", bargap=0.05, height=320, **PLOTLY_LAYOUT)
        st.plotly_chart(fig, width="stretch")

    with right:
        st.markdown("##### Price per sqft distribution")
        median_pps = fdf["price_per_sqft_aed"].median()
        fig = px.histogram(fdf, x="price_per_sqft_aed", nbins=50, color_discrete_sequence=[PRIMARY])
        fig.add_vline(x=median_pps, line_dash="dash", line_color=SUCCESS, line_width=2,
                      annotation_text=f"Median {median_pps:,.0f}", annotation_position="top right",
                      annotation=dict(font_color=SUCCESS, font_size=11))
        fig.update_layout(xaxis_title="AED / sqft", yaxis_title="Listings", bargap=0.05, height=320, **PLOTLY_LAYOUT)
        st.plotly_chart(fig, width="stretch")

    st.markdown("##### Price by community (top 15 by listing count)")
    top_communities = fdf["community"].value_counts().head(15).index.tolist()
    box_df = fdf[fdf["community"].isin(top_communities)]
    fig = px.box(box_df, x="community", y="price_aed", points="outliers",
                 category_orders={"community": top_communities},
                 color_discrete_sequence=[PRIMARY])
    fig.update_layout(xaxis_title=None, yaxis_title="Price (AED)", xaxis_tickangle=-30, height=420, **PLOTLY_LAYOUT)
    st.plotly_chart(fig, width="stretch")

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("##### Per-community pricing summary")
        comm_stats = (
            fdf.groupby("community")["price_aed"]
            .agg(listings="count", mean="mean", median="median", std="std", min="min", max="max")
            .sort_values("listings", ascending=False)
            .round(0)
        )
        st.dataframe(
            comm_stats.head(20).style.format({"mean": "{:,.0f}", "median": "{:,.0f}", "std": "{:,.0f}", "min": "{:,.0f}", "max": "{:,.0f}"}),
            width="stretch", height=420,
        )

    with col_r:
        st.markdown(f"##### Outliers — {fdf['is_outlier'].sum()} listings (|Z| > 2 within community)")
        out_cols = ["community", "bedrooms", "size_sqft", "price_aed", "price_per_sqft_aed", "price_z"]
        outliers = fdf[fdf["is_outlier"]][out_cols].sort_values("price_z", key=lambda s: s.abs(), ascending=False)
        st.dataframe(
            outliers.style.format({
                "price_aed": "{:,.0f}", "price_per_sqft_aed": "{:,.0f}",
                "price_z": "{:+.2f}", "size_sqft": "{:,.0f}",
            }),
            width="stretch", height=420,
        )

with tab_timeline:
    st.markdown("##### Listings volume and median price by month")
    monthly = (
        fdf.groupby("listed_month")
        .agg(listings=("price_aed", "size"), median_price=("price_aed", "median"))
        .reset_index()
        .sort_values("listed_month")
    )
    fig = go.Figure()
    fig.add_bar(x=monthly["listed_month"], y=monthly["listings"], name="Listings",
                marker_color=PRIMARY, opacity=0.85, yaxis="y")
    fig.add_trace(go.Scatter(x=monthly["listed_month"], y=monthly["median_price"], name="Median price",
                             mode="lines+markers", line=dict(color=ACCENT, width=3), yaxis="y2"))
    fig.update_layout(
        xaxis_title=None,
        yaxis=dict(title="Listings", gridcolor="#E2E8F0"),
        yaxis2=dict(title="Median price (AED)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.12, x=0, bgcolor="rgba(0,0,0,0)"),
        height=420,
        **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")},
    )
    st.plotly_chart(fig, width="stretch")

    st.markdown("##### Cumulative listings over time")
    daily = fdf.groupby(fdf["listed_dt"].dt.date).size().reset_index(name="listings")
    daily.columns = ["date", "listings"]
    daily["cumulative"] = daily["listings"].cumsum()
    fig = px.area(daily, x="date", y="cumulative", color_discrete_sequence=[PRIMARY])
    fig.update_traces(line_color=PRIMARY, fillcolor="rgba(37, 99, 235, 0.15)")
    fig.update_layout(xaxis_title=None, yaxis_title="Cumulative listings", height=320, **PLOTLY_LAYOUT)
    st.plotly_chart(fig, width="stretch")

with tab_map:
    st.markdown("##### Geographic distribution")
    st.caption("Color = AED per sqft · Size = absolute price")
    map_df = fdf.dropna(subset=["latitude", "longitude"]).copy()
    fig = px.scatter_map(
        map_df,
        lat="latitude", lon="longitude",
        color="price_per_sqft_aed",
        size="price_aed",
        size_max=18, zoom=12, height=650,
        hover_data={
            "community": True, "bedrooms": True,
            "size_sqft": ":,.0f", "price_aed": ":,.0f", "price_per_sqft_aed": ":,.0f",
            "latitude": False, "longitude": False,
        },
        color_continuous_scale="Viridis",
    )
    fig.update_layout(map_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, width="stretch")

with tab_data:
    st.markdown(f"##### Filtered listings — {len(fdf):,} rows")
    show_cols = [
        "community", "building", "bedrooms", "bathrooms",
        "size_sqft", "price_aed", "price_per_sqft_aed", "furnishing", "status",
        "listed_on", "permit_number",
    ]
    st.dataframe(
        fdf[show_cols].style.format({
            "size_sqft": "{:,.0f}", "price_aed": "{:,.0f}",
            "price_per_sqft_aed": "{:,.0f}", "bathrooms": "{:.0f}",
        }),
        width="stretch", height=600,
    )
    st.download_button(
        "⬇ Download filtered CSV",
        fdf[show_cols].to_csv(index=False).encode("utf-8"),
        file_name="filtered_listings.csv",
        mime="text/csv",
    )
