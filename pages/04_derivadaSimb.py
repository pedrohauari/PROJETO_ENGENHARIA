import streamlit as st
import sympy as sp
import numpy as np
import string

# --- FUNÇÃO DE LIMPEZA VISUAL (V2: COM SUPORTE A GREGO) ---
def limpar_notacao_tempo(expr, vars_tempo, t_sym):
    """
    Varre a expressão do SymPy e substitui a notação pesada por notação mais limpa, especialmente para derivadas temporais. 
    Corrige automaticamente o LaTeX para letras gregas.
    """
    gregas = [
        "alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
        "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
        "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"
    ]
    
    expr_limpa = expr
    for v in vars_tempo:
        # Define como o SymPy enxerga a variável internamente (como funcao)
        func = sp.Function(v)(t_sym)
        derivada = sp.diff(func, t_sym)
        
        # PASSO 1: Formatação da derivada (Tratamento especial para Gregas)
        if v.lower() in gregas:
            # Força o comando LaTeX (ex: \theta')
            simbolo_derivada = sp.Symbol(rf"\{v}'")
        else:
            # Letra normal (ex: x')
            simbolo_derivada = sp.Symbol(rf"{v}'")
            
        expr_limpa = expr_limpa.subs(derivada, simbolo_derivada)
        
        # PASSO 2: Substitui a função base, removendo o (t)
        simbolo_base = sp.Symbol(v)
        expr_limpa = expr_limpa.subs(func, simbolo_base)
        
    return expr_limpa

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Calculadora de Engenharia - Derivadas", 
    layout="centered", 
    page_icon="⚙️"
)

def calculadora():
    # PREPARAÇÃO DOS SÍMBOLOS 
    latino = list(string.ascii_lowercase + string.ascii_uppercase)
    gregas = [
        "alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
        "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
        "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"
    ]
    todos_simbolos = latino + gregas + [g.capitalize() for g in gregas]

    st.title("⚙️ Calculadora de Derivadas Profissional")
    st.markdown("---") 
    
    

    # --- INTERFACE LATERAL ---
    st.sidebar.header("🔧 Configurações")
    
    modo = st.sidebar.radio("Modo de Cálculo:", ["Explícita", "Implícita", "Taxas Relacionadas"])
    
    entrada_raw = st.sidebar.text_area("Digite a função/equação:", "x^3 + x^2 + x", help="Use '*' para multiplicar e '^' para potência.")
    entrada_usuario = entrada_raw.replace('^', '**') 

    # Lógica de seleção de variáveis baseada no modo
    if modo == "Explícita":
        var_indep = st.sidebar.selectbox("Variável Independente (x):", todos_simbolos, index=23)
        var_dep = None
    elif modo == "Implícita":
        var_indep = st.sidebar.selectbox("Variável Independente (x):", todos_simbolos, index=23)
        var_dep = st.sidebar.selectbox("Variável Dependente (y):", todos_simbolos, index=24)
    else: # Taxas Relacionadas
        vars_tempo = st.sidebar.multiselect(
            "Variáveis que dependem do tempo (t):", 
            todos_simbolos, 
            default=["x", "theta"] if "theta" in todos_simbolos else ["x", "y"]
        )
        t_sym = sp.symbols('t')

    n = st.sidebar.number_input("Ordem da derivada (n):", min_value=1, value=1, step=1)
    
    tipo_simplificacao = st.sidebar.selectbox(
        "Nível de Simplificação:", 
        ["Leve (Rápido)", "Médio (Cancel)", "Profundo (Lento)"],
        index=1
    )
    

    # --- PROCESSAMENTO ---
    try:
        # Limpeza da equação => f(x) = g(x)  vira f(x) - g(x) = 0 para o sympy fazer as contas
        if "=" in entrada_usuario:
            lado_esquerdo, lado_direito = entrada_usuario.split("=")
            texto_para_sympy = f"({lado_esquerdo}) - ({lado_direito})"
        else:
            texto_para_sympy = entrada_usuario

        f = sp.sympify(texto_para_sympy, locals={"e": sp.E})

        if modo == "Taxas Relacionadas":
            st.subheader("🕒 Análise de Taxas Relacionadas")
            
            with st.spinner("Derivando em relação ao tempo..."):
                # PASSO CRÍTICO: Transformar símbolos em Funções do Tempo f(t)
                substituicoes = {sp.symbols(v): sp.Function(v)(t_sym) for v in vars_tempo}
                f_temporal = f.subs(substituicoes)
                
                # Derivada total em relação a t
                resultado = sp.diff(f_temporal, t_sym, n)
                notacao = rf"\frac{{d^{{{n}}}}}{{dt^{{{n}}}}}" if n > 1 else r"\frac{d}{dt}"
                
        elif modo == "Implícita" and var_dep:
            x_sym = sp.symbols(var_indep)
            y_sym = sp.symbols(var_dep)
            st.subheader("📝 Equação Analisada")
            st.latex(f"{sp.latex(f)} = 0")
            
            with st.spinner("Calculando derivada implícita..."):
                resultado = sp.idiff(f, y_sym, x_sym, n)
                notacao = rf"\frac{{d^{{{n}}}{var_dep}}}{{d{var_indep}^{{{n}}}}}" if n > 1 else rf"\frac{{d{var_dep}}}{{d{var_indep}}}"
        
        else: # Explícita
            x_sym = sp.symbols(var_indep)
            st.subheader("📝 Função Original")
            st.latex(f"f({var_indep}) = {sp.latex(f)}")
            
            with st.spinner("Calculando derivada..."):
                resultado = sp.diff(f, x_sym, n)
                notacao = rf"\frac{{d^{{{n}}}}}{{d{var_indep}^{{{n}}}}}" if n > 1 else rf"\frac{{d}}{{d{var_indep}}}"

        # --- SIMPLIFICAÇÃO ---
        if tipo_simplificacao == "Leve (Rápido)":
            resultado_final = resultado
        elif tipo_simplificacao == "Médio (Cancel)":
            resultado_final = sp.cancel(resultado)
        else:
            resultado_final = sp.simplify(resultado)

        # --- APLICAÇÃO DA LIMPEZA VISUAL ---
        if modo == "Taxas Relacionadas":
            # Aqui acionamos a função que criamos lá em cima!
            resultado_exibicao = limpar_notacao_tempo(resultado_final, vars_tempo, t_sym)
            f_exibicao = limpar_notacao_tempo(f_temporal, vars_tempo, t_sym)
        else:
            resultado_exibicao = resultado_final
            f_exibicao = f

        # --- EXIBIÇÃO DO RESULTADO ---
        st.divider()
        st.subheader(f"🎯 Resultado")

        # Geramos o LaTeX do resultado já limpo
        latex_resultado = sp.latex(resultado_exibicao)
        latex_original = sp.latex(f_exibicao)

        # Aumentamos o limite significativamente
        if len(latex_resultado) > 5000:
            st.warning("⚠️ O resultado é grande demais, exibindo código:")
            st.code(str(resultado_exibicao), language="python")
        else:
            with st.container():
                if modo == "Taxas Relacionadas":
                    # Mostra d/dt [Equação] = Resultado
                    st.latex(rf"{notacao} \left[ {latex_original} \right] \implies {latex_resultado} = 0")
                else:
                    # Mostra dy/dx = Resultado
                    st.latex(rf"{notacao} = {latex_resultado}")

    except Exception as erro:
        st.error(f"❌ Erro: {erro}")
        st.info("Dica: Use '*' para multiplicações. Ex: 6*tan(theta).")
        

if __name__ == "__main__":
    calculadora()


