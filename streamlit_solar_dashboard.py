import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

# Configure page
st.set_page_config(
    page_title="Solar Panel Energy Analytics",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2E86AB;
        margin-bottom: 1rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .info-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF6B35;
        margin: 1rem 0;
    }
    .stSelectbox > div > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Feature ranges for all seasons
feature_ranges = {
    'summer': {
        'irradiance': (600, 1000),
        'humidity': (10, 50),
        'wind_speed': (0, 5),
        'ambient_temperature': (30, 45),
        'tilt_angle': (10, 40),
    },
    'monsoon': {
        'irradiance': (100, 600),
        'humidity': (70, 100),
        'wind_speed': (2, 8),
        'ambient_temperature': (20, 35),
        'tilt_angle': (10, 40),
    },
    'winter': {
        'irradiance': (300, 700),
        'humidity': (30, 70),
        'wind_speed': (1, 6),
        'ambient_temperature': (5, 20),
        'tilt_angle': (10, 40),
    }
}

# Months with exact days for each season
season_months_days = {
    'summer': {
        'March': 31,
        'April': 30,
        'May': 31,
        'June': 30
    },
    'monsoon': {
        'July': 31,
        'August': 31,
        'September': 30,
        'October': 31
    },
    'winter': {
        'November': 30,
        'December': 31,
        'January': 31,
        'February': 28
    }
}

def calc_kwh_summer(irradiance, humidity, wind_speed, ambient_temp, tilt_angle):
    return (0.25 * irradiance
            - 0.05 * humidity
            + 0.02 * wind_speed
            + 0.1 * ambient_temp
            - 0.03 * abs(tilt_angle - 30))

def calc_kwh_monsoon(irradiance, humidity, wind_speed, ambient_temp, tilt_angle):
    return (0.15 * irradiance
            - 0.1 * humidity
            + 0.01 * wind_speed
            + 0.05 * ambient_temp
            - 0.04 * abs(tilt_angle - 30))

def calc_kwh_winter(irradiance, humidity, wind_speed, ambient_temp, tilt_angle):
    return (0.18 * irradiance
            - 0.03 * humidity
            + 0.015 * wind_speed
            + 0.08 * ambient_temp
            - 0.02 * abs(tilt_angle - 30))

@st.cache_data
def generate_seasonal_data(season, feature_ranges, months_days):
    """Generate data for a specific season"""
    data = []
    season_ranges = feature_ranges[season]
    season_months = months_days[season]
    
    # Select appropriate calculation function
    if season == 'summer':
        calc_func = calc_kwh_summer
    elif season == 'monsoon':
        calc_func = calc_kwh_monsoon
    elif season == 'winter':
        calc_func = calc_kwh_winter
    
    for month, days in season_months.items():
        for _ in range(days):
            irr = np.random.uniform(*season_ranges['irradiance'])
            hum = np.random.uniform(*season_ranges['humidity'])
            wind = np.random.uniform(*season_ranges['wind_speed'])
            temp = np.random.uniform(*season_ranges['ambient_temperature'])
            tilt = np.random.uniform(*season_ranges['tilt_angle'])

            kwh = calc_func(irr, hum, wind, temp, tilt)

            data.append({
                'irradiance': round(irr, 2),
                'humidity': round(hum, 2),
                'wind_speed': round(wind, 2),
                'ambient_temperature': round(temp, 2),
                'tilt_angle': round(tilt, 2),
                'kwh': round(kwh, 2),
                'season': season,
                'month': month
            })
    
    return pd.DataFrame(data)

@st.cache_data
def generate_all_seasons_data():
    """Generate data for all seasons and combine them"""
    all_data = []
    
    for season in ['summer', 'monsoon', 'winter']:
        season_df = generate_seasonal_data(season, feature_ranges, season_months_days)
        all_data.append(season_df)
    
    # Combine all seasonal data
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df

