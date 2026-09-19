import streamlit as st
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(page_title="Analisador de Derivadas Profissional", layout="wide")

st.title("📈 Analisador de Derivadas e Descoberta de Modelos")
st.markdown("""
Esta ferramenta utiliza o filtro de *Savitzky-Golay* para processamento e 
*Regressão Polinomial* para sugerir uma equação matemática para seus dados.
""")

arquivo_subido = st.file_uploader("Arraste seu arquivo CSV aqui", type="csv")

if arquivo_subido is not None:
    try:
        df = pd.read_csv(arquivo_subido)
        nome_x, nome_y = df.columns[0], df.columns[1]
        df_limpo = df.apply(pd.to_numeric, errors='coerce').dropna()
        x, y = df_limpo.iloc[:, 0].values, df_limpo.iloc[:, 1].values

        if len(x) < 5:
            st.error("O arquivo precisa de pelo menos 5 pontos.")
        else:
            # 1. Parâmetros e Processamento
            st.sidebar.header("🔧 Parâmetros")
            janela = st.sidebar.slider("Janela", 5, min(len(x)-1, 101), 15, step=2)
            ordem_poli = st.sidebar.slider("Ordem do Polinômio", 2, 5, 3)
            
            h_medio = np.mean(np.diff(x))
            y_suave = savgol_filter(y, janela, ordem_poli, deriv=0)
            derivada1 = savgol_filter(y, janela, ordem_poli, deriv=1, delta=h_medio)
            derivada2 = savgol_filter(y, janela, ordem_poli, deriv=2, delta=h_medio)

            # 2. Visualização dos Gráficos (4 níveis)
            fig, axes = plt.subplots(4, 1, figsize=(10, 18))
            axes[0].scatter(x, y, color='black', s=5, alpha=0.3, label='Brutos')
            axes[1].plot(x, y_suave, color='blue', label='Suavizado')
            axes[2].plot(x, derivada1, color='red', label='1ª Derivada')
            axes[3].plot(x, derivada2, color='purple', label='2ª Derivada')
            for ax in axes: ax.grid(True, alpha=0.5); ax.legend()
            plt.tight_layout()
            st.pyplot(fig)

            # --- NOVA FUNCIONALIDADE: DESCOBERTA DE EQUAÇÃO ---
            st.divider()
            st.subheader("🧪 Descoberta de Equação Matemática")
            st.warning("⚠️ O computador tentou encontrar a equação que mais se parece com o sinal suavizado, use com cuidado!")

            # 1. Extração inteligente do símbolo:
            # Pega a primeira letra da coluna, remove espaços ou símbolos e põe em minúsculo
            import re
# Remove números e símbolos, mantém a primeira letra original (Maiúscula ou Minúscula)
            letras_apenas = re.sub(r'[^a-zA-Z]', '', nome_x)
            simbolo = letras_apenas[0] if letras_apenas else 'x'

            # Ajustamos um polinômio de 3º grau: y = ax³ + bx² + cx + d
            coeffs = np.polyfit(x, y_suave, 3)
            a, b, c, d = coeffs

            # 3. Exibição da legenda e da fórmula
            st.markdown(f"Considerando *${simbolo}$* como a variável *{nome_x}*:")
            # Criando a representação em LaTeX
            # Usamos f-strings para colocar os coeficientes na fórmula
            formula_latex = rf"f({simbolo}) = {a:.4f}{simbolo}^3 + ({b:.4f}){simbolo}^2 + ({c:.4f}){simbolo} + ({d:.4f})"
            
            st.markdown("O modelo matemático aproximado para os seus dados é:")
            st.latex(formula_latex)
            
            st.info("""
            *Nota:* Esta é uma aproximação polinomial de 3º grau. Ela é excelente para 
            entender a tendência geral, mas pode não capturar variações locais muito bruscas.
            """)

            # 3. Exportação e Tabela
            df_res = pd.DataFrame({
                nome_x: x, f'{nome_y}_suave': y_suave, 
                '1_derivada': derivada1, '2_derivada': derivada2
            }).round(4)

            with st.expander("Clique para abrir a tabela de dados completa"):
                st.dataframe(df_res, use_container_width=True)

            csv_saida = df_res.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Relatório (CSV)", csv_saida, "analise_completa.csv")

    except Exception as e:
        st.error(f"Erro: {e}")