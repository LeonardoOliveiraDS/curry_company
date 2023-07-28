# ================================================================
# ||||||||||||||| === LIBRARY ** BIBLIOTECAS === |||||||||||||||||
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

st.set_page_config( page_title='Visão Empresa', page_icon='🔎', layout='wide' )

# ================================================================
# |||||||||||||||| === FUNCTIONS ** FUNÇÕES === ||||||||||||||||||
# ================================================================

def country_maps( df1 ):
        
        cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df_aux = ( df1.loc[:, cols]
                      .groupby( ['City', 'Road_traffic_density'] )
                      .median()
                      .reset_index() )
 
        map = folium.Map()
    
        for index, location_info in df_aux.iterrows():
            folium.Marker( [location_info['Delivery_location_latitude'],
                            location_info['Delivery_location_longitude']],
                            popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
        
        folium_static( map, width=1024, height=600 )

# ______________________________________________________________
# ______________________________________________________________

def order_share_by_week( df1 ):
    # Quantidade de pedidos por semana / Número unico de entregadores por semana
    df_aux1 = ( df1.loc[:, ['ID', 'week_of_year']]
                   .groupby('week_of_year')
                   .count()
                   .reset_index() )
    df_aux2 = ( df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                   .groupby('week_of_year')
                   .nunique()
                   .reset_index() )
            
    df_aux = pd.merge( df_aux1, df_aux2, how='inner', on='week_of_year'  )
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID'] 
        
    fig = px.line( df_aux, x='week_of_year', y='order_by_deliver')
    return fig

# ______________________________________________________________
# ______________________________________________________________

def order_by_week( df1 ):
    # criar coluna da semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    df_aux = ( df1.loc[:, ['ID','week_of_year']]
                  .groupby('week_of_year')
                  .count()
                  .reset_index() )
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    return fig
    

# ______________________________________________________________
# ______________________________________________________________

def traffic_order_city( df1 ):
    """ 
        Esta função recebe o df e retorna uma fig do percentual
        de entregas por 'City' - Grafico Scatter

    """
    df_aux = ( df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                  .groupby(['City', 'Road_traffic_density'])
                  .count()
                  .reset_index() )
    
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City' )

    return fig

# ______________________________________________________________
# ______________________________________________________________

def traffic_order_share( df1 ):
    """ 
        Esta função recebe o df e retorna uma fig do percentual
        de entregas por tipo de trafego - Grafico Pizza

    """
                    
    df_aux = ( df1.loc[:, ['ID', 'Road_traffic_density']]
                                  .groupby('Road_traffic_density')
                                  .count()
                                  .reset_index() )
    
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
                    
    fig = px.pie( df_aux,
                     values='entregas_perc', 
                     names='Road_traffic_density' )

    return fig

# ______________________________________________________________
# ______________________________________________________________

def order_metric( df1 ):
    """ Esta funcao recebe um dataframe, executa, gera uma figura e devolve uma figura
    """
    
    cols= ['ID', 'Order_Date']
    # selecao de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index() 
    # Desenhar Grafico
    fig = px.bar( df_aux, x='Order_Date', y='ID' )

    return fig

# ______________________________________________________________
# ______________________________________________________________

def clean_code( df1 ):
    """ Esta funcao tem a responsabilidade de limpar o data frame
    
        TIpos de limpeza:
        1. removeção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Removação dos espaços das variaveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variavel númerica )

        Imput: Dataframe
        Output: Dataframe
    
    """
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
    
# ***********************************************************************************************************************************************
# **------------------------------------------------- || INICIO DA ESTRUTURA LÓGICA DO CÓDIGO || ----------------------------------------------**
# ***********************************************************************************************************************************************
# ------------------ || IMPORT DATASET ||
# ***************************************

df = pd.read_csv( 'dataset/train.csv' )

# ***************************************
# --------------- || LIMPANDO OS DADOS ||
# ***************************************

df1 = clean_code( df )

# ***************************************************--------------------------------------------------------------------------
# ------------------- || BARRA LATERAL **************--------------------------------------------------------------------------
# ***************************************************--------------------------------------------------------------------------

st.header( 'Marketplace - Visão Cliente' )

#image_path = '/Users/leona/Documents/repos/jupyterlab/logo.PNG'
image = Image.open( 'logo.PNG' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" ) # Cria uma linha horizontal no sidebar

st.sidebar.markdown( '## Seleciona uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime( 2022, 4, 13 ),
    min_value=datetime.datetime(2022, 2, 11 ),
    max_value=datetime.datetime(2022, 4, 6 ),
    format='DD-MM-YYYY' )

# ************************

st.sidebar.markdown( """___""" ) 

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """___""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# -------------------------------------
# ********** FILTRO DE DATA ***********
# -------------------------------------
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# -------------------------------------
# ******** FILTRO DE TRANSITO *********
# -------------------------------------

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# ***************************************************--------------------------------------------------------------------------
# ------------------- || LAYOUT NO STREAMLIT ********--------------------------------------------------------------------------
# ***************************************************--------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs( ['Visao Gerencial', 'Visão Tática', 'Visão Geográfica'] )

# ****************************************************************
# ****|               TAB 01 - Visão Tática                 |*****
# ****************************************************************

with tab1:
    with st.container():
        
        # Order Metrics
        st.markdown ('# Orders by Day')
        fig = order_metric( df1 )
        st.plotly_chart( fig, use_container_width=True ) # pra exibir o grafico pelo streamlit

#----------------------- || CONTAINER ||

        
        with st.container():
            col1, col2 = st.columns( 2 ) # uso para dividir a primeira coluna em 2
            
            with col1:
                fig = traffic_order_share( df1 )
                st.header( " Traffic Order Share " )
                st.plotly_chart( fig, use_container_width=True )
                
            with col2:
                fig = traffic_order_city( df1 )
                st.header( " Traffic Order City " )
                st.plotly_chart( fig, use_container_width=True )
            
#************************************************************
#                       TAB 02 - Visão Tática
#************************************************************

with tab2:
    with st.container():
        st.markdown( '# Order per Week' )
        fig = order_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )

#----------------------- || CONTAINER ||

    with st.container():
        st.markdown( '# Order Share by Week' )
        fig = order_share_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )

        
# *********************************************************
#                 TAB 03 - VISÃO GEOGRAFICA
# *********************************************************

with tab3:    
    st.markdown( '# Country Maps' )
    country_maps( df1 )

    
    



       