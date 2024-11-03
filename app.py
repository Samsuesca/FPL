import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuración inicial de la página
st.set_page_config(page_title="Fantasy PL Analysis", layout="wide")

# Datos
data = {
    'TEAM': ['FPLcolombia', 'Ben', 'AtlNacional', 'terror de las enanas', 'SamChelsea', 
            'Falso 9', 'Aston Birras', 'Arsenal Giraldo', 'Terreneitor', 'team1', 
            'JD team', 'Batipibe', 'JMfc'],
    'MANAGER': ['CHRISTIAN POSSO', 'JUAN ESTEBAN RIVERA', 'ARLEN GUARIN', 'ANDRES RINCON',
               'SAMUEL SUESCA', 'NICOLAS MANCERA', 'DANIEL MARQUEZ', 'SEBASTIAN GIRALDO',
               'SANTIAGO VELASQUEZ', 'GABRIEL SUAREZ', 'DIEGO MONTOYA', 'BRAYAN PINEDA',
               'JAIRO MONTOYA'],
    'GW1': [81, 67, 69, 72, 39, 67, 62, 71, 66, 47, 47, 64, 66],
    'GW2': [86, 74, 83, 58, 72, 83, 80, 55, 70, 86, 43, 73, 60],
    'GW3': [84, 78, 95, 67, 41, 71, 76, 75, 91, 54, 55, 64, 56],
    'GW4': [54, 59, 60, 57, 27, 64, 52, 38, 33, 65, 59, 52, 38],
    'GW5': [61, 70, 67, 52, 81, 75, 55, 50, 73, 54, 69, 48, 55],
    'GW6': [47, 30, 32, 85, 68, 25, 31, 44, 54, 65, 47, 41, 64],
    'GW7': [48, 40, 56, 39, 60, 43, 27, 44, 40, 39, 43, 39, 26],
    'GW8': [46, 45, 29, 34, 42, 18, 41, 55, 24, 32, 48, 30, 31],
    'GW9': [52, 62, 53, 60, 85, 54, 73, 57, 46, 40, 54, 60, 69],
    'GW10': [22, 40, 22, 29, 47, 27, 39, 32, 24, 15, 28, 37, 30]
}

# Crear DataFrame inicial
df = pd.DataFrame(data)

# Convertir a formato largo
df_long = df.melt(id_vars=['TEAM', 'MANAGER'], 
                  var_name='Gameweek', 
                  value_name='Points')

# Convertir Gameweek a numérico
df_long['Gameweek'] = df_long['Gameweek'].str.replace('GW', '').astype(int)

# Calcular puntos totales
df_long['Total_Points'] = df_long.groupby('TEAM')['Points'].cumsum()

# Calcular posiciones
df_long['Position'] = df_long.groupby('Gameweek')['Total_Points'].rank(method='min', ascending=False)

# Título principal
st.title('Fantasy Premier League Analysis')

# 1. Tabla actual
st.header('Current League Standings')
latest_gw = df_long['Gameweek'].max()
current_standings = df_long[df_long['Gameweek'] == latest_gw].sort_values('Position')
st.dataframe(current_standings[['Position', 'TEAM', 'MANAGER', 'Points', 'Total_Points']])

# 2. Evolución de puntos
st.header('Points Evolution')
fig_points = px.line(df_long, 
                     x='Gameweek', 
                     y='Points', 
                     color='TEAM',
                     title='Points per Gameweek by Team')
st.plotly_chart(fig_points, use_container_width=True)

# 3. Evolución de posiciones
st.header('Position Evolution')
fig_position = px.line(df_long, 
                       x='Gameweek', 
                       y='Position', 
                       color='TEAM',
                       title='Position Evolution by Team')
fig_position.update_yaxes(autorange="reversed")
st.plotly_chart(fig_position, use_container_width=True)

# 4. Promedio por equipo
st.header('Team Averages')
avg_by_team = df_long.groupby('TEAM')['Points'].mean().sort_values(ascending=False)
fig_avg = px.bar(avg_by_team, title='Average Points per Team')
st.plotly_chart(fig_avg, use_container_width=True)

# 5. Estadísticas de la liga
st.header('League Statistics')
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("League Average", f"{df_long['Points'].mean():.1f}")

with col2:
    max_points = df_long['Points'].max()
    max_team = df_long.loc[df_long['Points'] == max_points, 'TEAM'].iloc[0]
    max_gw = df_long.loc[df_long['Points'] == max_points, 'Gameweek'].iloc[0]
    st.metric("Highest Score", f"{max_points} ({max_team}, GW{max_gw})")

with col3:
    min_points = df_long['Points'].min()
    min_team = df_long.loc[df_long['Points'] == min_points, 'TEAM'].iloc[0]
    min_gw = df_long.loc[df_long['Points'] == min_points, 'Gameweek'].iloc[0]
    st.metric("Lowest Score", f"{min_points} ({min_team}, GW{min_gw})")

# 6. Distribución de puntos por gameweek
st.header('Points Distribution by Gameweek')
fig_box = px.box(df_long, x='Gameweek', y='Points')
st.plotly_chart(fig_box, use_container_width=True)