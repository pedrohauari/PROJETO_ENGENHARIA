import streamlit as st

# Configuração da aba do navegador
st.set_page_config(
    page_title="Portal de Cálculo",
    page_icon="📜",
    layout="wide"
)

st.title("🧮 Ecossistema de Ferramentas Matemáticas")

st.markdown("""
### Bem-vindo ao meu portal de Cálculo Numérico e Simbólico!
Use o menu à esquerda para navegar entre as ferramentas. 

Este projeto reúne:
* **Cálculo Simbólico:** Soluções exatas e fórmulas passo a passo.
* **Cálculo Numérico:** Aproximações de alta performance para engenharia.
* **Visualização:** Gráficos interativos para análise de comportamento de funções.
""")

st.info("Dica: Se estiver no celular, clique na seta no canto superior esquerdo para ver o menu.")