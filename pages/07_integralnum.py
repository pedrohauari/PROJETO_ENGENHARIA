import streamlit as st
import sympy as sp
from sympy.abc import _clash
import scipy as sc
from scipy.integrate import quad
import numpy as np
import matplotlib.pyplot as plt


st.set_page_config("Calculadora de Integrais Definidas", layout="wide", page_icon="🧮")
# 1) Inicializar o histórico
if 'historico' not in st.session_state:
    st.session_state.historico = []

st.title("🧮 Calculadora de Integrais Definidas")
# 2) BARRA LATERAL (HISTÓRICO) 
with st.sidebar: 
    st.header("🕒 Histórico")
    if not st.session_state.historico: 
        st.write("Nenhum cálculo recente.")
    else: 
        for item in reversed(st.session_state.historico):
            st.markdown(item)
            st.divider()
        if st.button("Limpar Histórico"):
            st.session_state.historico = []
            st.rerun()

# 3) INPUT DO USUÁRIO
raw_input = st.text_input("Digite a expressão(ex: e^x**2 ):", value = "e**x**2")
if not raw_input.strip():
    st.info("Aguardando uma expressão...")
    st.stop()

expr_str = raw_input.replace("^", "**")

try: 
    meus_simbolos = {}
    if _clash:
        meus_simbolos.update(_clash)
    meus_simbolos.update( {"pi": sp.pi, "Pi": sp.pi , "pI": sp.pi, "PI": sp.pi, "π": sp.pi, "e": sp.E})
    expr = sp.sympify(expr_str, locals = meus_simbolos)
    variaveis = sorted(list(expr.free_symbols), key= lambda s : s.name)

    # Identificação de Trigonometria
    funcoes_trig = (sp.sin, sp.cos, sp.tan, sp.cot, sp.sec, sp.csc)
    trig_vars = set()
    if expr.has(*funcoes_trig):
        for f in expr.atoms(sp.Function):
            if isinstance(f, funcoes_trig):
                trig_vars.update(f.free_symbols)

    unidade_angulo = "Radianos"
    if trig_vars:
        st.divider()
        st.subheader("📐 Configuração de Trigonometria")
        unidade_angulo = st.radio("Entrada para ângulos:", ["Radianos", "Graus"], horizontal=True)

        # Input dos valores
    st.divider()
    st.subheader("📌 Valores das Variáveis")
    valores_subs = {}