# Main app
def main():
    st.markdown('<h1 class="main-header">☀️ Solar Panel Energy Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Generate data
    df = generate_all_seasons_data()
    
    # Sidebar controls
    st.sidebar.markdown("## 🎛️ Dashboard Controls")
    
    # Season filter
    selected_seasons = st.sidebar.multiselect(
        "Select Seasons:",
        options=['summer', 'monsoon', 'winter'],
        default=['summer', 'monsoon', 'winter']
    )
    
    # Month filter
    available_months = df[df['season'].isin(selected_seasons)]['month'].unique()
    selected_months = st.sidebar.multiselect(
        "Select Months:",
        options=available_months,
        default=available_months
    )
    
    # Filter data
    filtered_df = df[
        (df['season'].isin(selected_seasons)) & 
        (df['month'].isin(selected_months))
    ]
    
    # KWH range filter
    kwh_min, kwh_max = st.sidebar.slider(
        "KWH Range:",
        min_value=float(df['kwh'].min()),
        max_value=float(df['kwh'].max()),
        value=(float(df['kwh'].min()), float(df['kwh'].max())),
        step=0.1
    )
    
    filtered_df = filtered_df[
        (filtered_df['kwh'] >= kwh_min) & 
        (filtered_df['kwh'] <= kwh_max)
    ]
    
    # Key Metrics
    st.markdown('<h2 class="sub-header">📊 Key Performance Metrics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Data Points",
            value=f"{len(filtered_df):,}",
            delta=f"{len(filtered_df) - len(df):,}"
        )
    
    with col2:
        avg_kwh = filtered_df['kwh'].mean()
        st.metric(
            label="Average KWH",
            value=f"{avg_kwh:.2f}",
            delta=f"{avg_kwh - df['kwh'].mean():.2f}"
        )
    
    with col3:
        max_kwh = filtered_df['kwh'].max()
        st.metric(
            label="Peak KWH",
            value=f"{max_kwh:.2f}",
            delta=f"{max_kwh - df['kwh'].max():.2f}"
        )
    
    with col4:
        avg_irradiance = filtered_df['irradiance'].mean()
        st.metric(
            label="Avg Irradiance",
            value=f"{avg_irradiance:.1f}",
            delta=f"{avg_irradiance - df['irradiance'].mean():.1f}"
        )
    
    # Main visualizations
    st.markdown('<h2 class="sub-header">📈 Energy Production Analysis</h2>', unsafe_allow_html=True)
    
    # Row 1: KWH trends
    col1, col2 = st.columns(2)
    
    with col1:
        # KWH by Season
        fig_season = px.box(
            filtered_df, 
            x='season', 
            y='kwh',
            color='season',
            title='KWH Distribution by Season',
            color_discrete_map={
                'summer': '#FF6B35',
                'monsoon': '#2E86AB',
                'winter': '#A23B72'
            }
        )
        fig_season.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        st.plotly_chart(fig_season, use_container_width=True)
    
    with col2:
        # KWH by Month
        monthly_avg = filtered_df.groupby('month')['kwh'].mean().reset_index()
        fig_month = px.bar(
            monthly_avg,
            x='month',
            y='kwh',
            title='Average KWH by Month',
            color='kwh',
            color_continuous_scale='Viridis'
        )
        fig_month.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        st.plotly_chart(fig_month, use_container_width=True)
    
    # Row 2: Environmental factors
    st.markdown('<h2 class="sub-header">🌡️ Environmental Factors Impact</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Irradiance vs KWH
        fig_irr = px.scatter(
            filtered_df,
            x='irradiance',
            y='kwh',
            color='season',
            size='ambient_temperature',
            hover_data=['humidity', 'wind_speed'],
            title='Irradiance vs KWH Production',
            color_discrete_map={
                'summer': '#FF6B35',
                'monsoon': '#2E86AB',
                'winter': '#A23B72'
            }
        )
        fig_irr.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_irr, use_container_width=True)
    
    with col2:
        # Temperature vs KWH
        fig_temp = px.scatter(
            filtered_df,
            x='ambient_temperature',
            y='kwh',
            color='season',
            size='wind_speed',
            hover_data=['humidity', 'irradiance'],
            title='Temperature vs KWH Production',
            color_discrete_map={
                'summer': '#FF6B35',
                'monsoon': '#2E86AB',
                'winter': '#A23B72'
            }
        )
        fig_temp.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Row 3: Correlation and distribution
    st.markdown('<h2 class="sub-header">🔍 Advanced Analytics</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Correlation heatmap
        numeric_cols = ['irradiance', 'humidity', 'wind_speed', 'ambient_temperature', 'tilt_angle', 'kwh']
        corr_matrix = filtered_df[numeric_cols].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            title='Feature Correlation Matrix',
            aspect='auto',
            color_continuous_scale='RdBu_r'
        )
        fig_corr.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with col2:
        # KWH distribution
        fig_dist = px.histogram(
            filtered_df,
            x='kwh',
            color='season',
            title='KWH Distribution',
            marginal='box',
            color_discrete_map={
                'summer': '#FF6B35',
                'monsoon': '#2E86AB',
                'winter': '#A23B72'
            }
        )
        fig_dist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Data table
    st.markdown('<h2 class="sub-header">📋 Data Explorer</h2>', unsafe_allow_html=True)
    
    # Summary statistics
    st.markdown("### Summary Statistics")
    st.dataframe(filtered_df.describe(), use_container_width=True)
    
    # Raw data with search and filter
    st.markdown("### Raw Data")
    st.dataframe(
        filtered_df.head(1000),  # Limit for performance
        use_container_width=True,
        height=300
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='solar_panel_data_filtered.csv',
        mime='text/csv',
        use_container_width=True
    )
    
    # Info box
    st.markdown("""
    <div class="info-box">
        <h4>🔬 About This Dataset</h4>
        <p>This synthetic dataset simulates solar panel energy production across different seasons with realistic environmental factors. 
        The data includes irradiance, humidity, wind speed, temperature, and tilt angle measurements with corresponding KWH output calculations.</p>
        <ul>
            <li><strong>Summer:</strong> High irradiance, low humidity, optimal conditions</li>
            <li><strong>Monsoon:</strong> Low irradiance, high humidity, challenging conditions</li>
            <li><strong>Winter:</strong> Moderate irradiance, variable humidity, cooler temperatures</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
