import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp 

# Configuração da página
st.set_page_config(page_title="Analisador de Polinômios Gerais", layout="wide")

st.title("🔬 Analisador de Raízes de Polinômios")
st.markdown("""
Diferente do gerador de polígonos, aqui você define todos os coeficientes. 
Exemplo: para $1z^2 - 4$, digite `1, 0, -4`.
""")

# --- Entrada de Dados ---
# O usuário digita os coeficientes separados por vírgula
input_coefs = st.text_input("Digite os coeficientes (separados por vírgula):", value="1, 1, 2, -1")

try:
    # Converte a string de entrada em uma lista de números
    coefs = [float(c.strip()) for c in input_coefs.split(",")]
    
    # O NumPy faz a mágica de achar as raízes de qualquer grau
    raizes = np.roots(coefs)
    # grau de um polinomio n é  quantidade(coeficientes) - 1 
    grau = len(coefs) - 1
    # Equacao simbólica com o sympy
    z = sp.symbols('z')
    equacao_sym = 0
    for i, c in enumerate(coefs):
        equacao_sym += c * z**(grau - i)

    st.subheader("Equacao Interpretada:")
    st.latex(f"{sp.latex(equacao_sym)} = 0")
    st.divider() 

    st.subheader(f"Distribuição das {grau} Raízes no Plano Complexo")

    # --- Plotagem ---
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Extrair partes reais e imaginárias
    reais = [r.real for r in raizes]
    imags = [r.imag for r in raizes]

    # Desenhar eixos
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.set_xlabel("Eixo Real (Re)", fontsize = 12)
    ax.set_ylabel("Eixo Imaginário (Im)", fontsize = 12)
    
    # Plotar as raízes
    ax.scatter(reais, imags, color='magenta', s=100, edgecolors='black', zorder=5)

    # Identificar cada raiz com seu valor
    for i, raiz in enumerate(raizes):
        ax.annotate(f"  z{i}: {raiz:.2f}", (reais[i], imags[i]), fontsize=9)

    # Ajustar limites do gráfico
    max_dim = max(max([abs(r) for r in reais] + [abs(i) for i in imags] + [1]), 1) * 1.5
    ax.set_xlim(-max_dim, max_dim)
    ax.set_ylim(-max_dim, max_dim)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    st.pyplot(fig)

    # --- Tabela de Raízes ---
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Raízes Encontradas:**")
        for i, r in enumerate(raizes):
            st.write(f"z{i} = {r:.4f}")
            
    with col2:
        # Curiosidade de Engenharia: Estabilidade
        estaveis = all(r.real < 0 for r in raizes)
        if estaveis:
            st.success("✅ Sistema Estável (Todas as partes reais são negativas)")
        else:
            st.warning("⚠️ Sistema Instável ou Marginal (Há raízes no lado direito ou no eixo Jw)")

except Exception as e:
    st.error(f"Erro ao processar coeficientes: {e}. Certifique-se de usar números separados por vírgula.")