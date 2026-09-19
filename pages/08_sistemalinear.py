import numpy as np
import streamlit as st
import sympy as sp

st.set_page_config("Analista de Sistemas Lineares", layout="centered")
st.title("Resolvedor de Sistemas Lineares")

n = st.number_input("Número de Variáveis: ", min_value=2, max_value=10, value=3)
st.write("Preencha a Matriz de Coeficientes [A] e o Vetor de Resultados [B]")

# Interface de entrada de dados
dados_iniciais = np.zeros((n, n + 1))
df_input = st.data_editor(dados_iniciais)

if st.button("Analisar e Resolver"):
    A = df_input[:, :-1]
    B = df_input[:, -1]
    
    # 1. Matriz Ampliada e Postos para o Teorema de Rouché-Capelli
    ampliada = np.column_stack((A, B))
    posto_a = np.linalg.matrix_rank(A)
    posto_amp = np.linalg.matrix_rank(ampliada)
    
    st.divider()

    # --- CASO 1: SPD (Solução Única) ---
    if posto_a == posto_amp and posto_a == n:
        st.success("💎 **SPD: Sistema Possível e Determinado**")
        x = np.linalg.solve(A, B)
        
        # Exibição dos valores encontrados
        cols = st.columns(n)
        for i, valor in enumerate(x):
            cols[i].latex(f"x_{{{i+1}}} = {valor:.4f}")

        # REINSERINDO A VERIFICAÇÃO VISUAL (PROVA REAL)
        st.subheader("🔍 Verificação Visual (Prova Real)")
        st.write("Confirmando se $A \cdot X = B$:")
        
        # Formatando para LaTeX (arredondado para não poluir o visual)
        matriz_A_f = sp.Matrix(A.round(2))
        vetor_X_f = sp.Matrix(x.reshape(-1, 1).round(4)) # Reshape para coluna
        vetor_B_f = sp.Matrix(B.round(2))
        
        st.latex(f"{sp.latex(matriz_A_f)} \cdot {sp.latex(vetor_X_f)} = {sp.latex(vetor_B_f)}")
        st.caption("Nota: Valores arredondados no LaTeX para facilitar a leitura.")

    # --- CASO 2: SPI (Infinitas Soluções) ---
    elif posto_a == posto_amp and posto_a < n:
        st.warning("♾️ **SPI: Sistema Possível e Indeterminado**")
        st.info(f"O sistema tem infinitas soluções. Há {n - posto_a} grau(s) de liberdade.")
        st.latex(rf"\rho(A) = {posto_a} \quad \text{{e}} \quad \rho(A|B) = {posto_amp}")

    # --- CASO 3: SI (Impossível) ---
    else:
        st.error("🚫 **SI: Sistema Impossível**")
        st.info("As equações são contraditórias e não existe solução.")
        st.latex(rf"\rho(A) = {posto_a} \quad \neq \quad \rho(A|B) = {posto_amp}")

    # Expander de Análise Técnica (Opcional)
    with st.expander("Ver detalhes da Análise Técnica"):
        st.write("Critério de Rouché-Capelli:")
        st.markdown(f"- **Número de variáveis (n):** {n}")
        st.markdown(f"- **Posto da Matriz A ($\rho_A$):** {posto_a}")
        st.markdown(f"- **Posto da Matriz Ampliada ($\rho_{{A|B}}$):** {posto_amp}")
        if posto_a == posto_amp == n:
            st.write("Como $\rho_A = \rho_{A|B} = n$, o sistema é **Determinado**.")
        elif posto_a == posto_amp < n:
            st.write("Como $\rho_A = \rho_{A|B} < n$, o sistema é **Indeterminado**.")
        else:
            st.write("Como $\rho_A < \rho_{A|B}$, o sistema é **Impossível**.")