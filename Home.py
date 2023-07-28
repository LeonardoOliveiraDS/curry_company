import streamlit as st
from PIL import Image

st.set_page_config( 
    page_title='Home',
    page_icon="📊",
    layout='wide' )
# layout='wide' faz usar todo o espaço do monitor


#image_path = '/Users/leona/Documents/repos/jupyterlab/'
image = Image.open( 'logo.PNG' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )

st.write( "# Curry Company Growth Dashboard" )
st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimentos dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial:  Métricas gerais de comportamento.
        - Visão Tática:     Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhmento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
    - Time de DataScience no Discord
        - @LeonardoOliveiraDS
        
    """
    )


