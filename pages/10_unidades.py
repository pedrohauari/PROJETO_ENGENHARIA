import streamlit as st
from pint import UnitRegistry
from sympy import degree

# 1. Inicializa o Registro de Unidades do Pint
ureg = UnitRegistry()


# Configuração da página
st.set_page_config(page_title="Conversor de Unidades", page_icon="📏", layout="centered")
st.title("📏 Conversor de Unidades Inteligente")
st.markdown("Alimentado pela biblioteca **Pint** para precisão científica.")

# 2. DICIONÁRIO DE MAPEAMENTO (Nome no App : Nome no Pint)
# A vantagem é que o Pint já sabe as fórmulas de temperatura sozinho!
categorias = {
    "Pressão": {
        "Pascal (Pa)": "pascal",
        "Atmosfera (atm)": "atm",
        "Bar": "bar",
        "PSI (lbf/in²)": "psi",
        "mmHg (Torr)": "mmHg"
    },
    "Volume": {
        "Metro Cúbico (m³)": "m**3",
        "Litro (L)": "liter",
        "Mililitro (ml)": "ml",
        "Galão (US)": "gallon",
        "Polegada Cúbica": "inch**3"
    },
    "Temperatura": {
        "Celsius (°C)": "degC",
        "Kelvin (K)": "kelvin",
        "Fahrenheit (°F)": "degF"
    },
    "Comprimento": {
        "Metros": "meter",
        "Quilômetros": "km",
        "Milhas": "mile",
        "Pés": "foot",
        "Polegadas": "inch"
    },
"Massa": {
        "Quilogramas": "kilogram",
        "Gramas": "gram",
        "Libras (lb)": "pound",
        "Onças (oz)": "ounce",
        "Toneladas (t)": "tonne"}
        ,
"Tempo": {
        "Segundos": "second",
        "Minutos": "minute",
        "Horas": "hour",
        "Dias": "day",
        "Semanas": "week",
        "Anos": "year" }, 
"Velocidade": {
        "Metros por Segundo (m/s)": "meter/second",
        "Quilômetros por Hora (km/h)": "km/hour",
        "Milhas por Hora (mph)": "mile/hour",
        "Pés por Segundo (ft/s)": "foot/second",
        "Nós (kn)": "knot"
}, 
"Aceleração": {
        "Metros por Segundo ao Quadrado (m/s²)": "meter/second**2",
        "Quilômetros por Hora ao Quadrado (km/h²)": "km/hour**2",
        "Milhas por Hora ao Quadrado (mph²)": "mile/hour**2",
        "Pés por Segundo ao Quadrado (ft/s²)": "foot/second**2",
        "Nós por Segundo (kn/s)": "knot/second"
} ,
"Energia": {
        "Joule (J)": "joule",
        "Quilojoule (kJ)": "kilojoule",
        "Quilowatt-hora (kWh)": "kilowatt_hour",
        "Caloria (cal)": "calorie",
        "Quilocaloria (kcal)": "kilocalorie",
        "BTU": "BTU",
        "eV (elétron-volt)": "electron_volt"
}, 
"Potência": {
        "Watt (W)": "watt",
        "Quilowatt (kW)": "kilowatt",
        "Megawatt (MW)": "megawatt",
        "Cavalos de Potência (hp)": "horsepower",
        "BTU/h": "BTU/hour", } ,
"Força": {
        "Newton (N)": "newton",
        "Quilonewton (kN)": "kilonewton",
        "Libra-força (lbf)": "pound_force",
        "Dina (dyn)": "dyne",
        "Kilograma-força (kgf)": "kilogram_force" },
"Angulo": {
        "Graus (°)": "degree",
        "Radianos (rad)": "radian",
        "Grados (gon)": "gradian",
        "Milésimos de Polegada (mil)": "mil" },
"Frequência": {
        "Hertz (Hz)": "hertz",
        "Quilohertz (kHz)": "kilohertz",
        "Megahertz (MHz)": "megahertz",
        "Gigahertz (GHz)": "gigahertz",
        "Revoluções por Minuto (RPM)": "revolution/minute" }, 
"Torque": {
        "Newton-metro (N·m)": "newton*meter",
        "Libra-polegada (lbf·in)": "pound_force*inch",
        "Libra-pé (lbf·ft)": "pound_force*foot",
        "Quilograma-força-metro (kgf·m)": "kilogram_force*meter",
        "Dina-centímetro (dyn·cm)": "dyne*centimeter" },
"Densidade": {
        "Quilograma por Metro Cúbico (kg/m³)": "kilogram/meter**3",
        "Gramas por Centímetro Cúbico (g/cm³)": "gram/centimeter**3",
        "Libras por Pé Cúbico (lb/ft³)": "pound/foot**3",
        "Onças por Polegada Cúbica (oz/in³)": "ounce/inch**3",
        "Gramas por Litro (g/L)": "gram/liter"
         },
"Viscosidade": {
        "Pascal-segundo (Pa·s)": "pascal*second",
        "Centipoise (cP)": "centipoise",
        "Libra-força-segundo por Pé Quadrado (lbf·s/ft²)": "pound_force*second/foot**2",
        "Dina-segundo por Centímetro Quadrado (dyn·s/cm²)": "dyne*second/centimeter**2",
        "Quilograma-força-segundo por Metro Quadrado (kgf·s/m²)": "kilogram_force*second/meter**2" },
"Resistência Elétrica": {
        "Ohm (Ω)": "ohm",
        "Quiloohm (kΩ)": "kilohm",
        "Megaohm (MΩ)": "megohm",
        "Gigaohm (GΩ)": "gigohm",
        "MiliOhm (mΩ)": "milliohm" },
"Capacitância": {
        "Farad (F)": "farad",
        "Microfarad (µF)": "microfarad",
        "Nanofarad (nF)": "nanofarad",
        "Picofarad (pF)": "picofarad",
        "Milifarad (mF)": "millifarad" },
"Indutância": {
        "Henry (H)": "henry",
        "Millihenry (mH)": "millihenry",
        "Microhenry (µH)": "microhenry",
        "Nanohenry (nH)": "nanohenry",
        "Picohenry (pH)": "picohenry" },
"Resistividade": {
        "Ohm-metro (Ω·m)": "ohm*meter",
        "Ohm-centímetro (Ω·cm)": "ohm*centimeter",
        "Ohm-pé (Ω·ft)": "ohm*foot",
        "Ohm-polegada (Ω·in)": "ohm*inch",
},
"Condutividade": {
        "Siemens por Metro (S/m)": "siemens/meter",
        "Millisiemens por Centímetro (mS/cm)": "millisiemens/centimeter",
        "Microsiemens por Centímetro (µS/cm)": "microsiemens/centimeter",
        "Siemens por Pé (S/ft)": "siemens/foot",
        "Siemens por Polegada (S/in)": "siemens/inch" },
"Intensidade Luminosa": {
        "Candela (cd)": "candela",
        "Milicandela (mcd)": "millicandela",
        "Microcandela (µcd)": "microcandela",
        "Nanocandela (ncd)": "nanocandela",
        "Picocandela (pcd)": "picocandela" },
"Velocidade Angular": {
        "Radianos por Segundo (rad/s)": "radian/second",
        "Graus por Segundo (°/s)": "degree/second",
        "Revoluções por Segundo (rev/s)": "revolution/second",
        "RPM (revoluções por minuto)": "revolution/minute",
        "Grados por Segundo (gon/s)": "gradian/second" },

}
# Escolha da Categoria
st.write( "Escolha uma Variável") 
categoria_selecionada = st.selectbox("Variável:", list(categorias.keys()))

