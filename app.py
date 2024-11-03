import pandas as pd
import streamlit as st
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np

# Configuración inicial de la página
st.set_page_config(page_title="Análisis Fantasy PL", layout="wide")

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

# Wildcards
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

# Agregar puntos perdidos (15 puntos en GW10 para todos)
df_long['Lost_Points'] = 0
df_long.loc[df_long['Gameweek'] == 10, 'Lost_Points'] = 15

# Calcular puntos corregidos
df_long['Corrected_Points'] = df_long['Points'] - df_long['Lost_Points']

# Calcular puntos totales corregidos
df_long['Total_Points'] = df_long.groupby('TEAM')['Corrected_Points'].cumsum()

# Calcular posiciones
df_long['Position'] = df_long.groupby('Gameweek')['Total_Points'].rank(method='min', ascending=False)

# Título principal
st.title('Análisis Fantasy Premier League')

# Filtros superiores
col1, col2 = st.columns(2)
with col1:
    gw_range = st.select_slider(
        'Rango de Jornadas',
        options=range(1, df_long['Gameweek'].max() + 1),
        value=(1, df_long['Gameweek'].max())
    )
with col2:
    container = st.container()
    select_all = st.checkbox("Seleccionar todos los equipos")
    if select_all:
        selected_teams = container.multiselect(
            "Equipos seleccionados",
            options=df_long['TEAM'].unique(),
            default=df_long['TEAM'].unique()
        )
    else:
        selected_teams = container.multiselect(
            "Equipos seleccionados",
            options=df_long['TEAM'].unique()
        )

# 1. Tabla principal con filtros
filtered_df = df_long[
    (df_long['Gameweek'].between(gw_range[0], gw_range[1])) & 
    (df_long['TEAM'].isin(selected_teams))
].copy()

# Función para estilizar la tabla
def highlight_wildcards(df):
    styles = []
    for idx, row in df.iterrows():
        team = row['TEAM']
        gw = row['Gameweek']
        used_wildcard = any((wildcards_df['TEAM'] == team) & 
                           (wildcards_df['Gameweek'] == f'GW{gw}'))
        if used_wildcard:
            styles.append('background-color: lightgreen')
        else:
            styles.append('')
    return styles

show_single_gw = st.checkbox('Mostrar solo la última jornada seleccionada')
if show_single_gw:
    display_df = filtered_df[filtered_df['Gameweek'] == gw_range[1]]
    st.header(f'Tabla de la Liga - Jornada {gw_range[1]}')
else:
    display_df = filtered_df
    st.header(f'Tabla de la Liga - Jornadas {gw_range[0]} a {gw_range[1]}')

styled_df = display_df.sort_values(['Gameweek', 'Position'])[
    ['TEAM', 'MANAGER', 'Corrected_Points', 'Total_Points', 'Position']
].style.apply(highlight_wildcards, axis=1)
st.dataframe(styled_df)

# 2. Evolución de puntos
st.header('Evolución de Puntos')
col1, col2 = st.columns([4, 1])
with col1:
    fig_points = go.Figure()
    for team in selected_teams:
        team_data = filtered_df[filtered_df['TEAM'] == team]
        fig_points.add_trace(
            go.Scatter(x=team_data['Gameweek'], 
                      y=team_data['Corrected_Points'],
                      name=team)
        )
    fig_points.update_layout(
        title='Puntos por Jornada',
        xaxis_title='Jornada',
        yaxis_title='Puntos'
    )
    st.plotly_chart(fig_points, use_container_width=True)

with col2:
    st.write("Opacidad")
    for team in selected_teams:
        opacity = st.slider(f'{team}', 0.0, 1.0, 1.0, key=f'points_{team}')
        fig_points.update_traces(opacity=opacity, selector=dict(name=team))

# 3. Evolución de posiciones
st.header('Evolución de Posiciones')
col1, col2 = st.columns([4, 1])
with col1:
    fig_position = go.Figure()
    for team in selected_teams:
        team_data = filtered_df[filtered_df['TEAM'] == team]
        fig_position.add_trace(
            go.Scatter(x=team_data['Gameweek'], 
                      y=team_data['Position'],
                      name=team)
        )
    fig_position.update_layout(
        title='Posiciones por Jornada',
        xaxis_title='Jornada',
        yaxis_title='Posición',
        yaxis={'autorange': 'reversed'}
    )
    st.plotly_chart(fig_position, use_container_width=True)

with col2:
    st.write("Opacidad")
    for team in selected_teams:
        opacity = st.slider(f'{team}', 0.0, 1.0, 1.0, key=f'pos_{team}')
        fig_position.update_traces(opacity=opacity, selector=dict(name=team))

# 4. Distribución de puntos por equipo
st.header('Distribución de Puntos por Equipo')
fig_box_teams = px.box(
    filtered_df,
    x='TEAM',
    y='Corrected_Points',
    title='Distribución de Puntos por Equipo'
)
fig_box_teams.update_layout(
    xaxis_title='Equipo',
    yaxis_title='Puntos'
)
st.plotly_chart(fig_box_teams, use_container_width=True)

# 4. Distribución de puntos por GW  
st.header('Distribución de Puntos por Fecha')
fig_box_gw = px.box(
    filtered_df,
    x='Gameweek',
    y='Corrected_Points',
    title='Distribución de Puntos por Fecha'
)
fig_box_gw.update_layout(
    xaxis_title='Fecha',
    yaxis_title='Puntos'
)
st.plotly_chart(fig_box_gw, use_container_width=True)


# 6. Estadísticas de la liga
st.header('Estadísticas de la Liga')
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Promedio de la Liga", f"{filtered_df['Corrected_Points'].mean():.1f}")

with col2:
    max_points = filtered_df['Corrected_Points'].max()
    max_team = filtered_df.loc[filtered_df['Corrected_Points'] == max_points, 'TEAM'].iloc[0]
    max_gw = filtered_df.loc[filtered_df['Corrected_Points'] == max_points, 'Gameweek'].iloc[0]
    st.metric("Máxima Puntuación", f"{max_points} ({max_team}, GW{max_gw})")

with col3:
    min_points = filtered_df['Corrected_Points'].min()
    min_team = filtered_df.loc[filtered_df['Corrected_Points'] == min_points, 'TEAM'].iloc[0]
    min_gw = filtered_df.loc[filtered_df['Corrected_Points'] == min_points, 'Gameweek'].iloc[0]
    st.metric("Mínima Puntuación", f"{min_points} ({min_team}, GW{min_gw})")

  