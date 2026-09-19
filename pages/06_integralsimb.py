import streamlit as st # pyright: ignore[reportMissingImports]
import sympy as sp # pyright: ignore[reportMissingModuleSource]
from sympy.abc import _clash # pyright: ignore[reportMissingImports]
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor # pyright: ignore[reportMissingModuleSource]
from sympy.integrals.manualintegrate import manualintegrate # pyright: ignore[reportMissingModuleSource]
import numpy as np # type: ignore
from scipy.integrate import quad # pyright: ignore[reportMissingImports]
import matplotlib.pyplot as plt # pyright: ignore[reportMissingModuleSource]

st.set_page_config(page_title="Calculadora de Integrais", layout="wide", page_icon="🧮")

# --- Mapeamento de Funções Especiais e Constantes ---
funcoes_especiais = {
    sp.erf: "Função de Erro (comum em probabilidade e calor)",
    sp.Si: "Seno Integral (comum em processamento de sinais)",
    sp.Ci: "Cosseno Integral",
    sp.expint: "Integral Exponencial"
}

meus_simbolos = {"e": sp.E, "pi": sp.pi, "ln": sp.log}
transformacoes = standard_transformations + (implicit_multiplication_application, convert_xor)


def forcar_solucao_real(expr, var):
    """
    Remove unidades imaginárias (I) convertendo logaritmos complexos
    em funções trigonométricas inversas reais (arcsin, arctan, etc).
    """
    if isinstance(expr, sp.Integral) or not expr.has(sp.I):
        return expr

    for func_trig in [sp.asin, sp.atan, sp.acos]:
        try:
            candidato = sp.simplify(expr.rewrite(func_trig))
            if not candidato.has(sp.I):
                return candidato
        except Exception:
            pass

    try:
        candidato = sp.refine(expr, sp.Q.real(var) & sp.Q.positive(var))
        candidato = sp.simplify(candidato)
        if not candidato.has(sp.I):
            return candidato
    except Exception:
        pass

    try:
        candidato = sp.trigsimp(sp.expand_complex(expr)[0])
        if not candidato.has(sp.I):
            return candidato
    except Exception:
        pass

    return expr


def calcular_integral_robusta(func, var):
    """
    Executa uma estratégia em cascata para resolver a integral analítica.
    Só aceita soluções que NÃO contenham a unidade imaginária I.
    """
    # 1. Tentativa Direta Padrão (recusa se tiver 'I')
    res = sp.integrate(func, var)
    if not isinstance(res, sp.Integral) and not res.has(sp.I):
        return res

    # 2. Suposições de símbolos reais e positivos
    simbolos = func.free_symbols
    sub_dict = {s: sp.Symbol(s.name, real=True, positive=True) for s in simbolos}
    func_assumed = func.subs(sub_dict)
    var_assumed = sub_dict.get(var, sp.Symbol(var.name, real=True, positive=True))

    res_assumed = sp.integrate(func_assumed, var_assumed)
    if not isinstance(res_assumed, sp.Integral) and not res_assumed.has(sp.I):
        revert_dict = {v: k for k, v in sub_dict.items()}
        return res_assumed.subs(revert_dict)

    # 3. Tentativa via manualintegrate
    try:
        res_manual = manualintegrate(func, var)
        if not isinstance(res_manual, sp.Integral) and res_manual is not None and not res_manual.has(sp.I):
            return res_manual
    except Exception:
        pass

    # 4. Tentativa com manualintegrate + suposições
    try:
        res_manual_assumed = manualintegrate(func_assumed, var_assumed)
        if not isinstance(res_manual_assumed, sp.Integral) and res_manual_assumed is not None and not res_manual_assumed.has(sp.I):
            revert_dict = {v: k for k, v in sub_dict.items()}
            return res_manual_assumed.subs(revert_dict)
    except Exception:
        pass

    # 5. Reescrever radicais e simplificar
    try:
        func_prep = sp.powdenest(sp.radsimp(sp.simplify(func)), force=True)
        res_prep = sp.integrate(func_prep, var)
        if not isinstance(res_prep, sp.Integral) and not res_prep.has(sp.I):
            return res_prep
    except Exception:
        pass

    # Se nada sem 'I' funcionou, retorna o resultado com suposições convertido
    if not isinstance(res_assumed, sp.Integral):
        revert_dict = {v: k for k, v in sub_dict.items()}
        return res_assumed.subs(revert_dict)

    return res


# ==============================================================================
# 1. SEÇÃO: INTEGRAIS INDEFINIDAS
# ==============================================================================
st.title("Calculadora de Integrais Indefinidas")

col_input_indef, col_var_indef = st.columns([3, 1])

with col_input_indef:
    raw_input = st.text_input(
        "Digite a função a ser integrada:", 
        value="sqrt(x / (R - x))", 
        key="func_indef"
    )

