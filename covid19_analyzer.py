"""
COVID-19 Data Analyzer
======================
Fetches real-time COVID-19 case and vaccination data using the disease.sh API,
analyzes it with Pandas, and renders interactive charts with Plotly.
"""

import os

import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Config.
BASE_URL = "https://disease.sh/v3/covid-19"
OUTPUT_DIR = "output/charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

#Data fetching

def fetch_country_data() -> pd.DataFrame:
    
    print("Fetching country case data...")
    response = requests.get(f"{BASE_URL}/countries", timeout=10)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data)
    df = df[[
        "country", "cases", "todayCases", "deaths", "todayDeaths",
        "recovered", "active", "critical", "casesPerOneMillion",
        "deathsPerOneMillion", "tests", "population"
    ]]
    df.columns = [
        "Country", "Total Cases", "Today Cases", "Total Deaths", "Today Deaths",
        "Recovered", "Active", "Critical", "Cases/1M", "Deaths/1M",
        "Tests", "Population"
    ]
    return df


def fetch_vaccination_data() -> pd.DataFrame:
    """Fetch vaccination coverage data per country."""
    print("Fetching vaccination data...")
    response = requests.get(f"{BASE_URL}/vaccine/coverage/countries?lastdays=1", timeout=10)
    response.raise_for_status()
    data = response.json()

    records = []
    for item in data:
        country = item.get("country", "Unknown")
        timeline = item.get("timeline", {})
        doses = list(timeline.values())[-1] if timeline else 0
        records.append({"Country": country, "Total Doses": doses})

    return pd.DataFrame(records)


def fetch_global_history(days: int = 30) -> pd.DataFrame:
    """Fetch global historical COVID-19 data for the past N days."""
    print(f"Fetching global history ({days} days)...")
    response = requests.get(f"{BASE_URL}/historical/all?lastdays={days}", timeout=10)
    response.raise_for_status()
    data = response.json()

    cases_df = pd.DataFrame(list(data["cases"].items()), columns=["Date", "Total Cases"])
    deaths_df = pd.DataFrame(list(data["deaths"].items()), columns=["Date", "Total Deaths"])

    df = cases_df.merge(deaths_df, on="Date")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Daily Cases"] = df["Total Cases"].diff().fillna(0).clip(lower=0)
    df["Daily Deaths"] = df["Total Deaths"].diff().fillna(0).clip(lower=0)
    return df

#Analysis

def top_countries_by_cases(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df.nlargest(n, "Total Cases")[["Country", "Total Cases", "Total Deaths", "Recovered"]]


def compute_fatality_rate(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Fatality Rate (%)"] = (df["Total Deaths"] / df["Total Cases"] * 100).round(2)
    return df[df["Total Cases"] > 10000].nlargest(15, "Fatality Rate (%)")


def merge_cases_and_vaccines(cases_df: pd.DataFrame, vacc_df: pd.DataFrame) -> pd.DataFrame:
    merged = cases_df.merge(vacc_df, on="Country", how="inner")
    merged["Doses per 100 people"] = (merged["Total Doses"] / merged["Population"] * 100).round(2)
    return merged[merged["Population"] > 1_000_000]


#visualization

def plot_top_cases(df: pd.DataFrame):
    
    top = top_countries_by_cases(df)
    fig = px.bar(
        top,
        x="Country", y="Total Cases",
        color="Total Deaths",
        color_continuous_scale="Reds",
        title="Top 10 Countries by Total COVID-19 Cases",
        labels={"Total Cases": "Total Cases", "Total Deaths": "Deaths (color)"},
        text_auto=".2s"
    )
    fig.update_layout(xaxis_tickangle=-30)
    path = f"{OUTPUT_DIR}/top_cases.html"
    fig.write_html(path)
    fig.show()
    print(f"Saved: {path}")


def plot_daily_trends(history_df: pd.DataFrame):
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=history_df["Date"], y=history_df["Daily Cases"],
                   name="Daily Cases", line=dict(color="steelblue")),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=history_df["Date"], y=history_df["Daily Deaths"],
                   name="Daily Deaths", line=dict(color="crimson", dash="dash")),
        secondary_y=True
    )

    fig.update_layout(title="Global Daily COVID-19 Cases & Deaths")
    fig.update_yaxes(title_text="Daily Cases", secondary_y=False)
    fig.update_yaxes(title_text="Daily Deaths", secondary_y=True)

    path = f"{OUTPUT_DIR}/daily_trends.html"
    fig.write_html(path)
    fig.show()
    print(f"Saved: {path}")


