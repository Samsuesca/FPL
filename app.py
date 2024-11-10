import pandas as pd
import streamlit as st
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
import requests
import time
from datetime import datetime

class FPLData:
    def __init__(self):
        self.session = requests.session()
        self.base_url = "https://fantasy.premierleague.com/api/"
        self.general_data = None

    # Primero, añadamos un método para obtener el nombre de la liga
    def get_league_info(self,league_id):
        """Obtiene información básica de la liga"""
        url = f"{self.base_url}leagues-classic/{league_id}/"
        r = self.session.get(url)
        return r.json()

    def gln(self,lid):
        return self.get_league_info(lid)['name']
    '''
    def get_league_name(self, league_id):
        """Obtiene nombre de la liga"""
        league_info = 
        return league_info['name']
    '''
    def get_general_data(self):
        """Obtiene datos generales de la FPL"""
        if not self.general_data:
            url = f"{self.base_url}bootstrap-static/"
            r = self.session.get(url)
            self.general_data = r.json()
        return self.general_data
    
    def get_league_standings(self, league_id, page=1):
        """Obtiene la clasificación de una liga"""
        url = f"{self.base_url}leagues-classic/{league_id}/standings/?page_standings={page}"
        r = self.session.get(url)
        return r.json()
    
    def get_manager_history(self, team_id):
        """Obtiene el historial de un manager"""
        url = f"{self.base_url}entry/{team_id}/history/"
        r = self.session.get(url)
        return r.json()
    
    def get_team_picks(self, team_id, gameweek):
        """Obtiene las selecciones de un equipo para una gameweek"""
        url = f"{self.base_url}entry/{team_id}/event/{gameweek}/picks/"
        r = self.session.get(url)
        return r.json()
    
    def get_player_details(self, player_id):
        """Obtiene detalles de un jugador"""
        url = f"{self.base_url}element-summary/{player_id}/"
        r = self.session.get(url)
        return r.json()
   
    # Y modifiquemos el process_league_data para incluir más detalles
    def process_league_data(self, league_id):
        # Obtener datos generales
        general_data = self.get_general_data()
        players_df = pd.DataFrame(general_data['elements'])
        teams_df = pd.DataFrame(general_data['teams'])
        events_df = pd.DataFrame(general_data['events'])
        
        # Obtener datos de la liga
        league_data = self.get_league_standings(league_id)
        league_info = self.get_league_info(league_id)
        
        if not league_data or 'standings' not in league_data:
            st.error("No se pudieron obtener los datos de la liga")
            return None
            
        # Procesar managers y sus equipos
        managers_data = []
        managers_summary = []
        current_event = events_df[events_df['is_current']].iloc[0]['id'] if not events_df[events_df['is_current']].empty else events_df['id'].max()
        
        with st.spinner('Cargando datos de los equipos...'):
            progress_bar = st.progress(0)
            
            for i, entry in enumerate(league_data['standings']['results']):
                team_id = entry['entry']
                try:
                    # Obtener historial del equipo
                    history = self.get_manager_history(team_id)
                    if history and 'current' in history:
                        wildcards_used = []
                        chips_used = history.get('chips', [])
                        for chip in chips_used:
                            if chip['name'] == 'wildcard':
                                wildcards_used.append(chip['event'])
                        
                        for gw in history['current']:
                            gw_data = {
                                'manager_id': team_id,
                                'manager_name': entry['player_name'],
                                'team_name': entry['entry_name'],
                                'gameweek': gw['event'],
                                'total_points': gw['total_points'],
                                'gameweek_points': gw['points'],
                                'transfers': gw['event_transfers'],
                                'transfer_cost': gw['event_transfers_cost'],
                                'bank': gw['bank'],
                                'team_value': gw['value'],
                                'wildcard_used': gw['event'] in wildcards_used,
                                'overall_rank': gw['overall_rank'],
                                'rank': gw['rank']
                            }
                            
                            # Obtener alineación para esta gameweek
                            picks_data = self.get_team_picks(team_id, gw['event'])
                            if picks_data and 'picks' in picks_data:
                                squad_data = []
                                for pick in picks_data['picks']:
                                    player_info = players_df[players_df['id'] == pick['element']].iloc[0]
                                    team_info = teams_df[teams_df['id'] == player_info['team']].iloc[0]
                                    
                                    squad_data.append({
                                        'player_id': pick['element'],
                                        'player_name': f"{player_info['first_name']} {player_info['second_name']}",
                                        'player_team': team_info['name'],
                                        'position': pick['position'],
                                        'is_captain': pick['is_captain'],
                                        'is_vice_captain': pick['is_vice_captain'],
                                        'multiplier': pick['multiplier']
                                    })
                                
                                gw_data['squad'] = squad_data
                            
                            managers_data.append(gw_data)
                    
                    time.sleep(0.5)  # Respetar rate limits
                    progress_bar.progress((i + 1) / len(league_data['standings']['results']))
                    
                except Exception as e:
                    st.warning(f"Error obteniendo datos para el equipo {team_id}: {str(e)}")
                    continue
        
        df = pd.DataFrame(managers_data)
        
        return df