try:
    func = parse_expr(raw_input, local_dict={**meus_simbolos, **_clash}, transformations=transformacoes)
    simbolos_presentes = sorted([s.name for s in func.free_symbols])
    
    with col_var_indef:
        if simbolos_presentes:
            idx_padrao = simbolos_presentes.index('x') if 'x' in simbolos_presentes else 0
            var_nome = st.selectbox(
                "Diferencial:",
                options=simbolos_presentes,
                index=idx_padrao,
                format_func=lambda s: f"d{s}",
                key="var_indef_select"
            )
        else:
            var_nome = st.selectbox(
                "Diferencial:", 
                options=['x', 't', 'y', 'z'], 
                index=0, 
                format_func=lambda s: f"d{s}", 
                key="var_indef_const"
            )
    
    var = sp.Symbol(var_nome)

    integral = calcular_integral_robusta(func, var)
    integral = forcar_solucao_real(integral, var)

    if isinstance(integral, sp.Integral):
        st.warning("⚠️ **Aviso:** Não foi encontrada uma solução analítica simples para esta função.")
        st.markdown("Tente calcular numericamente na seção de integrais definidas abaixo.") 
        st.latex(rf"\int {sp.latex(func)} \, d{var.name} = {sp.latex(integral)}")
    else:
        for f, desc in funcoes_especiais.items():
            if integral.has(f):
                st.info(f"⚡ A integral envolve a função especial `{f.__name__}`: {desc}")
        
        st.write(f"Integral de `{func}` em relação a **d{var.name}**:")
        st.latex(rf"\int {sp.latex(func)} \, d{var.name} = {sp.latex(integral)} + C")

except Exception as e:
    st.error(f"Erro ao processar a função: {e}")

st.divider()

# ==============================================================================
# 2. SEÇÃO: INTEGRAIS DEFINIDAS (NUMÉRICAS)
# ==============================================================================
st.title("Calculadora de Integrais Definidas")
st.caption("Cálculo numérico da área sob a curva com opção de definir limites e variáveis.")

col_input_def, col_var_def = st.columns([3, 1])

with col_input_def:
    raw_input_def = st.text_input(
        "Função para integrar numericamente:", 
        value="exp(-x^2)", 
        key="func_def_input"
    )

try:
    func_def = parse_expr(raw_input_def, local_dict={**meus_simbolos, **_clash}, transformations=transformacoes)
    simbolos_def = sorted([s.name for s in func_def.free_symbols])

    with col_var_def:
        if simbolos_def:
            idx_def = simbolos_def.index('x') if 'x' in simbolos_def else 0
            var_def_nome = st.selectbox(
                "Diferencial:",
                options=simbolos_def,
                index=idx_def,
                format_func=lambda s: f"d{s}",
                key="var_def_select"
            )
        else:
            var_def_nome = st.selectbox(
                "Diferencial:", 
                options=['x', 't', 'y', 'z'], 
                index=0, 
                format_func=lambda s: f"d{s}", 
                key="var_def_const"
            )

    col_limit1, col_limit2 = st.columns(2)
    with col_limit1:
        lower_limit = st.number_input("Limite inferior:", value=0.0) 
    with col_limit2:
        upper_limit = st.number_input("Limite superior:", value=1.0)

    expr_lower = sp.Number(lower_limit) 
    expr_upper = sp.Number(upper_limit)

    if lower_limit is not None and upper_limit is not None:
        var_def = sp.Symbol(var_def_nome)
        
        f_lamb = sp.lambdify(var_def, func_def, modules=['numpy'])
        resultado, erro = quad(f_lamb, lower_limit, upper_limit)

        st.write("### Resultado:")
        st.latex(rf"\int_{{{sp.latex(expr_lower)}}}^{{{sp.latex(expr_upper)}}} {sp.latex(func_def)} \, d{var_def.name} \approx {resultado:.4f}")

        col1, _ = st.columns([1, 1])

        with col1:
            st.subheader("Visualização da Área")
            
            margem = abs(upper_limit - lower_limit) * 0.2 if upper_limit != lower_limit else 1
            x_vals = np.linspace(lower_limit - margem, upper_limit + margem, 400)
            y_vals = f_lamb(x_vals)
            
            if np.isscalar(y_vals) or isinstance(y_vals, (int, float)):
                y_vals = np.full_like(x_vals, float(y_vals))
                
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(x_vals, y_vals, label=f'f({var_def.name}) = {func_def}', color='royalblue')
            ax.fill_between(x_vals, y_vals, where=(x_vals >= lower_limit) & (x_vals <= upper_limit), color='lightblue', alpha=0.6)
            
            ax.axhline(0, color='black', lw=0.8)
            ax.axvline(0, color='black', lw=0.8)
            ax.set_xlabel(f"Eixo {var_def.name}")
            ax.set_ylabel(f"f({var_def.name})")
            ax.set_title("Área Sob a Curva")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.5)
            st.pyplot(fig)

except Exception as e:
    st.error(f"Erro no cálculo ou no gráfico: {e}")

st.divider()

# ==============================================================================
# 3. EXEMPLOS E DOCUMENTAÇÃO DA INTERFACE
# ==============================================================================
with st.expander("Exemplos de Funções Avançadas"):
    st.markdown("""
    * `sqrt(x / (R - x))` (Integral algébrica com radical e parâmetros).
    * `sqrt(a^2 - x^2)` (Substituição trigonométrica).
    * `x * sqrt(1 - x^2)` (Substituição direta $u$).
    * `1 / (x^2 + a^2)` (Integrais com arcotangente).
    """)

st.subheader("Guia de Sintaxe")
st.markdown("""
* **Diferencial Automático:** Detecta os símbolos e permite escolher a variável principal de integração.
* **Radicais:** Use `sqrt(...)` para raízes quadradas ou `(...)**(1/3)` para raízes cúbicas.
* **Constantes e Parâmetros:** Letras secundárias são tratadas automaticamente como parâmetros reais positivos.
""")