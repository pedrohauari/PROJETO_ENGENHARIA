import streamlit as st
import sympy as sp
import math
import numpy as np
import string
from sympy.abc import _clash

def formatar_latex(nome):
    """Garante que letras gregas fiquem elegantes no LaTeX."""
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    nome_low = nome.lower()
    if nome_low in gregas:
        return f"\\{nome_low}"
    return nome

def calcular_seguro(func, *args):
    """
    Executa a função numérica e captura erros de domínio ou complexos,
    extraindo apenas a parte real para evitar quebras no Streamlit.
    """
    try:
        res = func(*args)
        # Se for um array ou valor complexo, pegamos apenas a parte real
        if np.iscomplexobj(res):
            return float(np.real(res))
        return float(res)
    except (TypeError, ValueError, ZeroDivisionError):
        return float('nan')

def app():
    st.set_page_config(page_title="Calculadora de Derivadas Robusta", layout="wide")
    
    # --- PREPARAÇÃO DE SÍMBOLOS ---
    latino = list(string.ascii_lowercase + string.ascii_uppercase)
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    todos_simbolos = latino + gregas + [g.capitalize() for g in gregas]

    st.title("🚀 Calculadora de Derivadas Inteligente")
    st.markdown("Insira funções como `cos(w*t)` ou equações como `x^3 + y^3 = 6*x*y`.")

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.header("🔧 Configurações")
        var_indep_nome = st.selectbox("Variável Independente:", todos_simbolos, index=todos_simbolos.index('x'))
        v1_sym = sp.Symbol(var_indep_nome)
        
        entrada_raw = st.text_input("Sua Equação/Função:", value="x^3 + y^3 = 6*x*y")
        v1_val = st.number_input(f"Valor de {var_indep_nome}:", value=1.0)
        
        st.divider()
        unidade = st.radio("Unidade Angular:", ("Radianos", "Graus"))
        h = 1e-5 
        calc_segunda = st.checkbox("Calcular 2ª Derivada?", value=True)

    try:
        # --- PARSE E TRADUÇÃO ---
        # Contexto expandido para evitar o erro de 'ufunc' e traduzir termos comuns
        contexto = {**_clash, "e": sp.E, "E": sp.E, "pi": sp.pi, "sen": sp.sin, "tg": sp.tan}
        texto_limpo = entrada_raw.replace('^', '**')
        
        if "=" in texto_limpo:
            esq, dir = texto_limpo.split("=")
            f_simbolica = sp.sympify(f"({dir}) - ({esq})", locals=contexto)
            modo_implicito = True
        else:
            f_simbolica = sp.sympify(texto_limpo, locals=contexto)
            modo_implicito = False

        # --- GESTÃO DE VARIÁVEIS  ---
        todos_na_func = f_simbolica.free_symbols
        # Candidatos são símbolos que não são a variável independente nem constantes matemáticas
        candidatos = [s for s in todos_na_func if str(s) != var_indep_nome and str(s) not in ['e', 'pi', 'E']]

        var_dep_sym = None
        dict_params = {}

        if candidatos:
            st.info("🔍 **Análise de Parâmetros**")
            
            # SÓ procuramos variável dependente se houver um "=" na entrada
            if modo_implicito:
                if len(candidatos) > 1:
                    var_dep_nome = st.selectbox("Qual destas é a variável DEPENDENTE?", [str(c) for c in candidatos])
                    var_dep_sym = sp.Symbol(var_dep_nome)
                else:
                    var_dep_sym = candidatos[0]
                    st.write(f"Variável dependente detectada: **{var_dep_sym}**")
            
            # Tudo que NÃO for a variável dependente (ou tudo, se for explícito) vira constante
            outros_params = [c for c in candidatos if str(c) != str(var_dep_sym)]
            
            if outros_params:
                with st.expander("📝 Valores das Constantes Detectadas", expanded=True):
                    cols = st.columns(len(outros_params))
                    for i, p in enumerate(outros_params):
                        dict_params[p] = cols[i].number_input(f"Valor de {p}:", value=1.0, key=f"const_{p}")

            # Se for implícito, precisamos do valor fixo da variável dependente no ponto
            if modo_implicito and var_dep_sym:
                v2_val_fixo = st.sidebar.number_input(f"Valor de {var_dep_sym} no ponto:", value=1.0)

        # --- PREPARAÇÃO PARA CÁLCULO ---
        # Substituímos as constantes pelos valores numéricos ANTES do lambdify
        f_num_preparada = f_simbolica.subs(dict_params)
        
        if modo_implicito and var_dep_sym:
            # A função numérica precisará de (independente, dependente)
            F_num = sp.lambdify((v1_sym, var_dep_sym), f_num_preparada, modules=['numpy', 'math'])
        else:
            # A função numérica precisará apenas da independente
            F_num = sp.lambdify(v1_sym, f_num_preparada, modules=['numpy', 'math'])

        # --- CÁLCULO DAS DERIVADAS ---
        v1_calc = math.radians(v1_val) if unidade == "Graus" else v1_val
        l_ind = formatar_latex(var_indep_nome)
        l_dep = formatar_latex(str(var_dep_sym)) if var_dep_sym else "f"

        # 1ª Ordem
        if modo_implicito and var_dep_sym:
            df_dx_s = sp.diff(f_simbolica, v1_sym)
            df_dy_s = sp.diff(f_simbolica, var_dep_sym)
            der_simb = -df_dx_s / df_dy_s
            
            v2_calc = math.radians(v2_val_fixo) if unidade == "Graus" else v2_val_fixo
            Fx_n = (calcular_seguro(F_num, v1_calc + h, v2_calc) - calcular_seguro(F_num, v1_calc - h, v2_calc)) / (2 * h)
            Fy_n = (calcular_seguro(F_num, v1_calc, v2_calc + h) - calcular_seguro(F_num, v1_calc, v2_calc - h)) / (2 * h)
            res_num = -Fx_n / Fy_n if Fy_n != 0 else float('nan')
            sub_dict = {v1_sym: v1_calc, var_dep_sym: v2_calc, **dict_params}
        else:
            der_simb = sp.diff(f_simbolica, v1_sym)
            res_num = (calcular_seguro(F_num, v1_calc + h) - calcular_seguro(F_num, v1_calc - h)) / (2 * h)
            sub_dict = {v1_sym: v1_calc, **dict_params}

        # --- EXIBIÇÃO DE RESULTADOS ---
        st.divider()
        st.info("📖 **Equação Interpretada:**")
        st.latex(rf"{sp.latex(f_simbolica)} = 0")
        
        st.subheader(f"🎯 Primeira Derivada: $d{l_dep}/d{l_ind}$")
        if math.isnan(res_num):
            st.error("O resultado numérico é indefinido ou complexo neste ponto.")
        else:
            st.latex(rf"\frac{{d {l_dep}}}{{d {l_ind}}} \approx {res_num:.8f}")
            
            # Validação Analítica
            try:
                val_analitico = float(sp.re(der_simb.subs(sub_dict)).evalf())
                c1, c2 = st.columns(2)
                c1.metric("Valor Analítico (SymPy)", f"{val_analitico:.8f}")
                erro = abs((res_num - val_analitico)/val_analitico * 100) if val_analitico != 0 else 0
                c2.metric("Erro Relativo", f"{erro:.2e} %")
            except:
                st.warning("Não foi possível calcular o valor analítico exato.")

        with st.expander("🔍 Ver Fórmula Simbólica da 1ª Derivada"):
            st.latex(sp.latex(der_simb))

        # --- SEGUNDA DERIVADA ---
        if calc_segunda:
            st.divider()
            if modo_implicito and var_dep_sym:
                # Fórmula da 2ª derivada implícita
                Fxx_s = sp.diff(f_simbolica, v1_sym, 2)
                Fyy_s = sp.diff(f_simbolica, var_dep_sym, 2)
                Fxy_s = sp.diff(f_simbolica, v1_sym, var_dep_sym)
                der2_simb = -(Fxx_s * df_dy_s**2 - 2 * Fxy_s * df_dx_s * df_dy_s + Fyy_s * df_dx_s**2) / (df_dy_s**3)
                
                # Numérico
                f0 = calcular_seguro(F_num, v1_calc, v2_calc)
                Fxx_n = (calcular_seguro(F_num, v1_calc + h, v2_calc) - 2*f0 + calcular_seguro(F_num, v1_calc - h, v2_calc)) / (h**2)
                Fyy_n = (calcular_seguro(F_num, v1_calc, v2_calc + h) - 2*f0 + calcular_seguro(F_num, v1_calc, v2_calc - h)) / (h**2)
                Fxy_n = (calcular_seguro(F_num, v1_calc+h, v2_calc+h) - calcular_seguro(F_num, v1_calc+h, v2_calc-h) - 
                         calcular_seguro(F_num, v1_calc-h, v2_calc+h) + calcular_seguro(F_num, v1_calc-h, v2_calc-h)) / (4 * h**2)
                res2_num = -(Fxx_n * Fy_n**2 - 2 * Fxy_n * Fx_n * Fy_n + Fyy_n * Fx_n**2) / (Fy_n**3) if Fy_n != 0 else float('nan')
            else:
                der2_simb = sp.diff(f_simbolica, v1_sym, 2)
                res2_num = (calcular_seguro(F_num, v1_calc + h) - 2*calcular_seguro(F_num, v1_calc) + calcular_seguro(F_num, v1_calc - h)) / (h**2)

            st.subheader(f"🎯 Segunda Derivada: $d^2{l_dep}/d{l_ind}^2$")
            if math.isnan(res2_num):
                st.error("O resultado da 2ª derivada é indefinido neste ponto.")
            else:
                st.latex(rf"\frac{{d^2 {l_dep}}}{{d {l_ind}^2}} \approx {res2_num:.8f}")
                try:
                    val_analitico2 = float(sp.re(der2_simb.subs(sub_dict)).evalf())
                    st.metric("Valor Analítico 2ª (SymPy)", f"{val_analitico2:.8f}")
                except:
                    pass
            
            with st.expander("🔍 Ver Fórmula Simbólica da 2ª Derivada"):
                st.latex(sp.latex(der2_simb))

    except Exception as e:
        st.error(f"Ocorreu um erro na análise: {e}")
        st.info("Verifique se usou parênteses corretamente e se as variáveis coincidem.")

if __name__ == "__main__":
    app()