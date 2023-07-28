# ================================================================
# ||||||||||||||||||||||| === LIBRARY === |||||||||||||||||||||||||
# ================================================================

import pandas as pd
import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
import folium

from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image

st.set_page_config( page_title='Visão Entregadores', page_icon='🔎', layout='wide' ) 
# layout='wide' faz usar todo o espaço do monitor

# ================================================================
# ||||||||||||||||||||| === FUNCTIONS === ||||||||||||||||||||||||
# ================================================================

def top_delivers( df1, top_asc ):
    
#######    
    """
        Esta função recebe um DF e top_asc contendo "True" ou "False".
        Ela retornara um DF com o top 10 entregadores mais Rapidos ou 
        mais Centos por Cidade.
    """
#######    
    
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                           .groupby(['City', 'Delivery_person_ID'])
                           .max()
                           .sort_values(['City', 'Time_taken(min)'], ascending=top_asc )
                           .reset_index() )
            
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            
    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )

    return df3
    
# ==================================== ::

def clean_code( df1 ):
    
    # 1. Limpeza de 'NaN ' das colunas selecionadas
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    
    # 2. convertendo a coluna 'Delivery_person_Ratings' de texto para num decimal
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float)
    
    # 3. convertendo a coluna 'Order_Date' de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    
    # 4. convertendo 'multiple_deliveries' de texto para numero inteiro
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ' )
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    # 6. Removendo os espacos dentro de strings/texto/object
    df1.loc[ :, 'ID' ] = df1.loc[ :, 'ID' ].str.strip()
    df1.loc[ :, 'Road_traffic_density'] = df1.loc[ :, 'Road_traffic_density' ].str.strip()
    df1.loc[ :, 'Type_of_order'] = df1.loc[ :, 'Type_of_order' ].str.strip()
    df1.loc[ :, 'Type_of_vehicle'] = df1.loc[ :, 'Type_of_vehicle' ].str.strip()
    df1.loc[ :, 'City' ] = df1.loc[ :, 'City' ].str.strip()
    df1.loc[ :, 'Festival' ] = df1.loc[ :, 'Festival' ].str.strip()
    
    # 7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1
    
# =================================================================================
# |||||||||||||||| === INICIO DA ESTRUTURA LÓGICA DO CÓDIGO  === ||||||||||||||||||
# =================================================================================
# =================================== :: IMPORT DATASET ::
#                                        -------------
df = pd.read_csv( 'dataset/train.csv' )

# =================================== :: CLEAN DATASET ::
#                                        -------------
df1 = clean_code( df )

# =================================== :: SIDEBAR ::
#                                        -------
st.header( 'Marketplace - Visão Entregadores' )

#image_path = '/Users/leona/Documents/repos/jupyterlab/logo.PNG'
image = Image.open( 'logo.PNG' )
st.sidebar.image( image, width=120 )


st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" ) # Cria uma linha horizontal no sidebar

# ==================================== ::

st.sidebar.markdown( '## Seleciona uma data limite' )
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime( 2022, 4, 13 ),
    min_value=datetime.datetime(2022, 2, 11 ),
    max_value=datetime.datetime(2022, 4, 6 ),
    format='DD-MM-YYYY' )
st.sidebar.markdown( """___""" ) 
    
# ==================================== ::

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """___""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#=================================================================
#                         LAYOUT NO STREAMLIT
#=================================================================

tab1, tab2, tab3 = st.tabs( ['Visao Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        
        with col1:       
            # A Maior idade dos entregadores
            max_age = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior Idade', max_age )
            
        with col2:
            # A Menor idade dos entregadores
            min_age = df1['Delivery_person_Age'].min()
            col2.metric( 'Menor Idade', min_age )
            
        with col3:
            # A Melhor condição de veiculo
            max_vehicle_condition = df1['Vehicle_condition'].max()
            col3.metric( 'Melhor condição de veiculos', max_vehicle_condition )
            
        with col4:
            # A Pior condição de veiculo
            min_vehicle_condition = df1['Vehicle_condition'].min()
            col4.metric( ' Pior condição', min_vehicle_condition )
            
# ==================================== ::

    with st.container():
        st.markdown( """___""" )
        st.title( 'Avaliações' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.subheader( 'Avaliação média por entregador' )
            df_avg_ratings_per_deliver = (df1.loc[:, ['Delivery_person_ID','Delivery_person_Ratings']]
                                             .groupby('Delivery_person_ID')
                                             .mean()
                                             .reset_index())
            st.dataframe( df_avg_ratings_per_deliver, height=600 )

            
        with col2:
            st.subheader( 'Avaliação média por transito' )
            
            df_avg_std_rating_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                                                .groupby('Road_traffic_density')
                                                .agg( {'Delivery_person_Ratings': ['mean', 'std'] } ) )
            # mudanca de nome das colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            # reset do index
            df_avg_std_rating_by_traffic.reset_index()
            st.dataframe( df_avg_std_rating_by_traffic )

            st.markdown( """___""" )
            with st.container():
                st.subheader( 'Avaliação média por condição climatica' )
                df_avg_std_rating_by_weather = ( df1.loc[:, ['Delivery_person_Ratings','Weatherconditions']]
                                                    .groupby('Weatherconditions')
                                                    .agg( {'Delivery_person_Ratings': ['mean', 'std'] } ) )
                # mudanca de nome das colunas
                df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
                # reset do index
                df_avg_std_rating_by_weather.reset_index()
                st.dataframe( df_avg_std_rating_by_weather )
    
                
    #            st.markdown( """___""" )
    #           with st.container():
    #                st.subheader( 'Avaliação média por condição climatica' )
            
        st.markdown( """___""" )
        
# ..........................

    with st.container():
        st.title(' Velocidade de Entrega' )
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.subheader( 'Top Entregadores mais rapidos' )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )


        with col2:
            st.subheader( 'Top Entregadores mais lentos' )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )
            
# ====================================================================================================::
# ====================================================================================================::
            



# Exemplo de modularização da primeira coluna
#def calcule_big_number( col, operation):
#                if operation == 'max':
#                    results = df1.loc[:, col].max()
#                elif operation == 'min':
#                    results = df1.loc[:, col].min()
#                    
#                
#                return results




















