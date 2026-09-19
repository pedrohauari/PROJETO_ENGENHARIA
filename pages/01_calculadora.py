import streamlit as st
import sympy as sp
from sympy.abc import _clash
import math
import string 

st.set_page_config(page_title="Calculadora de Engenharia", page_icon="🧮")

# --- 1. INICIALIZAÇÃO DO HISTÓRICO ---
if 'historico' not in st.session_state:
    st.session_state.historico = []

st.title("🧮 Calculadora de Expressões de Engenharia")

# --- 2. BARRA LATERAL (HISTÓRICO) ---
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

# --- 3. INPUT DA EQUAÇÃO ---
raw_input = st.text_input("Digite a expressão (ex: sin(x) + exp(x)): ", value="x**2")

if not raw_input.strip():
    st.info("Aguardando uma expressão...")
    st.stop()

expr_str = raw_input.replace('^', '**')

try:
    # Preparação de símbolos e constantes
    meus_simbolos = {}
    if _clash: 
        meus_simbolos.update(_clash)
    meus_simbolos.update({"pi": sp.pi, "PI": sp.pi, "Pi": sp.pi, "pI": sp.pi, "π": sp.pi, "e": sp.E})
    
    expr = sp.sympify(expr_str, locals=meus_simbolos)
    variaveis = sorted(list(expr.free_symbols), key=lambda s: s.name)

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
        st.warning("⚠️ Cuidado: Se usar graus, os cálculos podem ser imprecisos.")
        # mostrar o angulo em graus para radianos na entrada
        for var in trig_vars:
            if unidade_angulo == "Graus":
                expr = expr.subs(var, var * (sp.pi / 180))
    st.divider()

    # Input dos valores
    st.divider()
    st.subheader("📌 Valores das Variáveis")
    valores_subs = {}
    
    if not variaveis:
        st.info("A expressão é uma constante.")
    else:
        cols = st.columns(len(variaveis))
        for i, var in enumerate(variaveis):
            label = f"Valor de {var}:"
            if var in trig_vars: label += " (Ângulo)"
            val = cols[i].number_input(label, value=1.0, format="%.6f", key=f"input_{var}")
            
            if var in trig_vars and unidade_angulo == "Graus":
                valores_subs[var] = val * (sp.pi / 180)
            else:
                valores_subs[var] = val

    # --- 👁️ VISUALIZAÇÃO EM TEMPO REAL ---
    st.divider()
    st.markdown("### 📖 Expressão Interpretada")
    st.latex(sp.latex(expr))

    # --- 🚀 CÁLCULO E SALVAMENTO NO HISTÓRICO ---
    if st.button("Calcular Valor Numérico", type="primary"):
        res_val = expr.evalf(subs=valores_subs)
        
        # 1. Determina o texto do resultado
        try:
            res_float = float(res_val)
            resultado_texto = f"{res_float:.6f}"
        except Exception:
            resultado_texto = str(res_val)

        # 2. Prepara os detalhes para o histórico
        detalhes_vars = ", ".join([f"{var}={float(val):.4g}" for var, val in valores_subs.items()])
        
        # 3. Monta o registro visual
        registro = (
            f"#### :red[{raw_input}] \n"
            f":grey[Valores:] :orange[{detalhes_vars}] \n\n"
            f"➜ **:green[{resultado_texto}]**"
        )
        
        # 4. Salva no histórico (Antes do rerun!)
        if registro not in st.session_state.historico:
            st.session_state.historico.append(registro)
        if len(st.session_state.historico) > 5:
            st.session_state.historico.pop(0)

        # 5. Mostra o resultado na tela
        st.divider()
        st.subheader("🎯 Resultado")
        if "res_float" in locals():
            st.success(f"Valor final: {resultado_texto}")
        else:
            st.warning(f"Resultado: {resultado_texto}")
        
        # 6. Agora sim, reinicia para atualizar a barra lateral
        st.rerun()

except Exception as e:
    st.error(f"Erro na expressão: {e}")

# --- 4. GUIA DE SINTAXE ---
st.divider()
with st.expander("ℹ️ Guia de Sintaxe"):
    st.write("""
    * **Multiplicacao:** `2*x`
    * **Potência:** `x**2` `ou x^2`, `x^-1`
    * **Raiz Quadrada:** `sqrt(x)`
    * **Logaritmo Natural:** `log(x)`
    * **Exponencial Natural:** `exp(x)`
    * **Exponencial Normal:** `2**x`
    * **Trigonometria:** `sin(x)`, `cos(x)`, `tan(x)`, `asin(x) (arco seno)`, `sinh(x) (seno hiperbólico)`
    * **Constantes:** `e (Numero de Euler)`, `pi, Pi, pI, PI, π`
    """)