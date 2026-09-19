import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Simulador de Estática: Vetores", layout="centered")
st.title("🏹 Analisador de Vetores: Equilíbrio de Forças")
st.markdown("Encontre a Resultante e o Vetor Equilibrante para sistemas em estática.")

# 2. ENTRADAS DO USUÁRIO
col1, col2 = st.columns(2)

with col1:
    st.subheader("Vetor A (Azul)")
    mag_A = st.number_input("Magnitude A", value=10.0, key="mag_a")
    ang_A = st.number_input("Ângulo A (°)", value=45.0, key="ang_a")

with col2:
    st.subheader("Vetor B (Verde)")
    mag_B = st.number_input("Magnitude B", value=10.0, key="mag_b")
    ang_B = st.number_input("Ângulo B (°)", value=135.0, key="ang_b")

# --- 3. CÁLCULOS MATEMÁTICOS ---
rad_A, rad_B = np.radians(ang_A), np.radians(ang_B)
ax_v, ay_v = mag_A * np.cos(rad_A), mag_A * np.sin(rad_A)
bx_v, by_v = mag_B * np.cos(rad_B), mag_B * np.sin(rad_B)

# Resultante R
Rx, Ry = ax_v + bx_v, ay_v + by_v
mag_R = np.sqrt(Rx**2 + Ry**2)
ang_R = np.degrees(np.arctan2(Ry, Rx))
ang_display_R = ang_R % 360

# --- 4. CONFIGURAÇÃO DA BARRA LATERAL ---
st.sidebar.header("⚙️ Ferramentas de Análise")
modo_soma = st.sidebar.checkbox("Ativar Método Ponta com Cauda", value=False)
alvo_perp = st.sidebar.selectbox("Vetor Perpendicular (+90°):", ["Nenhum", "A", "B", "R"])
ativar_equilibrante = st.sidebar.checkbox("Calcular Vetor Equilibrante (E)", value=False)

# --- 5. LÓGICA DO VETOR EQUILIBRANTE ---
Ex, Ey, mag_E, ang_E = 0, 0, 0, 0
if ativar_equilibrante:
    # O Equilibrante é o oposto da Resultante
    Ex, Ey = -Rx, -Ry
    mag_E = mag_R
    ang_E = (ang_display_R + 180) % 360

# --- 6. EXIBIÇÃO DE MÉTRICAS ---
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Vetor A (x, y)", f"({ax_v:.2f}, {ay_v:.2f})")
m2.metric("Vetor B (x, y)", f"({bx_v:.2f}, {by_v:.2f})")
m3.metric("Resultante R", f"({Rx:.2f}, {Ry:.2f})", delta=f"Mag: {mag_R:.2f}")

# Se o equilibrante estiver ativo, mostra métricas extras abaixo
if ativar_equilibrante:
    st.write("---")
    e1, e2 = st.columns(2)
    e1.info(f"**Vetor Equilibrante E (x, y):** ({Ex:.2f}, {Ey:.2f})")
    e2.info(f"**Polar E:** Mag: {mag_E:.2f} | Ângulo: {ang_E:.1f}°")

# --- 7. GRÁFICO INTERATIVO ---
fig = go.Figure()

def desenhar_vetor(orig_x, orig_y, vx, vy, cor, nome, largura=5, dash=None):
    fig.add_trace(go.Scatter(
        x=[orig_x, orig_x + vx], y=[orig_y, orig_y + vy],
        mode='lines+markers',
        name=nome,
        line=dict(color=cor, width=largura, dash=dash),
        marker=dict(size=12, symbol='arrow-bar-up', angleref='previous'),
        hovertemplate=f"<b>{nome}</b><br>X: %{{x:.2f}}<br>Y: %{{y:.2f}}<extra></extra>"
    ))

# Desenho base (Soma comum ou Ponta com Cauda)
if modo_soma:
    desenhar_vetor(0, 0, ax_v, ay_v, '#636EFA', 'Vetor A')
    desenhar_vetor(ax_v, ay_v, bx_v, by_v, '#00CC96', 'Vetor B')
else:
    desenhar_vetor(0, 0, ax_v, ay_v, '#636EFA', 'Vetor A')
    desenhar_vetor(0, 0, bx_v, by_v, '#00CC96', 'Vetor B')

desenhar_vetor(0, 0, Rx, Ry, '#EF553B', 'Resultante R', largura=8)

# Desenha o Equilibrante
if ativar_equilibrante:
    desenhar_vetor(0, 0, Ex, Ey, '#FFA500', 'Equilibrante E', largura=6, dash=None)

# Lógica Perpendicular (Complexos)
if alvo_perp != "Nenhum":
    mapping = {"A": (ax_v, ay_v), "B": (bx_v, by_v), "R": (Rx, Ry)}
    bx, by = mapping[alvo_perp]
    z_perp = complex(bx, by) * 1j
    desenhar_vetor(0, 0, z_perp.real, z_perp.imag, '#FFEB3B', f"Perp de {alvo_perp}", dash='dash')

# Ajustes de Layout
limit = max(mag_A, mag_B, mag_R, mag_E) * 1.3
fig.update_layout(
    template="plotly_dark",
    xaxis=dict(range=[-limit, limit], zeroline=True, zerolinewidth=3, zerolinecolor='white', title="Eixo X (i)"),
    yaxis=dict(range=[-limit, limit], zeroline=True, zerolinewidth=3, zerolinecolor='white', title="Eixo Y (j)", scaleanchor="x", scaleratio=1),
    height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
)
fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=10, color='white', symbol='circle-open-dot'), showlegend=False))

st.plotly_chart(fig, use_container_width=True)

st.info(f"💡 **Resultado Final:** Magnitude **{mag_R:.2f}** apontando para **{ang_display_R:.2f}°**.")
# 8. MENSAGEM DE EQUILÍBRIO
if ativar_equilibrante:
    st.success(f"✅ Se aplicarmos uma força de **{mag_E:.2f}** a **{ang_E:.1f}°**, o sistema estará em **EQUILÍBRIO** (Soma das forças = 0).")