# Configuración de la página
st.set_page_config(page_title="Fantasy Premier League Analytics", layout="wide")

# Inicializar clase de datos
@st.cache_resource
def get_fpl_data():
    return FPLData()

fpl = get_fpl_data()

# Cargar datos
LEAGUE_ID = "1126029"

@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_league_name():
    return fpl.gln(LEAGUE_ID)


@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_league_data():
    return fpl.process_league_data(LEAGUE_ID)

# Cargar datos
df = load_league_data()

league_name = "Mulas" #'load_league_name()'

# En la sección principal
st.title(f'🏆 {league_name}')
st.markdown(f"""
### Liga: {lleague_name }
Temporada 2023/24 • {len(df['team_name'].unique())} equipos
""")
st.markdown(f"""
Este dashboard muestra estadísticas detalladas de {league_name } de Fantasy Premier League.
""")





if df is not None:
    # Filtros superiores
    st.sidebar.header('Filtros')
    
    # Filtro de gameweeks
    all_gameweeks = sorted(df['gameweek'].unique())
    gw_range = st.sidebar.select_slider(
        'Rango de Jornadas',
        options=all_gameweeks,
        value=(min(all_gameweeks), max(all_gameweeks))
    )
    
    # Filtro de managers
    all_managers = sorted(df['team_name'].unique())
    select_all = st.sidebar.checkbox("Seleccionar todos los equipos", value=True)
    if select_all:
        selected_managers = all_managers
    else:
        selected_managers = st.sidebar.multiselect(
            "Equipos seleccionados",
            options=all_managers,
            default=[]
        )
    
    # Filtrar datos
    filtered_df = df[
        (df['gameweek'].between(gw_range[0], gw_range[1])) & 
        (df['team_name'].isin(selected_managers))
    ].copy()

    Métricas principales mejoradas
    latest_gw = filtered_df['gameweek'].max()
    current_gw_data = filtered_df[filtered_df['gameweek'] == latest_gw]

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_points = current_gw_data['gameweek_points'].mean()
        avg_points_prev = filtered_df[filtered_df['gameweek'] == latest_gw - 1]['gameweek_points'].mean()
        st.metric(
            "Promedio de Puntos GW actual", 
            f"{avg_points:.1f}", 
            f"{avg_points - avg_points_prev:+.1f} vs GW anterior"
        )
    
    with col2:
        highest_score_current = current_gw_data.nlargest(1, 'gameweek_points').iloc[0]
        st.metric(
            "Máxima Puntuación GW actual", 
            f"{highest_score_current['gameweek_points']}", 
            f"{highest_score_current['team_name']}"
        )
    
    with col3:
        current_transfers = current_gw_data.groupby('team_name')['transfers'].first()
        most_transfers_current = current_transfers.nlargest(1)
        st.metric(
            "Más Transferencias GW actual", 
            f"{most_transfers_current.values[0]}", 
            f"{most_transfers_current.index[0]}"
        )
    
    with col4:
        current_costs = current_gw_data.groupby('team_name')['transfer_cost'].first()
        highest_cost_current = current_costs.nlargest(1)
        st.metric(
            "Mayor Costo GW actual", 
            f"{highest_cost_current.values[0]}", 
            f"{highest_cost_current.index[0]}"
        )

    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Promedio de Puntos", f"{filtered_df['gameweek_points'].mean():.1f}")
        st.divider()  
        ### promedio de puntos ultimo gameweek
    with col2:
        highest_score = filtered_df.nlargest(1, 'gameweek_points').iloc[0]
        st.metric("Máxima Puntuación", f"{highest_score['gameweek_points']}", f"({highest_score['team_name']}, GW{highest_score['gameweek']})",delta_color="off")
        st.divider()  
        ### MAXIMA PUTUACION EN ESTE GAMEWEEK
    with col3:
        most_transfers = filtered_df.nlargest(1, 'transfers').iloc[0]
        st.metric("Más Transferencias", f"{most_transfers['transfers']}",f"({most_transfers['team_name']}, GW{most_transfers['gameweek']})",delta_color="off")
        st.divider()  
        #### MOST TRANSFERS THIS GAMEWEEK
    with col4:
        highest_cost = filtered_df.nlargest(1, 'transfer_cost').iloc[0]
        st.metric("Mayor Costo", f"{highest_cost['transfer_cost']}",f"({highest_cost['team_name']}, GW{highest_cost['gameweek']})",delta_color="off")
        st.divider()  
        ### MAYOR COSTO THIS GAMEWEEK
        
    
    # Visualizaciones
    tab1, tab2, tab3 = st.tabs(["📈 Rendimiento", "👥 Equipos", "🌟 Capitanes"])
    
    with tab1:
        # Evolución de puntos
        st.subheader('Evolución de Puntos')
        points_df = filtered_df.groupby(['gameweek', 'team_name'])['gameweek_points'].max().reset_index()
        fig_points = px.line(points_df, 
                           x='gameweek', 
                           y='gameweek_points', 
                           color='team_name',
                           title='Puntos por Jornada')
        st.plotly_chart(fig_points, use_container_width=True)
        
        # Posiciones De Cada Gameweek
        st.subheader('Evolución de Posiciones')
        cumulative_df = filtered_df.groupby(['gameweek', 'team_name'])['gameweek_points'].sum().groupby(level=0).rank(ascending=False).reset_index()
        fig_positions = px.line(cumulative_df, 
                              x='gameweek', 
                              y='gameweek_points', 
                              color='team_name',
                              title='Posiciones por Jornada')
        fig_positions.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_positions, use_container_width=True)
        
                # Posiciones acumuladas
        st.subheader('Evolución de Posiciones Acumuladas')
        cumulative_points = df.groupby(['gameweek', 'team_name'])['gameweek_points'].first().groupby('team_name').cumsum().reset_index()
        cumulative_ranks = cumulative_points.groupby('gameweek').rank(ascending=False, method='min')
        cumulative_df = pd.DataFrame({
            'gameweek': cumulative_points['gameweek'],
            'team_name': cumulative_points['team_name'],
            'position': cumulative_ranks
        })
        
        fig_cumulative = px.line(
            cumulative_df,
            x='gameweek',
            y='position',
            color='team_name',
            title='Posiciones Acumuladas por Jornada'
        )
        fig_cumulative.update_layout(
            title_x=0.5,
            yaxis={'autorange': 'reversed'},
            xaxis_title='Jornada',
            yaxis_title='Posición',
        )
        st.plotly_chart(fig_cumulative, use_container_width=True)

    with tab2:
        # Análisis de equipos
        st.subheader('Análisis de Equipos')
        
        # Distribución de puntos
        fig_box = px.box(filtered_df, 
                        x='team_name', 
                        y='gameweek_points',
                        title='Distribución de Puntos por Equipo')
        st.plotly_chart(fig_box, use_container_width=True)
        
        # Transferencias y costos
        transfers_df = filtered_df.groupby('team_name').agg({
            'transfers': 'sum',
            'transfer_cost': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        with col1:
            fig_transfers = px.bar(transfers_df, 
                                 x='team_name', 
                                 y='transfers',
                                 title='Total de Transferencias')
            st.plotly_chart(fig_transfers, use_container_width=True)
        
        with col2:
            fig_costs = px.bar(transfers_df, 
                             x='team_name', 
                             y='transfer_cost',
                             title='Costo Total de Transferencias')
            st.plotly_chart(fig_costs, use_container_width=True)


            # Añadir análisis de wildcards
            st.header('Análisis de Wildcards')
            wildcards_used = df[df['wildcard_used']].groupby(['team_name', 'gameweek']).size().reset_index()
            wildcards_used.columns = ['team_name', 'gameweek', 'count']
            
            fig_wildcards = px.scatter(
                wildcards_used,
                x='gameweek',
                y='team_name',
                size='count',
                title='Uso de Wildcards por Equipo'
            )
            fig_wildcards.update_layout(
                title_x=0.5,
                xaxis_title='Jornada',
                yaxis_title='Equipo',
            )
            st.plotly_chart(fig_wildcards, use_container_width=True)
            
            # Análisis de jugadores
            st.header('Análisis de Jugadores')
            player_stats = df.explode('squad').reset_index(drop=True)
            top_players = player_stats.groupby('player_name').agg({
                'is_captain': 'sum',
                'gameweek_points': 'mean',
                'player_team': 'first'
            }).sort_values('gameweek_points', ascending=False)
            
            fig_players = px.bar(
                top_players.head(15),
                x='player_name',
                y='gameweek_points',
                color='player_team',
                title='Top 15 Jugadores por Promedio de Puntos'
            )
            fig_players.update_layout(
                title_x=0.5,
                xaxis_title='Jugador',
                yaxis_title='Promedio de Puntos',
                showlegend=True
            )
            st.plotly_chart(fig_players, use_container_width=True)
    
    with tab3:
        # Análisis de capitanes
        st.subheader('Análisis de Capitanes')
        captains_df = filtered_df[filtered_df['is_captain']].groupby(['player_name', 'player_team']).size().reset_index(name='times_captain')
        captains_df = captains_df.sort_values('times_captain', ascending=False)
        
        fig_captains = px.bar(captains_df.head(10), 
                            x='player_name', 
                            y='times_captain',
                            color='player_team',
                            title='Jugadores Más Capitaneados')
        st.plotly_chart(fig_captains, use_container_width=True)
        
        # Tabla detallada de capitanes por gameweek
        st.subheader('Capitanes por Jornada')
        captain_details = filtered_df[filtered_df['is_captain']].pivot_table(
            index='gameweek',
            columns='team_name',
            values='player_name',
            aggfunc='first'
        )
        st.dataframe(captain_details)

else:
    st.error("No se pudieron cargar los datos. Por favor, intenta más tarde.")
