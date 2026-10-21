
# ============================================================
# SMART TRAFFIC ANALYTICS DASHBOARD
# Streamlit + MySQL + Plotly + Seaborn
# ============================================================
#
# Install once:
# pip install streamlit pandas mysql-connector-python plotly seaborn matplotlib
#
# Run:
# streamlit run traffic_dashboard.py
#
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Traffic Analytics",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0b1120;
    color: #f8fafc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border-right: 1px solid #1e293b;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* Main title */
.dashboard-title {
    font-size: 34px;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 2px;
}

.dashboard-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 25px;
}

/* KPI cards */
.kpi-card {
    background: linear-gradient(145deg, #111827, #172033);
    border: 1px solid #263449;
    border-radius: 16px;
    padding: 18px;
    min-height: 135px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.18);
}

.kpi-icon {
    font-size: 26px;
    margin-bottom: 5px;
}

.kpi-label {
    color: #94a3b8;
    font-size: 13px;
    font-weight: 600;
}

.kpi-value {
    color: #f8fafc;
    font-size: 27px;
    font-weight: 800;
    margin-top: 5px;
}

.kpi-small {
    color: #64748b;
    font-size: 11px;
    margin-top: 5px;
}

/* Section headers */
.section-header {
    color: #f8fafc;
    font-size: 19px;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 10px;
}

/* Chart containers */
.chart-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 8px 10px 2px 10px;
}

/* Filter labels */
.filter-title {
    color: #38bdf8;
    font-weight: 700;
    font-size: 14px;
}

