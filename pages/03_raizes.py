import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from sympy.abc import _clash

# ==========================================
# 1. CONFIGURAÇÕES INICIAIS
# ==========================================
st.set_page_config(page_title="Engenharia: Achador de Raízes", layout="wide")


# Dicionário para o SymPy entender 'e' como a constante de Euler
# e garantir que variáveis como 'S' ou 'E' não quebrem o código
definicoes_extras = {'e': sp.E, "pi": sp.pi, "PI": sp.pi, "ln":sp.log, "log10": lambda x:sp.log(x,10)}

def verificar_viabilidade(expr_sym, var_sym):  # AGORA RECEBE UMA VARIÁVEL
    """Analisa a função antes de tentar calcular numericamente."""
    
    try:
        solucoes = sp.solve(expr_sym, var_sym) # TENTA RESOLVER PARA A VARIÁVEL ESPECÍFICA
        if not solucoes:
            if expr_sym.simplify().is_number and expr_sym.simplify() != 0:
                return "impossivel"
            return "ok"
        
        tem_raiz_real = any(sol.is_real for sol in solucoes if hasattr(sol, 'is_real'))
        if not tem_raiz_real:
            return "complexa"
        return "ok"
    except:
        return "ok"

# ==========================================
# 2. INTERFACE E ENTRADA DE DADOS
# ==========================================
st.title("🚀 Calculadora de Raízes Profissional")
st.markdown("---")
st.write("Digite as funções para resolver a equação **f(x) = g(x)**. Se quiser apenas a raiz de f(x), deixe o g(x) como 0.")
st.write("O programa irá fazer f(x) - g(x) = 0 internamente para encontrar as raízes.")
st.sidebar.title("🔧 Configurações")
st.sidebar.info("""
**Nota:** Este projeto utiliza métodos numéricos reais. 
Atualmente, ele identifica e calcula apenas **raízes reais**. 
Soluções no campo dos números complexos serão ignoradas.
""")
st.sidebar.info("Os ângulos de funções trigonométricas devem ser inseridos em radianos. lembrando que 180° = π radianos.")
# Entrada da Função 
col_f, col_g = st.columns(2)
with col_f:
    expr_f_str = st.text_input("Função f(x):", value="x**2 - 4", key = "f_input")
with col_g:
    expr_g_str = st.text_input("Função g(x) (Opcional):", value="0", key = "g_input")

# ==========================================
# 3. PROCESSAMENTO SIMBÓLICO (SymPy)
# ==========================================
mostrar_secao_calculo = False

try:
    # Interpretação da função
    expr_f_sym = sp.sympify(expr_f_str, locals={**_clash, **definicoes_extras})

    # INTERPRETA O INPUT DE g(x) APENAS SE O USUÁRIO DIGITAR ALGO VÁLIDO E DIFERENTE DE ZERO, PARA EVITAR PROBLEMAS COM SIMPLIFICAÇÃO
    if expr_g_str.strip() and expr_g_str.strip() != "0":
        expr_g_sym = sp.sympify(expr_g_str, locals={**_clash, **definicoes_extras})
        # SYMPY PRECISA QUE A EQUAÇÃO SEJA DO TIPO f(x) - g(x) = 0 PARA RESOLVER, ENTÃO SUBTRAÍMOS AS DUAS EXPRESSÕES
        expressao_sympy = expr_f_sym - expr_g_sym
        # VISUAL DO INPUT PARA O USUÁRIO, MOSTRANDO A EQUAÇÃO QUE ESTAMOS RESOLVENDO
        st.latex(f"{sp.latex(expr_f_sym)} = {sp.latex(expr_g_sym)} ")
    else:
        expressao_sympy = expr_f_sym
        st.latex(f"f(x) = {sp.latex(expr_f_sym)} = 0")
    simbolos = expressao_sympy.free_symbols
    if len(simbolos) == 0:
        st.error("A função deve conter pelo menos uma variável (ex: x).")
        mostrar_secao_calculo = False
    # ... (dentro do bloco onde detectamos os simbolos) ...

    elif len(simbolos) > 1:
        st.warning(f"Detectadas {len(simbolos)} variáveis: {simbolos}")
        
        # 1. Usuário escolhe a incógnita
        lista_nomes = sorted([str(s) for s in simbolos])
        var_incognita_str = st.selectbox("Qual variável você deseja encontrar?", lista_nomes)
        var_incognita_sym = sp.Symbol(var_incognita_str)
        
        # 2. Criar inputs para as outras variáveis (os parâmetros)
        st.write("Defina os valores para as outras variáveis:")
        valores_parametros = {}
        
        cols = st.columns(len(lista_nomes) - 1)
        idx = 0
        for s_nome in lista_nomes:
            if s_nome != var_incognita_str:
                with cols[idx]:
                    val = st.number_input(f"Valor de {s_nome}:", value=1.0, step=0.1, format="%.6f", key=f"input_{s_nome}")
                    valores_parametros[s_nome] = val
                    idx += 1
        
        # 3. A MÁGICA: Substituir os valores na equação
        # Isso transforma PV = nRT em (2)*V - (1)*(0.082)*(300) = 0
        expressao_final = expressao_sympy.subs(valores_parametros)
        
        st.write(f"Resolvendo para {var_incognita_str}:")
        st.latex(sp.latex(expressao_final) + " = 0")
        
        # Agora var_sym vira a nossa incógnita escolhida
        var_sym = var_incognita_sym
        expressao_sympy = expressao_final # A partir daqui, o resto do código funciona normal!
    else:   
        var_sym = list(simbolos)[0]
        st.success(f"✅ Equação válida. Variável independente detectada: **{var_sym}**")

    # Verificação de Viabilidade
    status = verificar_viabilidade(expressao_sympy, var_sym)
    mostrar_secao_calculo = True  # Habilita a seção de cálculo para mostrar mensagens de aviso ou erro, mesmo que a função seja "ok"
    
    if status == "impossivel":
        st.error("❌ Esta equação não possui solução lógica (ex: $x = x + 1$).")
    elif status == "complexa":
        st.warning("⚠️ Esta função possui apenas raízes complexas (não cruza o eixo X).")
        mostrar_secao_calculo = True
    else:
        st.success("✅ Equação válida. Gráfico gerado abaixo.")
        mostrar_secao_calculo = True