# --- CONTINUAÇÃO: INPUT DOS VALORES E LIMITES ---
    if not variaveis:
        st.error("A expressão não possui variáveis para integrar.")
        st.stop()

    # Se houver mais de uma variável, o usuário escolhe a de integração
    if len(variaveis) > 1:
        var_integracao = st.selectbox("Selecione a variável de integração (dx):", variaveis)
    else:
        var_integracao = variaveis[0]

    # Criamos colunas para os Limites e para as outras variáveis (se existirem)
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Limites de integração para {var_integracao}:**")
    
    # CORREÇÃO: Pegamos apenas UM valor do widget
        lim_inf = st.number_input("Limite Inferior (a):", value=0.0)
    # Criamos a versão SymPy para o LaTeX
        expr_inf = sp.Number(lim_inf) 

        lim_sup = st.number_input("Limite Superior (b):", value=1.0)
    # Criamos a versão SymPy para o LaTeX
        expr_sup = sp.Number(lim_sup)

    # Se sobrarem variáveis (ex: integrar x, mas tem um 'y' constante)
    outras_vars = [v for v in variaveis if v != var_integracao]
    valores_subs = {}
    
    if outras_vars:
        with col2:
            st.write("**Valores das constantes:**")
            for v in outras_vars:
                label = f"Valor de {v}:"
                # Se a constante for um ângulo, tratamos como no projeto anterior
                val = st.number_input(label, value=1.0, format="%.6f", key=f"const_{v}")
                
                if v in trig_vars and unidade_angulo == "Graus":
                    valores_subs[v] = val * (sp.pi / 180)
                else:
                    valores_subs[v] = val

    # --- 👁️ VISUALIZAÇÃO DA INTEGRAL ---
    st.divider()
    st.markdown("### 📖 Representação Matemática")
    
    # Criamos o símbolo da integral para o LaTeX: \int_{a}^{b} f(x) dx
    integral_visual = sp.Integral(expr, (var_integracao, expr_inf, expr_sup))
    st.latex(sp.latex(integral_visual))

    # --- 🚀 BOTÃO DE CÁLCULO ---
    if st.button("Calcular Integral Definida", type="primary"):
        try:
            # 1. Substituir constantes (se houver) na expressão
            # Isso deixa a expressão apenas com a variável de integração
            expr_preparada = expr.subs(valores_subs)
            
            # 2. Criar a "Ponte" (SymPy -> Função Numérica)
            # Usamos o módulo 'numpy' para que a função seja rápida
            f_num = sp.lambdify(var_integracao, expr_preparada, modules=['numpy'])
            
            # 3. Executar o Cálculo Numérico
            # O quad retorna (valor_da_area, erro_estimado)
            resultado, erro_estimado = quad(f_num, lim_inf, lim_sup)
            
            # 4. Formatação para o Histórico
            texto_resultado = (
                f"**∫ f({var_integracao}) d{var_integracao}** de {expr_inf} a {expr_sup}\n\n"
                f"Função: `{expr}`\n\n"
                f"Valores das constantes: `{valores_subs}`\n\n"
                f"**Resultado: {resultado:.8f}** \n\n"
                f"*Erro estimado: `{erro_estimado:.1e}`)*"
            )
            
            # Adicionar ao histórico (limitando aos 5 últimos)
            # Histórico inteligente - só adiciona cálculos inéditos
            if texto_resultado not in st.session_state.historico:
                st.session_state.historico.append(texto_resultado)

                if len(st.session_state.historico) > 5:
                    st.session_state.historico.pop(0)
                
                # 5. Mostrar o resultado atual na tela principal com destaque
                st.success(f"### Resultado: {resultado:.8f}")
                # Forçar a atualização para o histórico aparecer na barra lateral
                st.rerun()
            else:
                st.warning("Este Cálculo já está no histórico. Verifique a barra lateral.")
        except Exception as erro:
            st.error(f"Erro no cálculo: {erro}. A funcão pode não ser integrável numericamente ou pode ser descontínua no intervalo escolhido.")
        

except Exception as e:
    st.error(f"Erro na expressão: {e}")


# quero adicionar o gráfico da funcao integrada entre os limites definidos, mostrando a área sob a curva
if 'resultado' in locals():
     st.divider()
     st.subheader("Visualização da Área Sob a Curva")
     x_vals = np.linspace(lim_inf - 1, lim_sup + 1, 400)
     y_vals = [sp.lambdify(var_integracao, expr_preparada, modules=['numpy'])(x) for x in x_vals]
     fig, ax = plt.subplots()
     ax.plot(x_vals, y_vals, label=f'f({var_integracao}) = {expr_preparada}')
     ax.fill_between(x_vals, y_vals, where=(x_vals >= lim_inf) & (x_vals <= lim_sup), color='lightblue', alpha=0.5)
     ax.axhline(0, color='gray', lw=0.5)
     ax.axvline(0, color='gray', lw=0.5)
     ax.set_xlabel(f'{var_integracao}')
     ax.set_ylabel('f({var_integracao})')
     ax.set_title('Área Sob a Curva da Função Integrada')
     ax.legend()
     st.pyplot(fig)
else:
    st.info("Calcule a integral definida para visualizar a área sob a curva.")


st.divider()
st.info("Use de preferencia Radianos para funcoes trigonométricas, ou defina os valores das constantes para evitar erros de precisão. Se a função for muito complexa ou tiver descontinuidades, o cálculo numérico pode falhar ou retornar um erro grande.")