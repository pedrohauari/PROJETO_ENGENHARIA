import streamlit as st
import numpy as np
import sympy as sp
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import pandas as pd 

st.set_page_config(page_title="Achador de Raízes complexas", layout="wide")

st.title("🌌 Buscador de Raízes no Plano Complexo")
st.markdown("Este programa encontra raízes complexas usando um sistema de busca robusto (fsolve).")

with st.expander("Guia de Síntaxe"):
    st.info("Variável: *z* | Conjugado: *conjugate(z)* | Módulo: *abs(z)* | Exponencial: *exp(z)*")
st.divider()

# 1. Configurações na Barra Lateral
st.sidebar.header("🎯 Área de Busca")
range_re = st.sidebar.slider("Alcance Real (±)", 1, 100, 10)
range_im = st.sidebar.slider("Alcance Imaginário (±)", 1, 100, 10)
densidade = st.sidebar.select_slider("Densidade da Grade", options=[10, 15, 20, 25], value=15)

# 2. Entrada da Equação
equacao_texto = st.text_input("Digite a equação (ex: A*z**2 + B = 0):", "exp(z) = -1")

if equacao_texto:
    try:
        # Parsing da Equação
        if "=" in equacao_texto:
            esq, dir_eq = equacao_texto.split("=")
            equacao_obj = sp.sympify(f"({esq}) - ({dir_eq})")
        else:
            equacao_obj = sp.sympify(equacao_texto)

        # --- NOVA LÓGICA DE PARÂMETROS E VARIÁVEIS ---
        simbolos = list(equacao_obj.free_symbols)
        
        if simbolos:
            # Identificar a variável principal (z, s ou w por preferência, ou a primeira da lista)
            var_principal = simbolos[0]
            for s in simbolos:
                if str(s).lower() in ['z', 's', 'w']:
                    var_principal = s
                    break
            
            # --- EXIBIÇÃO BONITA (Antes da substituição) ---
            st.subheader("📝 Expressão Simbólica:")
            st.latex(sp.latex(equacao_obj) + " = 0")

            st.sidebar.divider()
            st.sidebar.header("⚙️ Parâmetros Detectados")
            
            # Tratar os outros símbolos como parâmetros
            valores_parametros = {}
            outros_simbolos = [s for s in simbolos if s != var_principal]
            
            for p in outros_simbolos:
                # Cria um input numérico para cada letra extra encontrada
                valores_parametros[p] = st.sidebar.number_input(f"Valor de '{p}'", value=1.0, step=0.1)
            
            # Substituir os parâmetros na equação pelos valores do usuário
            equacao_obj = equacao_obj.subs(valores_parametros)
            
            st.info(f"Variável complexa detectada: **{var_principal}**")
        else:
            var_principal = sp.symbols('z') # Fallback se não houver letras

        st.subheader("Equação Processada:")
        st.latex(sp.latex(equacao_obj) + " = 0")

        # --- PREPARAÇÃO PARA O MODO ROBUSTO (OCULTO) ---
        a_sym, b_sym = sp.symbols('a b', real=True)
        # Substituímos a variável detectada (z, s, w...) por a + bi
        equacao_ab = equacao_obj.subs(var_principal, a_sym + sp.I * b_sym).expand()
        f_real_imag = sp.lambdify((a_sym, b_sym), [sp.re(equacao_ab), sp.im(equacao_ab)], modules='numpy')

        def sistema_real(vars):
            a_val, b_val = vars
            # Lidar com casos onde a função pode retornar um valor constante
            res = f_real_imag(a_val, b_val)
            return [float(res[0]), float(res[1])]

        # 3. Visualização da Região de Busca
        st.subheader("🗺️ Mapa de Varredura")
        fig_map, ax_map = plt.subplots(figsize=(6, 4))
        rect = plt.Rectangle((-range_re, -range_im), 2*range_re, 2*range_im, 
                              color='blue', alpha=0.15, label='Zona de Busca')
        ax_map.add_patch(rect)
        ax_map.axhline(0, color='black', lw=1)
        ax_map.axvline(0, color='black', lw=1)
        ax_map.set_xlim(-range_re*1.2, range_re*1.2)
        ax_map.set_ylim(-range_im*1.2, range_im*1.2)
        ax_map.set_xlabel(f"Re({var_principal})")
        ax_map.set_ylabel(f"Im({var_principal})")
        ax_map.grid(True, linestyle=':', alpha=0.6)
        st.pyplot(fig_map)

        # 4. Cálculo das Raízes
        if st.button("🚀 Iniciar Varredura"):
            st.toast("Modo Robusto ativado: Decompondo em sistema real 2x2...", icon="⚙️")
            
            re_pts = np.linspace(-range_re, range_re, densidade)
            im_pts = np.linspace(-range_im, range_im, densidade)
            
            raizes_encontradas = []
            progresso = st.progress(0)
            total = len(re_pts)
            
            for i, re_start in enumerate(re_pts):
                for im_start in im_pts:
                    try:
                        sol = fsolve(sistema_real, [re_start, im_start])
                        erro = np.linalg.norm(sistema_real(sol))
                        if erro < 1e-5:
                            raiz = np.round(sol[0], 5) + 1j * np.round(sol[1], 5)
                            raizes_encontradas.append(raiz)
                    except:
                        continue
                progresso.progress((i + 1) / total)

            raizes_unicas = sorted(list(set(raizes_encontradas)), key=lambda x: (x.real, x.imag))

            if raizes_unicas:
                st.success(f"Encontradas {len(raizes_unicas)} raízes únicas!")
                for r in raizes_unicas:
                    ax_map.scatter(r.real, r.imag, color='red', s=40, edgecolors='white', zorder=5)
                st.subheader("Raízes localizadas (pontos vermelhos):")
                st.pyplot(fig_map)

                with st.expander("Verificar Tabela com as raízes complexas"):
                    df_raizes = pd.DataFrame({
                        "Forma Complexa": [f"{r.real:.4f} {'+' if r.imag >= 0 else '-'} {abs(r.imag):.4f}i" for r in raizes_unicas],
                        "Parte Real": [r.real for r in raizes_unicas],
                        "Parte Imaginária": [r.imag for r in raizes_unicas]
                    })
                    st.dataframe(df_raizes, use_container_width=True)
                    st.divider()
                    csv_saida = df_raizes.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar Relatório (CSV)", csv_saida, "raízes_complexas.csv")
            else:
                st.warning("Nenhuma raiz encontrada. Tente aumentar a densidade ou mudar o alcance.")

    except Exception as e:
        st.error(f"Erro na interpretação: {e}")