except Exception as e:
    st.error(f"Erro ao interpretar a função: {e}")

# ==========================================
# 4. GRÁFICO E MÉTODOS NUMÉRICOS
# ==========================================
if mostrar_secao_calculo:
    st.markdown("---")
    st.subheader("📊 Análise Gráfica e Numérica")
    st.write("Escolha o intervalo de pesquisa para o eixo X:")
    
    # Configuração dos limites do gráfico
    c1, c2 = st.columns(2)
    with c1:
        x_min = st.number_input("**`X mínimo do gráfico`**", value=-10.0, key="xmin")
    with c2:
        x_max = st.number_input("**`X máximo do gráfico`**", value=10.0, key="xmax")

    if x_min >= x_max:
        st.error("O limite mínimo deve ser menor que o máximo.")
    else:
        # Preparação das funções numéricas
        
        f_num = sp.lambdify(var_sym, expressao_sympy, modules=['numpy'])
        derivada_sym = sp.diff(expressao_sympy, var_sym)
        f_prime_num = sp.lambdify(var_sym, derivada_sym, modules=['numpy'])

        # Geração dos pontos do gráfico
        var_plot = np.linspace(x_min, x_max, 500)
        y_plot = f_num(var_plot)

        # Configuração do gráfico Matplotlib
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(var_plot, y_plot, label=f'$f({var_sym})$', color='#1f77b4', lw=2)
        ax.axhline(0, color='black', lw=1)
        ax.axvline(0, color='black', lw=1)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlabel(f'{var_sym}')
        ax.set_ylabel(f"f({var_sym})")
        
        # --- ÁREA DE CÁLCULO ---
        st.write("Escolha um método para encontrar a raiz exata:")
        tab1, tab2 = st.tabs(["🚀 Método de Newton (Rápido)", "🛡️ Método de Brent (Robusto)"])

        raiz_encontrada = None

        with tab1:
            chute = st.number_input("Chute inicial (x0):", value=1.0, step=0.1, key="n_chute")
            if st.button("Calcular via Newton"):
                try:
                    res = optimize.root_scalar(f_num, fprime=f_prime_num, x0=chute, method='newton')
                    if res.converged:
                        raiz_encontrada = res.root
                        valor_na_raiz = f_num(raiz_encontrada)
                        if np.abs(valor_na_raiz) < 1e-3:
                            st.success(f"Raiz encontrada: **{raiz_encontrada:.6f}** em {res.iterations} iterações.")
                            st.write(f"Conferindo: $f({raiz_encontrada:.6f}) = {valor_na_raiz:.2e}$")
                    else:
                        st.error("Newton não convergiu. Tente outro chute ou use o modo Robusto.")                       
                except ZeroDivisionError:
                    st.error("💥 **Erro de Singularidade:** O método de Newton tentou dividir por zero.")
                    st.info("Isso acontece quando a derivada é zero ou o chute está em um ponto indefinido (como x=0 em 1/x). Tente outro chute!")

        with tab2:
            st.write("Escolha um intervalo [a,b] onde a função mude de sinal. o Método de Brent depende disso para garantir a convergência.")
            ca, cb = st.columns(2)
            with ca: a = st.number_input("Limite A:", value=x_min, key="b_a")
            with cb: b = st.number_input("Limite B:", value=x_max, key="b_b")
            
            if st.button("Calcular via Brent"):
                try:
                    res = optimize.root_scalar(f_num, bracket=[a, b], method='brentq')
                    if res.converged:
                        raiz_encontrada = res.root
                        st.success(f"Raiz encontrada: **{raiz_encontrada:.6f}**")
                except ZeroDivisionError:
                    st.error("💥 **Divisão por zero detectada.**")
                    st.warning("O método de Brent tentou avaliar a função em um ponto onde ela não existe (uma assíntota). Ajuste os limites A e B para desviar desse ponto.")
                except ValueError:
                    st.error("❌ Os sinais nos limites A e B devem ser diferentes (f(a) * f(b) < 0).")

        # Se uma raiz foi encontrada, marca no gráfico antes de mostrar
        if raiz_encontrada is not None:
            ax.plot(raiz_encontrada, 0, 'ro', markersize=3, label=f'Raiz: {raiz_encontrada:.4f}')
            ax.legend()
        
        st.pyplot(fig)
        # Na barra lateral, você pode mostrar os detalhes técnicos
with st.sidebar:
    st.header("📋 Relatório Técnico")
    if mostrar_secao_calculo:
        st.write(f"**Incógnita:** {var_sym}")
        st.write(f"**Método utilizado:** Newton/Brent")
        if raiz_encontrada is not None:
            st.metric("Raiz Final", f"{raiz_encontrada:.6f}")
            st.write("---")
            st.download_button("💾 Exportar para TXT", f"Raiz: {raiz_encontrada}", file_name="resultado.txt")
