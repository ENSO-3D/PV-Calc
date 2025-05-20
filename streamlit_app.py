import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun

# --- Default parameters ---
defaults = {
    'annual_usage': 12000.0,
    'batt_capacity': 14.33,
    'batt_rt_eff': 0.92,
    'DoD_pct': 0.8,
    'low_price': None,
    'high_price': None,
    'transfer_cost': 0.307,
    'energy_tax': 0.5488,
    'vat_rate': 0.25,
    'latitude': 55.6,
    'longitude': 13.0,
    'tilt': 45,
    'azimuth': 180,
    'losses_pct': 14,
    'panel_count': 12,
    'panel_watt': 395
}

st.title("PV + ESS ROI Simulator")

# --- Sidebar for inputs ---
st.sidebar.header("System Parameters")
annual_usage = st.sidebar.number_input("Annual consumption (kWh)", value=defaults['annual_usage'])
panel_count  = st.sidebar.number_input("Number of panels", value=defaults['panel_count'], step=1)
panel_watt   = st.sidebar.number_input("Panel wattage (W)", value=defaults['panel_watt'])
batt_capacity= st.sidebar.number_input("Battery capacity (kWh)", value=defaults['batt_capacity'])
batt_rt_eff  = st.sidebar.slider("Battery round-trip efficiency (%)", 50, 100, int(defaults['batt_rt_eff']*100))/100.0
n_dod        = st.sidebar.slider("Depth of discharge (%)", 10, 100, int(defaults['DoD_pct']*100))/100.0
transfer_cost= st.sidebar.number_input("Energy transfer cost (SEK/kWh)", value=defaults['transfer_cost'])
energy_tax   = st.sidebar.number_input("Energy tax (SEK/kWh)", value=defaults['energy_tax'])
vat_rate     = st.sidebar.slider("VAT rate (%)", 0, 50, int(defaults['vat_rate']*100))/100.0
latitude     = st.sidebar.number_input("Latitude", value=defaults['latitude'])
longitude    = st.sidebar.number_input("Longitude", value=defaults['longitude'])
tilt         = st.sidebar.slider("Tilt angle (°)", 0, 90, defaults['tilt'])
azimuth      = st.sidebar.slider("Azimuth (°)", 0, 360, defaults['azimuth'])
losses_pct   = st.sidebar.slider("System losses (%)", 0, 50, defaults['losses_pct'])

# --- Compute PVGIS monthly yields ---
@st.cache
 def fetch_pvgis(lat, lon, capacity, tilt, azimuth, losses):
    import requests
    url = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
    params = {
        'lat': lat, 'lon': lon, 'peakpower': capacity,
        'mountingplace': 'free', 'angle': tilt,
        'aspect': azimuth, 'loss': losses,
        'outputformat': 'json', 'browser': 0
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()['outputs']['monthly']['fixed']
    df = pd.DataFrame(data)
    df['PV'] = df['E_m']
    return df.set_index('month')['PV']

capacity = panel_count * panel_watt/1000.0
pvgis_monthly = fetch_pvgis(latitude, longitude, capacity, tilt, azimuth, losses_pct)

# --- Build df_monthly ---
months = np.arange(1,13)
# default consumption weights
default_wt = 1 + 0.2 * np.cos((months-1)/11 * 2*np.pi)
default_wt /= default_wt.sum()
# user shape = default
cons = default_wt * annual_usage

df_monthly = pd.DataFrame({
    'Month': months,
    'Consumption': cons,
    'PV': pvgis_monthly.values
})

# --- Generate hourly series, dispatch, and savings (omitted for brevity) ---
# You would bring in your existing simulation functions here.

st.subheader("Monthly Summary")
st.table(df_monthly.set_index('Month'))

# Placeholder
st.info("Simulated savings & charts will appear here once dispatch functions are integrated.")