/* Hide Streamlit menu/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_data(ttl=300)
def load_data():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Saxena@123",
        database="traffic_db"
    )

    query = """
        SELECT
            id,
            timestamp,
            latitude,
            longitude,
            vehicle_count,
            traffic_speed_kmh,
            road_occupancy_pct,
            traffic_light_state,
            weather_condition,
            accident_report,
            sentiment_score,
            ride_sharing_demand,
            parking_availability,
            emission_levels_g_km,
            energy_consumption_l_h,
            traffic_condition
        FROM traffic_data
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Useful time columns
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day_name()
    df["month"] = df["timestamp"].dt.strftime("%b")

    return df


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = load_data()
except Exception as e:
    st.error("Could not connect to MySQL.")
    st.code(str(e))
    st.info(
        "Open traffic_dashboard.py and change YOUR_MYSQL_PASSWORD "
        "to your MySQL password."
    )
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div style="
        text-align:center;
        padding:10px 0 25px 0;
    ">
        <div style="font-size:52px;">🚦</div>
        <div style="
            font-size:21px;
            font-weight:800;
            color:#f8fafc;
        ">
            TrafficIQ
        </div>
        <div style="
            color:#64748b;
            font-size:12px;
        ">
            Smart Traffic Analytics
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔎 Filters")

    conditions = sorted(df["traffic_condition"].dropna().unique())
    selected_conditions = st.multiselect(
        "Traffic Condition",
        conditions,
        default=conditions
    )

    weather = sorted(df["weather_condition"].dropna().unique())
    selected_weather = st.multiselect(
        "Weather",
        weather,
        default=weather
    )

    signals = sorted(df["traffic_light_state"].dropna().unique())
    selected_signals = st.multiselect(
        "Traffic Light",
        signals,
        default=signals
    )

    min_speed = float(df["traffic_speed_kmh"].min())
    max_speed = float(df["traffic_speed_kmh"].max())

    speed_range = st.slider(
        "Speed Range (km/h)",
        min_value=min_speed,
        max_value=max_speed,
        value=(min_speed, max_speed)
    )

    st.markdown("---")

    st.markdown("""
    <div style="
        background:#111827;
        border:1px solid #1e293b;
        border-radius:12px;
        padding:14px;
        color:#94a3b8;
        font-size:12px;
    ">
    <b style="color:#f8fafc;">📊 Dataset</b><br><br>
    Live data from MySQL<br>
    Traffic monitoring dataset<br>
    AI / Analytics Ready
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df[
    df["traffic_condition"].isin(selected_conditions)
    & df["weather_condition"].isin(selected_weather)
    & df["traffic_light_state"].isin(selected_signals)
    & df["traffic_speed_kmh"].between(speed_range[0], speed_range[1])
].copy()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">🚦 Smart Traffic Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Real-time style traffic monitoring, mobility analysis and environmental insights'
    '</div>',
    unsafe_allow_html=True
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_records = len(filtered)
avg_speed = filtered["traffic_speed_kmh"].mean()
avg_vehicles = filtered["vehicle_count"].mean()
avg_occupancy = filtered["road_occupancy_pct"].mean()

accidents = int(filtered["accident_report"].sum())

avg_emission = filtered["emission_levels_g_km"].mean()
avg_energy = filtered["energy_consumption_l_h"].mean()

parking = filtered["parking_availability"].mean()
ride_demand = filtered["ride_sharing_demand"].mean()


# ============================================================
# KPI CARDS
# ============================================================

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🚗</div>
        <div class="kpi-label">AVG VEHICLES</div>
        <div class="kpi-value">{avg_vehicles:,.0f}</div>
        <div class="kpi-small">vehicles per observation</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">⚡</div>
        <div class="kpi-label">AVG SPEED</div>
        <div class="kpi-value">{avg_speed:.1f} km/h</div>
        <div class="kpi-small">traffic movement</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🛣️</div>
        <div class="kpi-label">ROAD OCCUPANCY</div>
        <div class="kpi-value">{avg_occupancy:.1f}%</div>
        <div class="kpi-small">average road utilization</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-label">ACCIDENT REPORTS</div>
        <div class="kpi-value">{accidents:,}</div>
        <div class="kpi-small">reported incidents</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SECOND KPI ROW
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

k5, k6, k7, k8 = st.columns(4)

with k5:
    st.metric("🌫️ Avg Emission", f"{avg_emission:.2f} g/km")

with k6:
    st.metric("🔋 Energy Consumption", f"{avg_energy:.2f} L/h")

with k7:
    st.metric("🅿️ Parking Availability", f"{parking:,.0f}")

with k8:
    st.metric("🚕 Ride Sharing Demand", f"{ride_demand:,.0f}")


# ============================================================
# TRAFFIC TREND
# ============================================================

st.markdown(
    '<div class="section-header">📈 Traffic Movement Over Time</div>',
    unsafe_allow_html=True
)

hourly = (
    filtered
    .groupby("hour", as_index=False)
    .agg(
        avg_speed=("traffic_speed_kmh", "mean"),
        avg_vehicles=("vehicle_count", "mean"),
        avg_occupancy=("road_occupancy_pct", "mean")
    )
)

fig_trend = go.Figure()

fig_trend.add_trace(
    go.Scatter(
        x=hourly["hour"],
        y=hourly["avg_vehicles"],
        mode="lines+markers",
        name="Vehicles",
        line=dict(width=3),
        fill="tozeroy"
    )
)

fig_trend.update_layout(
    title="Average Vehicle Count by Hour",
    template="plotly_dark",
    height=390,
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis_title="Hour of Day",
    yaxis_title="Average Vehicles",
    hovermode="x unified"
)

st.plotly_chart(fig_trend, use_container_width=True)


# ============================================================
# TRAFFIC CONDITION + WEATHER
# ============================================================

c1, c2 = st.columns(2)

with c1:

    st.markdown(
        '<div class="section-header">🚦 Traffic Conditions</div>',
        unsafe_allow_html=True
    )

    condition_data = (
        filtered["traffic_condition"]
        .value_counts()
        .reset_index()
    )

    condition_data.columns = ["condition", "count"]

    fig_condition = px.bar(
        condition_data,
        x="condition",
        y="count",
        color="condition",
        text="count",
        template="plotly_dark"
    )

    fig_condition.update_layout(
        height=360,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    fig_condition.update_traces(
        textposition="outside"
    )

    st.plotly_chart(fig_condition, use_container_width=True)


with c2:

    st.markdown(
        '<div class="section-header">🌦️ Weather Distribution</div>',
        unsafe_allow_html=True
    )

    weather_data = (
        filtered["weather_condition"]
        .value_counts()
        .reset_index()
    )

    weather_data.columns = ["weather", "count"]

    fig_weather = px.pie(
        weather_data,
        names="weather",
        values="count",
        hole=0.55,
        template="plotly_dark"
    )

    fig_weather.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(fig_weather, use_container_width=True)


# ============================================================
# SPEED VS VEHICLES SCATTER
# ============================================================

c3, c4 = st.columns(2)

with c3:

    st.markdown(
        '<div class="section-header">🚗 Speed vs Vehicle Density</div>',
        unsafe_allow_html=True
    )

    fig_scatter = px.scatter(
        filtered,
        x="vehicle_count",
        y="traffic_speed_kmh",
        color="traffic_condition",
        size="road_occupancy_pct",
        hover_data=[
            "weather_condition",
            "traffic_light_state",
            "latitude",
            "longitude"
        ],
        template="plotly_dark"
    )

    fig_scatter.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(fig_scatter, use_container_width=True)


with c4:

    st.markdown(
        '<div class="section-header">🌫️ Emissions by Traffic Condition</div>',
        unsafe_allow_html=True
    )

    emission_data = (
        filtered
        .groupby("traffic_condition", as_index=False)
        ["emission_levels_g_km"]
        .mean()
        .sort_values("emission_levels_g_km", ascending=False)
    )

    fig_emission = px.bar(
        emission_data,
        x="traffic_condition",
        y="emission_levels_g_km",
        color="emission_levels_g_km",
        text_auto=".2f",
        template="plotly_dark"
    )

    fig_emission.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Traffic Condition",
        yaxis_title="Emission (g/km)"
    )

    st.plotly_chart(fig_emission, use_container_width=True)


# ============================================================
# HEATMAP
# ============================================================

st.markdown(
    '<div class="section-header">🔥 Traffic Correlation Heatmap</div>',
    unsafe_allow_html=True
)

numeric_columns = [
    "vehicle_count",
    "traffic_speed_kmh",
    "road_occupancy_pct",
    "sentiment_score",
    "ride_sharing_demand",
    "parking_availability",
    "emission_levels_g_km",
    "energy_consumption_l_h",
    "accident_report"
]

corr = filtered[numeric_columns].corr()

fig_heat, ax = plt.subplots(figsize=(13, 7))

fig_heat.patch.set_facecolor("#111827")
ax.set_facecolor("#111827")

sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    linewidths=0.5,
    ax=ax,
    cbar_kws={"shrink": 0.8}
)

ax.set_title(
    "Correlation Between Traffic Metrics",
    color="white",
    fontsize=15,
    fontweight="bold",
    pad=15
)

ax.tick_params(colors="white", labelsize=9)

for text in ax.get_xticklabels():
    text.set_color("white")

for text in ax.get_yticklabels():
    text.set_color("white")

st.pyplot(fig_heat, use_container_width=True)
plt.close(fig_heat)


# ============================================================
# HOURLY HEATMAP
# ============================================================

st.markdown(
    '<div class="section-header">🕒 Hour × Traffic Condition Heatmap</div>',
    unsafe_allow_html=True
)

hour_condition = pd.crosstab(
    filtered["hour"],
    filtered["traffic_condition"]
)

fig_hour, ax2 = plt.subplots(figsize=(13, 6))

fig_hour.patch.set_facecolor("#111827")
ax2.set_facecolor("#111827")

sns.heatmap(
    hour_condition,
    cmap="YlOrRd",
    annot=True,
    fmt="d",
    linewidths=0.3,
    ax=ax2
)

ax2.set_title(
    "Traffic Observations by Hour and Condition",
    color="white",
    fontsize=15,
    fontweight="bold"
)

ax2.set_xlabel("Traffic Condition", color="white")
ax2.set_ylabel("Hour of Day", color="white")

ax2.tick_params(colors="white")

st.pyplot(fig_hour, use_container_width=True)
plt.close(fig_hour)


# ============================================================
# TRAFFIC LIGHT ANALYSIS
# ============================================================

c5, c6 = st.columns(2)

with c5:

    st.markdown(
        '<div class="section-header">🚥 Traffic Light States</div>',
        unsafe_allow_html=True
    )

    light_data = (
        filtered["traffic_light_state"]
        .value_counts()
        .reset_index()
    )

    light_data.columns = ["state", "count"]

    fig_light = px.bar(
        light_data,
        x="state",
        y="count",
        color="state",
        text="count",
        template="plotly_dark"
    )

    fig_light.update_layout(
        height=370,
        showlegend=False
    )

    st.plotly_chart(fig_light, use_container_width=True)


with c6:

    st.markdown(
        '<div class="section-header">🅿️ Parking Availability</div>',
        unsafe_allow_html=True
    )

    parking_data = (
        filtered
        .groupby("hour", as_index=False)
        ["parking_availability"]
        .mean()
    )

    fig_parking = px.area(
        parking_data,
        x="hour",
        y="parking_availability",
        template="plotly_dark"
    )

    fig_parking.update_layout(
        height=370,
        xaxis_title="Hour",
        yaxis_title="Average Parking Availability"
    )

    st.plotly_chart(fig_parking, use_container_width=True)


# ============================================================
# DAILY SUMMARY TABLE
# ============================================================

st.markdown(
    '<div class="section-header">📋 Traffic Summary</div>',
    unsafe_allow_html=True
)

summary = (
    filtered
    .groupby("traffic_condition")
    .agg(
        Records=("id", "count"),
        Avg_Vehicles=("vehicle_count", "mean"),
        Avg_Speed=("traffic_speed_kmh", "mean"),
        Avg_Occupancy=("road_occupancy_pct", "mean"),
        Avg_Emission=("emission_levels_g_km", "mean"),
        Accidents=("accident_report", "sum")
    )
    .reset_index()
)

summary["Avg_Vehicles"] = summary["Avg_Vehicles"].round(0)
summary["Avg_Speed"] = summary["Avg_Speed"].round(2)
summary["Avg_Occupancy"] = summary["Avg_Occupancy"].round(2)
summary["Avg_Emission"] = summary["Avg_Emission"].round(2)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<hr style="border:1px solid #1e293b;">

<div style="
    text-align:center;
    color:#64748b;
    padding:10px;
    font-size:12px;
">
    🚦 TrafficIQ • Smart Traffic Analytics Dashboard
    <br>
    Built with Python • Streamlit • MySQL • Plotly • Seaborn
</div>
""", unsafe_allow_html=True)
