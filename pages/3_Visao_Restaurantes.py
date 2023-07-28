# ================================================================
# ||||||||||||||||||||||| === LIBRARY === |||||||||||||||||||||||||
# ================================================================

import pandas as pd
import streamlit as st
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
import folium

from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image

st.set_page_config( page_title='Visão Restaurantes', page_icon='🔎', layout='wide' )

# ================================================================
# ||||||||||||||||||||| === FUNCTIONS === ||||||||||||||||||||||||
# ================================================================

def avg_std_time_on_traffic( df1 ):
    df_aux = ( df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .agg( {'Time_taken(min)': ['mean', 'std'] } ) )
                
    df_aux.columns = ['avg_time', 'std_time']
                
    df_aux = df_aux.reset_index()
                
    fig = px.sunburst( df_aux, path=['City', 'Road_traffic_density'],
                                values='avg_time',
                                color='std_time', color_continuous_scale='RdBu',
                                color_continuous_midpoint=np.average( df_aux['std_time'] ) )
    return fig

# ==================================== ::

def avg_std_time_graph( df1):
    df_aux = ( df1.loc[:, ['Time_taken(min)', 'City']]
                  .groupby('City')
                  .agg( {'Time_taken(min)': ['mean','std']}) )
                    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
        
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',
                                x=df_aux['City'],
                                y=df_aux['avg_time'],
                                error_y=dict( type='data',
                                array=df_aux['std_time'] ) ) )
                    
    fig.update_layout(barmode='group')
    return fig        

# ==================================== ::

def avg_std_time_delivery( df1, festival, op ):
         
    """
        Esta funcao calcula o tempo médio e o desvio padrão
        do tempo de entrega.
        Parametros:
             Input:
                 - df: Dataframe com os dados necessários para o cálculo
                 - festival: Se está ou não dentro do festival
                     'Yes': Esta no festival
                     'No': Não esta no festival
                 - op: Tipo de operação que precisa ser calculado
                      'avg_time': Calcula o tempo médio
                      'std_time': Calcula o desvio padrão do tempo.
              Output:
                  - df: Dataframe com 2 colunas e 1 linha
    """       
    cols = ['Time_taken(min)', 'Festival']
    df_aux = ( df1.loc[:, cols]
                   .groupby('Festival')
                   .agg( {'Time_taken(min)': ['mean','std'] } ) )     

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
        
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == festival, op], 2 )
    return df_aux


# ==================================== ::

def distance( df1, fig ):
    if fig == 'False':
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude' ]
        df1['distance'] = ( df1.loc[:, cols].apply( lambda x: haversine( 
                                                            (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ) )
        avg_distance = np.round( df1['distance'].mean(), 2)
        return avg_distance

    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude' ]
        df1['distance'] = ( df1.loc[:, cols].apply( lambda x: haversine( 
                                                            (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ) )
        avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
        fig = go.Figure( data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0] ) ] )
        
        return fig
    
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
st.header( 'Marketplace - Visão Restaurantes' )

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

#=================================================================::
#                         LAYOUT NO STREAMLIT
#=================================================================::

tab1, tab2, tab3 = st.tabs( ['Visao Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title( "Overal Metrics" )

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = df1.Delivery_person_ID.nunique()
            col1.metric( 'Entregadores Unicos', delivery_unique )
#                         *******************        
        with col2:
            avg_distance = distance ( df1, fig='False' )
            col2.metric( 'Distancia Média', avg_distance )
#                         ***************

        with col3:
            df_aux = avg_std_time_delivery( df1, 'Yes', 'avg_time' )
            col3.metric( 'Tempo Médio', df_aux )
#                         ***********
        
        with col4:
            df_aux = avg_std_time_delivery( df1, 'Yes', 'std_time' )
            col4.metric( 'STD Entrega', df_aux )
#                         ***********          
      
        with col5:
            df_aux = avg_std_time_delivery( df1, 'No', 'avg_time' )
            col5.metric( 'Tempo Médio', df_aux )
#                         ***********  
        
        with col6:
            df_aux = avg_std_time_delivery( df1, 'No', 'std_time' )
            col6.metric( 'STD Entrega', df_aux )
#                         ***********            

# =================================== :: CONTAINER ::
#                                        ---------

    with st.container():
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( """___""" )
            st.subheader( "Distribuição da Distancia" )
#                          *************************         
            df_aux = ( df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order' ]]
                          .groupby( ['City', 'Type_of_order'] )
                          .agg( {'Time_taken(min)': ['mean','std'] }) )
            
            df_aux.columns = ['avg_time', 'std_time']
            
            df_aux = df_aux.reset_index()
            
            st.dataframe( df_aux, use_container_width=True )

        with col2:
            st.markdown( """___""" )
            st.subheader( 'Média de tempo por cidade' )
#                          *************************        
            fig = avg_std_time_graph( df1)    
            st.plotly_chart( fig, use_container_width=True )
        
# =================================== :: CONTAINER ::
#                                        ---------
    
    with st.container():
        st.markdown( """___""" )
        st.title( "Distribuição do Tempo" )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader( "Distancia Média de Entrega" )
#                          ********************************      
            fig = distance( df1, fig=True )
            st.plotly_chart( fig, use_container_width=True )
            
            
        with col2:
            st.subheader( 'Tempo médio por tipo de entrega' )
#                          *******************************    
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart( fig, use_container_width=True )
            
        
















        
        