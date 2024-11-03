  
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

# Wildcards (agregar los gameweeks donde se usó wildcard)
wildcards = {
    'TEAM': ['Ben', 'terror de las enanas','Arsenal Giraldo','FPLcolombia','JMfc'],
    'Gameweek': ['GW6', 'GW3','GW9','GW6','GW6']
}
wildcards_df = pd.DataFrame(wildcards)

# Crear DataFrame inicial
df = pd.DataFrame(data)

# Convertir a formato largo
df_long = df.melt(id_vars=['TEAM', 'MANAGER'], 
                  var_name='Gameweek', 
                  value_name='Points')

# Convertir Gameweek a numérico
df_long['Gameweek'] = df_long['Gameweek'].str.replace('GW', '').astype(int)

# Agregar columna de wildcard
df_long['Wildcard'] = 0
for _, row in wildcards_df.iterrows():
    gw = int(row['Gameweek'].replace('GW', ''))
    df_long.loc[(df_long['TEAM'] == row['TEAM']) & (df_long['Gameweek'] == gw), 'Wildcard'] = 1

# Calcular puntos totales
df_long['Total_Points'] = df_long.groupby('TEAM')['Points'].cumsum()

# Calcular posiciones
df_long['Position'] = df_long.groupby('Gameweek')['Total_Points'].rank(method='min', ascending=False)

# Título principal
st.title('Fantasy Premier League Analysis')

# Filtros superiores
col1, col2 = st.columns(2)
with col1:
    selected_gw = st.slider('Select Gameweek', min_value=1, max_value=df_long['Gameweek'].max(), value=df_long['Gameweek'].max())
with col2:
    selected_teams = st.multiselect('Select Teams', options=df_long['TEAM'].unique(), default=df_long['TEAM'].unique())

# 1. Tabla principal con filtros
st.header('League Table')
filtered_df = df_long[
    (df_long['Gameweek'] <= selected_gw) & 
    (df_long['TEAM'].isin(selected_teams))
].copy()

if st.checkbox('Show only selected Gameweek'):
    display_df = filtered_df[filtered_df['Gameweek'] == selected_gw]
else:
    display_df = filtered_df

st.dataframe(
    display_df.sort_values(['Gameweek', 'Position'])[
        ['Gameweek', 'Position', 'TEAM', 'MANAGER', 'Points', 'Total_Points', 'Wildcard']
    ]
)

# 2. Evolución de puntos con opacidad
st.header('Points Evolution')
fig_points = go.Figure()
for team in selected_teams:
    team_data = filtered_df[filtered_df['TEAM'] == team]
    opacity = st.sidebar.slider(f'Opacity for {team}', 0.0, 1.0, 1.0)
    fig_points.add_trace(
        go.Scatter(x=team_data['Gameweek'], 
                  y=team_data['Points'],
                  name=team,
                  opacity=opacity)
    )
fig_points.update_layout(title='Points per Gameweek by Team')
st.plotly_chart(fig_points, use_container_width=True)

# 3. Evolución de posiciones con opacidad
st.header('Position Evolution')
fig_position = go.Figure()
for team in selected_teams:
    team_data = filtered_df[filtered_df['TEAM'] == team]
    opacity = st.sidebar.slider(f'Position opacity for {team}', 0.0, 1.0, 1.0)
    fig_position.add_trace(
        go.Scatter(x=team_data['Gameweek'], 
                  y=team_data['Position'],
                  name=team,
                  opacity=opacity)
    )
fig_position.update_layout(
    title='Position Evolution by Team',
    yaxis={'autorange': 'reversed'}
)
st.plotly_chart(fig_position, use_container_width=True)

# 4. Boxplots por jugador
st.header('Points Distribution by Team')
fig_box_teams = px.box(
    filtered_df,
    x='TEAM',
    y='Points',
    title='Points Distribution by Team'
)
st.plotly_chart(fig_box_teams, use_container_width=True)

# 5. Estadísticas de la liga
st.header('League Statistics')
col1, col2, col3 = st.columns(3)

stats_df = filtered_df[filtered_df['Gameweek'] <= selected_gw]

with col1:
    st.metric("League Average", f"{stats_df['Points'].mean():.1f}")

with col2:
    max_points = stats_df['Points'].max()
    max_team = stats_df.loc[stats_df['Points'] == max_points, 'TEAM'].iloc[0]
    max_gw = stats_df.loc[stats_df['Points'] == max_points, 'Gameweek'].iloc[0]
    st.metric("Highest Score", f"{max_points} ({max_team}, GW{max_gw})")

with col3:
    min_points = stats_df['Points'].min()
    min_team = stats_df.loc[stats_df['Points'] == min_points, 'TEAM'].iloc[0]
    min_gw = stats_df.loc[stats_df['Points'] == min_points, 'Gameweek'].iloc[0]
    st.metric("Lowest Score", f"{min_points} ({min_team}, GW{min_gw})")