def plot_vaccination_choropleth(merged_df: pd.DataFrame):
    """World map — vaccination doses per 100 people."""
    fig = px.choropleth(
        merged_df,
        locations="Country",
        locationmode="country names",
        color="Doses per 100 people",
        color_continuous_scale="Greens",
        title="COVID-19 Vaccination Doses per 100 People (by Country)",
        labels={"Doses per 100 people": "Doses / 100 pop."}
    )
    path = f"{OUTPUT_DIR}/vaccination_map.html"
    fig.write_html(path)
    fig.show()
    print(f"Saved: {path}")


def plot_cases_vs_vaccination(merged_df: pd.DataFrame):
    """Scatter plot — total cases vs. vaccination rate."""
    fig = px.scatter(
        merged_df,
        x="Doses per 100 people",
        y="Cases/1M",
        size="Population",
        color="Country",
        hover_name="Country",
        title="Vaccination Rate vs. Cases per 1M Population",
        labels={
            "Doses per 100 people": "Vaccine Doses per 100 People",
            "Cases/1M": "Cases per 1 Million"
        },
        log_y=True
    )
    fig.update_layout(showlegend=False)
    path = f"{OUTPUT_DIR}/cases_vs_vaccination.html"
    fig.write_html(path)
    fig.show()
    print(f"Saved: {path}")


def plot_fatality_rates(df: pd.DataFrame):
    """Horizontal bar chart — fatality rates by country."""
    fat_df = compute_fatality_rate(df)
    fig = px.bar(
        fat_df,
        x="Fatality Rate (%)",
        y="Country",
        orientation="h",
        color="Fatality Rate (%)",
        color_continuous_scale="OrRd",
        title="COVID-19 Case Fatality Rate by Country (min 10K cases)",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    path = f"{OUTPUT_DIR}/fatality_rates.html"
    fig.write_html(path)
    fig.show()
    print(f"Saved: {path}")


#Summary(report)

def print_summary(cases_df: pd.DataFrame, history_df: pd.DataFrame):
    total_cases = cases_df["Total Cases"].sum()
    total_deaths = cases_df["Total Deaths"].sum()
    total_recovered = cases_df["Recovered"].sum()
    today_cases = cases_df["Today Cases"].sum()
    latest_date = history_df["Date"].max().strftime("%Y-%m-%d")

    print("\n" + "=" * 50)
    print("COVID-19 GLOBAL SUMMARY REPORT")
    print("=" * 50)
    print(f"  Data as of      : {latest_date}")
    print(f"  Total Cases     : {total_cases:,}")
    print(f"  Total Deaths    : {total_deaths:,}")
    print(f"  Total Recovered : {total_recovered:,}")
    print(f"  Today's Cases   : {today_cases:,}")
    print(f"  Global CFR      : {total_deaths / total_cases * 100:.2f}%")
    print("=" * 50 + "\n")


#main

def main():
    print("\n COVID-19 Data Analyzer Starting...\n")

    # Fetch
    cases_df = fetch_country_data()
    vacc_df = fetch_vaccination_data()
    history_df = fetch_global_history(days=60)

    # Summary
    print_summary(cases_df, history_df)

    # Merge
    merged_df = merge_cases_and_vaccines(cases_df, vacc_df)

    # Visualize
    plot_top_cases(cases_df)
    plot_daily_trends(history_df)
    plot_vaccination_choropleth(merged_df)
    plot_cases_vs_vaccination(merged_df)
    plot_fatality_rates(cases_df)

    print("\n✅ All charts saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
