import numpy as np
import sympy as sp
import scipy as sc
import matplotlib.pyplot as plt
import streamlit as st

# Inicializando Streamlit
st.set_page_config(page_title="Gráfico de Funções", layout="wide", page_icon="📈")
# Título da aplicação
st.title("📈 Gráfico de Funções com Streamlit")
st.markdown("Esta aplicação permite que você visualize gráficos de funções matemáticas usando Streamlit, NumPy, SymPy e Matplotlib.")


try:
    # Seção para entrada da função
    st.header("Entrada da Função")
    func_input = st.text_input("Digite a função em termos de x (ex: sin(x)", value="sin(x)", key="func_input")
    func_sympy = sp.sympify(func_input) # Convertendo em uma expressão simbólica
    # Mostrar em LateX para o usuário
    func_latex = sp.latex(func_sympy)
    st.markdown(f"A função que você digitou é: ${func_latex}$")
    # Seção para definir o intervalo de x
    st.header("Intervalo de x")
    x_min = st.number_input("Valor mínimo de x", value=-10.0, step =0.1, format = "%.6f", key="x_min")   
    x_max = st.number_input("Valor máximo de x", value=10.0, step=0.1, format = "%.6f", key="x_max")
    # Gerando os valores de x e y
    x = np.linspace(x_min, x_max, 500)
    y = sp.lambdify(sp.symbols('x'), func_sympy)(x) # Convertendo a função simbólica para uma função numérica
    # Seção para exibir o gráfico
    st.header("Gráfico da Função")
    fig, ax = plt.subplots()
    plt.figure(figsize=(10,5)) 
    ax.plot(x, y, label=f"f(x) = {func_input}")
    ax.set_xlabel("x")
    ax.set_ylabel("y = f(x)")
    ax.set_title("Gráfico da Função")
    ax.grid(True, linestyle='--', alpha=0.7)  # estilo de engenharia para a grade
    ax.legend()
    st.pyplot(fig)
except Exception as e:
    st.warning("Verifique se a funcao é válida.")
    print(f"Erro: {e}")