# Interface de conversão
col1, col2 = st.columns(2)
opcoes_unidades = categorias[categoria_selecionada]

with col1:
    u_origem_label = st.selectbox("De:", list(opcoes_unidades.keys()), key="origem")
    valor_origem = st.number_input("Quantidade:", value=1.0, format="%.4f")

with col2:
    u_destino_label = st.selectbox("Para:", list(opcoes_unidades.keys()), key="destino")

# 3. A MÁGICA DO PINT
try:
    # Busca os nomes técnicos das unidades no nosso dicionário
    u_interna_origem = opcoes_unidades[u_origem_label]
    u_interna_destino = opcoes_unidades[u_destino_label]

    # Cria a quantidade com unidade (ex: 10 * metro)
    origem = valor_origem * ureg(u_interna_origem)
    
    # Converte para a unidade de destino
    destino = origem.to(u_interna_destino)

    # Exibe o resultado
    st.success(f"**Resultado:** {destino.magnitude:.6f} {u_destino_label}")
    
    # Dica extra: Exibe a unidade reduzida no SI para curiosidade
    st.info(f"Equivalente no SI: `{origem.to_base_units():.4f~P}`")

except Exception as e:
    st.error(f"Erro na conversão: {e}")

st.divider()

# print(dir(ureg))  -> Útil para explorar as unidades disponíveis no Pint