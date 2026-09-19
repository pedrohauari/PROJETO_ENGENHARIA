import streamlit as st
import sympy as sp
import math
import string
from sympy.abc import _clash

def formatar_latex(nome):
    # Se for uma letra grega, adiciona a barra invertida para o LaTeX
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    if nome.lower() in gregas:
        return f"\\{nome}"
    return nome

def app():
    # --- PREPARAÇÃO DE SÍMBOLOS ---
    latino = list(string.ascii_lowercase + string.ascii_uppercase)
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    todos_simbolos = latino + gregas + [g.capitalize() for g in gregas]

    st.title("Calculadora de Derivadas Inteligente")

    with st.sidebar:
        st.header("🔧 Configurações")
        col_v = st.columns(2)
        var_indep = col_v[0].selectbox("Independente", todos_simbolos, index=todos_simbolos.index('x'))
        var_dep = col_v[1].selectbox("Dependente", todos_simbolos, index=todos_simbolos.index('y'))
        
        entrada_raw = st.text_input("Equação:", value=f"{var_dep} = sin({var_indep})", key="func_raw")
        
        col_pts = st.columns(2)
        v1_val = col_pts[0].number_input(f"Valor de {var_indep}:", value=1.0)
        v2_val = col_pts[1].number_input(f"Valor de {var_dep}:", value=1.0)
        
        st.divider()
        unidade = st.radio("Unidade Angular:", ("Radianos", "Graus"))
        h = 1e-5 
        calc_segunda = st.checkbox("Calcular 2ª Derivada?", value=False)

    try:
        # --- MOTOR DE INTELIGÊNCIA DA ENTRADA ---
        # 1. Definimos os símbolos baseados na escolha do usuário
        v1_sym = sp.Symbol(var_indep)
        v2_sym = sp.Symbol(var_dep)

        # 2. Criamos um dicionário de 'locals' para o sympify não se perder
        # Isso garante que 'e' seja o número de Euler e 'pi' seja 3.1415...
        contexto_matematico = {
            **_clash, 
            var_indep: v1_sym, 
            var_dep: v2_sym,
            "e": sp.E,
            "pi": sp.pi,
            "exp": sp.exp,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan
        }

        # 3. Limpeza de texto (substitui ^ por **)
        texto_limpo = entrada_raw.replace('^', '**')
        
        # 4. Transforma a igualdade em uma expressão nula (F(x,y) = 0)
        if "=" in texto_limpo:
            esq, dir = texto_limpo.split("=")
            f_simbolica = sp.sympify(f"({dir}) - ({esq})", locals=contexto_matematico)
        else:
            f_simbolica = sp.sympify(texto_limpo, locals=contexto_matematico)

        # --- ECO DA EQUAÇÃO (CONFIRMAÇÃO) ---
        st.info("📖 **Equação interpretada:**")
        # Mostramos a equação como F(var_ind, var_dep) = 0
        st.latex(rf"{sp.latex(f_simbolica)} = 0")

        # --- CÁLCULOS ---
        F = sp.lambdify((v1_sym, v2_sym), f_simbolica, "numpy")

        v1_calc = math.radians(v1_val) if unidade == "Graus" else v1_val
        v2_calc = math.radians(v2_val) if unidade == "Graus" else v2_val

        f0 = F(v1_calc, v2_calc)
        
        # Parciais Numéricas
        Fx_n = (F(v1_calc + h, v2_calc) - F(v1_calc - h, v2_calc)) / (2 * h)
        Fy_n = (F(v1_calc, v2_calc + h) - F(v1_calc, v2_calc - h)) / (2 * h)

        if Fy_n == 0:
            st.error("Erro: Derivada parcial em relação à variável dependente é zero (Divisão por zero).")
            return

        dy_dx_num = -Fx_n / Fy_n

        # --- VALIDAÇÃO ANALÍTICA (1ª ORDEM) ---
        df_dx_s = sp.diff(f_simbolica, v1_sym)
        df_dy_s = sp.diff(f_simbolica, v2_sym)
        dy_dx_expr = -df_dx_s / df_dy_s
        val_exato_1 = float(dy_dx_expr.subs({v1_sym: v1_calc, v2_sym: v2_calc}))
        erro_1 = abs((dy_dx_num - val_exato_1) / val_exato_1 * 100) if val_exato_1 != 0 else 0

        # --- RESULTADOS 1ª ORDEM ---
        l_ind = formatar_latex(var_indep)
        l_dep = formatar_latex(var_dep)
        
        st.subheader(f"🎯 Derivada de {var_dep} em relação a {var_indep}")
        st.latex(rf"\frac{{d {l_dep}}}{{d {l_ind}}} \approx {dy_dx_num:.8f}")

        c1, c2 = st.columns(2)
        c1.metric("Valor Exato", f"{val_exato_1:.8f}")
        c2.metric("Erro Relativo", f"{erro_1:.2e} %")

        with st.expander("Ver fórmula analítica"):
            st.latex(rf"\frac{{d {l_dep}}}{{d {l_ind}}} = {sp.latex(dy_dx_expr)}")

        # --- 2ª ORDEM ---
        if calc_segunda:
            st.divider()
            # Numérico
            Fxx = (F(v1_calc + h, v2_calc) - 2*f0 + F(v1_calc - h, v2_calc)) / (h**2)
            Fyy = (F(v1_calc, v2_calc + h) - 2*f0 + F(v1_calc, v2_calc - h)) / (h**2)
            Fxy = (F(v1_calc+h, v2_calc+h) - F(v1_calc+h, v2_calc-h) - 
                   F(v1_calc-h, v2_calc+h) + F(v1_calc-h, v2_calc-h)) / (4 * h**2)
            
            d2y_dx2_num = -(Fxx * Fy_n**2 - 2 * Fxy * Fx_n * Fy_n + Fyy * Fx_n**2) / (Fy_n**3)
            
            # Analítico
            Fxx_s = sp.diff(f_simbolica, v1_sym, 2)
            Fyy_s = sp.diff(f_simbolica, v2_sym, 2)
            Fxy_s = sp.diff(f_simbolica, v1_sym, v2_sym)
            d2y_dx2_expr = -(Fxx_s * df_dy_s**2 - 2 * Fxy_s * df_dx_s * df_dy_s + Fyy_s * df_dx_s**2) / (df_dy_s**3)
            
            val_exato_2 = float(d2y_dx2_expr.subs({v1_sym: v1_calc, v2_sym: v2_calc}))
            erro_2 = abs((d2y_dx2_num - val_exato_2) / val_exato_2 * 100) if val_exato_2 != 0 else 0

            st.subheader("🎯 Segunda Derivada")
            st.latex(rf"\frac{{d^2 {l_dep}}}{{d {l_ind}^2}} \approx {d2y_dx2_num:.8f}")
            
            c3, c4 = st.columns(2)
            c3.metric("Valor Exato", f"{val_exato_2:.8f}")
            c4.metric("Erro Relativo", f"{erro_2:.2e} %")
            
            with st.expander("Ver fórmula analítica 2ª ordem"):
                st.latex(rf"\frac{{d^2 {l_dep}}}{{d {l_ind}^2}} = {sp.latex(d2y_dx2_expr)}")

    except Exception as e:
        st.error(f"Erro no Processamento: Verifique a Sintaxe da equacao.")
        st.info("Dica: Use parênteses em funções. Ex: sin(x) em vez de sin x.")
        print(f"Erro: {e}")

if __name__ == "__main__":
    app()