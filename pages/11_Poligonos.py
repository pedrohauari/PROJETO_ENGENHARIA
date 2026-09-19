import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from math import atan2, sqrt, pi

# Configuração da página
st.set_page_config(page_title="Gerador de Polígonos Complexos", layout="wide")

st.title("🎨 Gerador de Polígonos Regulares no Plano Complexo")
st.markdown("""
Este app resolve equações do tipo $z^n = w$, onde $w = a + bi$. 
As raízes formam um polígono regular inscrito em uma circunferência.
""")

# --- Sidebar para Inputs ---
st.sidebar.header("Parâmetros da Equação")
a = st.sidebar.number_input("Parte Real (a)", value=1.0, step=1.0)
b = st.sidebar.number_input("Parte Imaginária (b)", value=0.0, step=1.0)
n = st.sidebar.number_input("Ordem da Raiz (n)", min_value=2, max_value=100, value=3)

# --- Processamento Matemático ---

# 1. Cálculo do Módulo e Argumento (numérico para o gráfico)
r = sqrt(a**2 + b**2)   
theta = atan2(b, a) 

# 2. Representação em LaTeX usando SymPy
z_sym = sp.symbols('z')
forma_algebrica = a + b*sp.I

# Simplificar o módulo e o ângulo simbolicamente
r_sym = sp.simplify(sp.sqrt(a**2 + b**2))
# AQUI ESTAVA O ERRO: Removi o sp.Rational. O sp.atan2 já faz o trabalho sujo.
theta_sym = sp.atan2(b, a) 

st.subheader("1. Representação da Equação")
col1, col2 = st.columns(2)

with col1:
    st.write("**Forma Algébrica:**")
    st.latex(f"z^{{{n}}} = {sp.latex(forma_algebrica)}")

with col2:
    st.write("**Forma Polar (w):**")
    # Melhorei aqui para usar o theta_sym (com pi) no LaTeX!
    st.latex(f"w = {sp.latex(r_sym)} \cdot (\cos({sp.latex(theta_sym)}) + i \cdot \sin({sp.latex(theta_sym)}))")

# 3. Cálculo das Raízes (De Moivre)
raizes = []
raio_raiz = r**(1/n)

for k in range(n):
    angulo_k = (theta + 2 * k * pi) / n
    real_k = raio_raiz * np.cos(angulo_k)
    imag_k = raio_raiz * np.sin(angulo_k)
    raizes.append((real_k, imag_k))

# --- Visualização com Matplotlib ---
st.subheader(f"2. Geometria das {n} Raízes")

fig, ax = plt.subplots(figsize=(8, 8))

x_coords = [p[0] for p in raizes]
y_coords = [p[1] for p in raizes]

x_plot = x_coords + [x_coords[0]]
y_plot = y_coords + [y_coords[0]]

circulo = plt.Circle((0, 0), raio_raiz, color='gray', fill=False, linestyle='--', alpha=0.5)
ax.add_artist(circulo)

ax.scatter(x_coords, y_coords, color='red', s=50, zorder=5, label='Raízes (Vértices)')
ax.plot(x_plot, y_plot, color='blue', linewidth=2, alpha=0.8, label=f'Polígono (n={n})')

limite = raio_raiz * 1.3
ax.set_xlim(-limite, limite)
ax.set_ylim(-limite, limite)
ax.axhline(0, color='black', linewidth=1)
ax.axvline(0, color='black', linewidth=1)
ax.set_aspect('equal') 
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_xlabel("Eixo Real (Re)")
ax.set_ylabel("Eixo Imaginário (Im)")
ax.legend()

unit_circle = plt.Circle((0, 0), 1.0, color='green', fill=False, linestyle=':', alpha=0.3)
ax.add_artist(unit_circle)

for x, y in raizes:
    angulo_deg = np.degrees(atan2(y, x))
    if angulo_deg < 0: angulo_deg += 360
    ax.annotate(f"{angulo_deg:.1f}°", (x, y), textcoords="offset points", xytext=(5,5), fontsize=8)

st.pyplot(fig)

with st.expander("Ver valores numéricos das raízes"):
    for i, (re, im) in enumerate(raizes):
        st.write(f"Raiz {i}: {re:.4f} + {im:.4f}j")