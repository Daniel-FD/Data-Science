"""
Simulador Fiscal: Autónomo vs SL
================================
Aplicación para comparar estrategias fiscales y calcular
la renta mensual neta después de impuestos de rescate.

Autor: Análisis para Daniel Fiuza Dosil
Fecha: Enero 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from typing import Tuple, List

# ============================================================
# CONFIGURACIÓN DE IMPUESTOS (España 2024-2025)
# ============================================================

# Tramos IRPF del ahorro (para plusvalías y dividendos)
TRAMOS_AHORRO = [
    (6_000, 0.19),
    (50_000, 0.21),
    (200_000, 0.23),
    (300_000, 0.27),
    (float('inf'), 0.28)
]

# Tramos IRPF general (aproximados, incluye estatal + autonómico Galicia)
TRAMOS_IRPF_GENERAL = [
    (12_450, 0.19),
    (20_200, 0.24),
    (35_200, 0.30),
    (60_000, 0.37),
    (300_000, 0.45),
    (float('inf'), 0.47)
]

# Impuesto de Sociedades
IS_TIPO_REDUCIDO = 0.15  # Primeros 2 años empresas nuevas
IS_TIPO_PYME_TRAMO1 = 0.23  # Primeros 50.000€
IS_TIPO_PYME_TRAMO2 = 0.25  # Resto


# ============================================================
# FUNCIONES DE CÁLCULO DE IMPUESTOS
# ============================================================

def calcular_irpf_ahorro(base: float) -> float:
    """Calcula el IRPF del ahorro (plusvalías/dividendos)"""
    if base <= 0:
        return 0
    
    impuesto = 0
    base_restante = base
    limite_anterior = 0
    
    for limite, tipo in TRAMOS_AHORRO:
        tramo = min(base_restante, limite - limite_anterior)
        if tramo <= 0:
            break
        impuesto += tramo * tipo
        base_restante -= tramo
        limite_anterior = limite
    
    return impuesto


def calcular_irpf_general(base: float) -> float:
    """Calcula el IRPF general (rendimientos del trabajo)"""
    if base <= 0:
        return 0
    
    impuesto = 0
    base_restante = base
    limite_anterior = 0
    
    for limite, tipo in TRAMOS_IRPF_GENERAL:
        tramo = min(base_restante, limite - limite_anterior)
        if tramo <= 0:
            break
        impuesto += tramo * tipo
        base_restante -= tramo
        limite_anterior = limite
    
    return impuesto


def calcular_is(beneficio: float, año_empresa: int) -> float:
    """Calcula el Impuesto de Sociedades"""
    if beneficio <= 0:
        return 0
    
    if año_empresa <= 2:
        return beneficio * IS_TIPO_REDUCIDO
    else:
        if beneficio <= 50_000:
            return beneficio * IS_TIPO_PYME_TRAMO1
        else:
            return 50_000 * IS_TIPO_PYME_TRAMO1 + (beneficio - 50_000) * IS_TIPO_PYME_TRAMO2


def calcular_cuota_autonomos(rendimiento_anual: float) -> float:
    """Calcula la cuota de autónomos según rendimiento (sistema 2025)"""
    rendimiento_mensual = rendimiento_anual / 12
    
    # Tabla simplificada de cuotas por tramos de rendimiento
    if rendimiento_mensual <= 670:
        return 230 * 12
    elif rendimiento_mensual <= 900:
        return 260 * 12
    elif rendimiento_mensual <= 1_166:
        return 290 * 12
    elif rendimiento_mensual <= 1_300:
        return 320 * 12
    elif rendimiento_mensual <= 1_700:
        return 350 * 12
    elif rendimiento_mensual <= 1_850:
        return 380 * 12
    elif rendimiento_mensual <= 2_030:
        return 400 * 12
    elif rendimiento_mensual <= 2_330:
        return 420 * 12
    elif rendimiento_mensual <= 2_760:
        return 450 * 12
    elif rendimiento_mensual <= 3_190:
        return 480 * 12
    elif rendimiento_mensual <= 3_620:
        return 510 * 12
    elif rendimiento_mensual <= 4_050:
        return 540 * 12
    elif rendimiento_mensual <= 6_000:
        return 590 * 12
    else:
        return 590 * 12  # Máximo


# ============================================================
# SIMULADORES DE ESCENARIOS
# ============================================================

@dataclass
class ResultadoAnual:
    año: int
    aportacion: float
    rentabilidad: float
    capital_acumulado: float
    impuestos_pagados_año: float


@dataclass
class ResultadoFinal:
    capital_bruto: float
    plusvalias: float
    impuestos_rescate: float
    capital_neto: float
    renta_anual_bruta: float
    renta_anual_neta: float
    renta_mensual_neta: float
    historial: List[ResultadoAnual]


def simular_autonomo(
    facturacion: float,
    gastos_deducibles: float,
    gastos_personales: float,
    años: int,
    rentabilidad: float,
    capital_inicial: float = 0,
    aportacion_plan_pensiones: float = 5750
) -> ResultadoFinal:
    """Simula el escenario de autónomo"""
    
    historial = []
    capital = capital_inicial
    total_aportado = capital_inicial
    total_impuestos = 0
    
    for año in range(1, años + 1):
        # Cálculo anual
        rendimiento_neto = facturacion - gastos_deducibles
        cuota_autonomos = calcular_cuota_autonomos(rendimiento_neto)
        base_irpf = rendimiento_neto - cuota_autonomos - aportacion_plan_pensiones
        irpf = calcular_irpf_general(base_irpf)
        
        neto_disponible = rendimiento_neto - cuota_autonomos - irpf
        aportacion = max(0, neto_disponible - gastos_personales - aportacion_plan_pensiones)
        
        # Rentabilidad sobre capital existente
        rent = capital * rentabilidad
        capital = capital + aportacion + rent
        total_aportado += aportacion
        total_impuestos += irpf + cuota_autonomos
        
        historial.append(ResultadoAnual(
            año=año,
            aportacion=aportacion,
            rentabilidad=rent,
            capital_acumulado=capital,
            impuestos_pagados_año=irpf + cuota_autonomos
        ))
    
    # Cálculo de rescate
    plusvalias = capital - total_aportado
    impuestos_rescate = calcular_irpf_ahorro(plusvalias)
    capital_neto = capital - impuestos_rescate
    
    # Renta con regla del 4%
    renta_anual_bruta = capital * 0.04
    # La renta anual también genera plusvalías, asumimos ~50% es plusvalía
    impuesto_renta_anual = calcular_irpf_ahorro(renta_anual_bruta * 0.5)
    renta_anual_neta = renta_anual_bruta - impuesto_renta_anual
    
    return ResultadoFinal(
        capital_bruto=capital,
        plusvalias=plusvalias,
        impuestos_rescate=impuestos_rescate,
        capital_neto=capital_neto,
        renta_anual_bruta=renta_anual_bruta,
        renta_anual_neta=renta_anual_neta,
        renta_mensual_neta=renta_anual_neta / 12,
        historial=historial
    )


def simular_sl_retencion(
    facturacion: float,
    gastos_deducibles: float,
    gastos_gestoria_sl: float,
    salario_administrador: float,
    gastos_personales: float,
    años: int,
    rentabilidad: float,
    capital_inicial: float = 0
) -> ResultadoFinal:
    """Simula el escenario de SL con retención máxima"""
    
    historial = []
    capital_sl = 0
    capital_personal = capital_inicial
    total_aportado_sl = 0
    total_impuestos = 0
    
    for año in range(1, años + 1):
        # Dentro de la SL
        ss_empresa = salario_administrador * 0.30
        beneficio_antes_is = facturacion - gastos_deducibles - salario_administrador - ss_empresa - gastos_gestoria_sl
        is_pagado = calcular_is(beneficio_antes_is, año)
        beneficio_neto = beneficio_antes_is - is_pagado
        
        # A nivel personal (salario)
        ss_trabajador = salario_administrador * 0.065
        irpf_salario = calcular_irpf_general(salario_administrador - ss_trabajador)
        salario_neto = salario_administrador - ss_trabajador - irpf_salario
        
        # La SL invierte el beneficio
        rent_sl = capital_sl * rentabilidad
        capital_sl = capital_sl + beneficio_neto + rent_sl
        total_aportado_sl += beneficio_neto
        
        # El capital personal inicial también crece
        rent_personal = capital_personal * rentabilidad
        capital_personal = capital_personal + rent_personal
        
        total_impuestos += is_pagado + irpf_salario
        
        historial.append(ResultadoAnual(
            año=año,
            aportacion=beneficio_neto,
            rentabilidad=rent_sl,
            capital_acumulado=capital_sl + capital_personal,
            impuestos_pagados_año=is_pagado + irpf_salario
        ))
    
    # Capital total
    capital_total = capital_sl + capital_personal
    
    # Rescate: dividendos de la SL
    # Las plusvalías dentro de la SL se consideran beneficios retenidos
    # Al sacar como dividendos, tributan al tipo del ahorro
    plusvalias_sl = capital_sl - total_aportado_sl
    
    # Impuesto al rescatar toda la SL como dividendos
    # Primero la SL paga IS sobre plusvalías no realizadas (ya pagado anualmente en realidad para fondos)
    # Luego los dividendos tributan en IRPF ahorro
    impuestos_rescate_sl = calcular_irpf_ahorro(capital_sl)
    
    # Plus el capital personal (plusvalías)
    plusvalias_personal = capital_personal - capital_inicial
    impuestos_rescate_personal = calcular_irpf_ahorro(plusvalias_personal)
    
    impuestos_rescate_total = impuestos_rescate_sl + impuestos_rescate_personal
    capital_neto = capital_total - impuestos_rescate_total
    
    # Renta con regla del 4%
    renta_anual_bruta = capital_total * 0.04
    # Los dividendos tributan íntegramente
    impuesto_renta_anual = calcular_irpf_ahorro(renta_anual_bruta)
    renta_anual_neta = renta_anual_bruta - impuesto_renta_anual
    
    return ResultadoFinal(
        capital_bruto=capital_total,
        plusvalias=plusvalias_sl + plusvalias_personal,
        impuestos_rescate=impuestos_rescate_total,
        capital_neto=capital_neto,
        renta_anual_bruta=renta_anual_bruta,
        renta_anual_neta=renta_anual_neta,
        renta_mensual_neta=renta_anual_neta / 12,
        historial=historial
    )


def simular_sl_dividendos(
    facturacion: float,
    gastos_deducibles: float,
    gastos_gestoria_sl: float,
    salario_administrador: float,
    gastos_personales: float,
    años: int,
    rentabilidad: float,
    capital_inicial: float = 0
) -> ResultadoFinal:
    """Simula el escenario de SL sacando dividendos cada año"""
    
    historial = []
    capital = capital_inicial
    total_aportado = capital_inicial
    total_impuestos = 0
    
    for año in range(1, años + 1):
        # Dentro de la SL
        ss_empresa = salario_administrador * 0.30
        beneficio_antes_is = facturacion - gastos_deducibles - salario_administrador - ss_empresa - gastos_gestoria_sl
        is_pagado = calcular_is(beneficio_antes_is, año)
        beneficio_neto = beneficio_antes_is - is_pagado  # Disponible para dividendos
        
        # A nivel personal
        ss_trabajador = salario_administrador * 0.065
        irpf_salario = calcular_irpf_general(salario_administrador - ss_trabajador)
        salario_neto = salario_administrador - ss_trabajador - irpf_salario
        
        # Dividendos (sacamos todo el beneficio)
        irpf_dividendos = calcular_irpf_ahorro(beneficio_neto)
        dividendos_netos = beneficio_neto - irpf_dividendos
        
        # Capacidad de inversión personal
        ingresos_netos_totales = salario_neto + dividendos_netos
        aportacion = max(0, ingresos_netos_totales - gastos_personales)
        
        # Rentabilidad
        rent = capital * rentabilidad
        capital = capital + aportacion + rent
        total_aportado += aportacion
        total_impuestos += is_pagado + irpf_salario + irpf_dividendos
        
        historial.append(ResultadoAnual(
            año=año,
            aportacion=aportacion,
            rentabilidad=rent,
            capital_acumulado=capital,
            impuestos_pagados_año=is_pagado + irpf_salario + irpf_dividendos
        ))
    
    # Rescate (plusvalías personales)
    plusvalias = capital - total_aportado
    impuestos_rescate = calcular_irpf_ahorro(plusvalias)
    capital_neto = capital - impuestos_rescate
    
    # Renta
    renta_anual_bruta = capital * 0.04
    impuesto_renta_anual = calcular_irpf_ahorro(renta_anual_bruta * 0.5)
    renta_anual_neta = renta_anual_bruta - impuesto_renta_anual
    
    return ResultadoFinal(
        capital_bruto=capital,
        plusvalias=plusvalias,
        impuestos_rescate=impuestos_rescate,
        capital_neto=capital_neto,
        renta_anual_bruta=renta_anual_bruta,
        renta_anual_neta=renta_anual_neta,
        renta_mensual_neta=renta_anual_neta / 12,
        historial=historial
    )


# ============================================================
# INTERFAZ STREAMLIT
# ============================================================

def main():
    st.set_page_config(
        page_title="Simulador Fiscal: Autónomo vs SL",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 Simulador Fiscal: Autónomo vs SL")
    st.markdown("*Calcula tu renta mensual NETA después de impuestos de rescate*")
    
    # Sidebar con parámetros
    st.sidebar.header("⚙️ Parámetros de Simulación")
    
    st.sidebar.subheader("📊 Ingresos y Gastos")
    facturacion = st.sidebar.number_input(
        "Facturación anual (€)",
        min_value=0,
        max_value=500_000,
        value=105_000,
        step=5_000
    )
    
    gastos_deducibles = st.sidebar.number_input(
        "Gastos deducibles actividad (€/año)",
        min_value=0,
        max_value=50_000,
        value=2_000,
        step=500
    )
    
    gastos_personales = st.sidebar.number_input(
        "Gastos personales (€/año)",
        min_value=0,
        max_value=100_000,
        value=12_000,
        step=1_000
    )
    
    st.sidebar.subheader("🏢 Parámetros SL")
    salario_administrador = st.sidebar.number_input(
        "Salario administrador SL (€/año)",
        min_value=0,
        max_value=100_000,
        value=18_000,
        step=1_000
    )
    
    gastos_gestoria = st.sidebar.number_input(
        "Gastos gestoría SL (€/año)",
        min_value=0,
        max_value=10_000,
        value=3_000,
        step=500
    )
    
    st.sidebar.subheader("📈 Inversión")
    capital_inicial = st.sidebar.number_input(
        "Capital inicial (€)",
        min_value=0,
        max_value=1_000_000,
        value=0,
        step=10_000
    )
    
    rentabilidad = st.sidebar.slider(
        "Rentabilidad anual esperada (%)",
        min_value=0.0,
        max_value=15.0,
        value=6.0,
        step=0.5
    ) / 100
    
    st.sidebar.subheader("⏱️ Horizonte")
    años = st.sidebar.slider(
        "Años de simulación",
        min_value=1,
        max_value=30,
        value=10
    )
    
    # Ejecutar simulaciones
    resultado_autonomo = simular_autonomo(
        facturacion=facturacion,
        gastos_deducibles=gastos_deducibles,
        gastos_personales=gastos_personales,
        años=años,
        rentabilidad=rentabilidad,
        capital_inicial=capital_inicial
    )
    
    resultado_sl_retencion = simular_sl_retencion(
        facturacion=facturacion,
        gastos_deducibles=gastos_deducibles,
        gastos_gestoria_sl=gastos_gestoria,
        salario_administrador=salario_administrador,
        gastos_personales=gastos_personales,
        años=años,
        rentabilidad=rentabilidad,
        capital_inicial=capital_inicial
    )
    
    resultado_sl_dividendos = simular_sl_dividendos(
        facturacion=facturacion,
        gastos_deducibles=gastos_deducibles,
        gastos_gestoria_sl=gastos_gestoria,
        salario_administrador=salario_administrador,
        gastos_personales=gastos_personales,
        años=años,
        rentabilidad=rentabilidad,
        capital_inicial=capital_inicial
    )
    
    # Mostrar resultados
    st.header(f"📊 Resultados a {años} años")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👤 Autónomo")
        st.metric("Capital Bruto", f"{resultado_autonomo.capital_bruto:,.0f}€")
        st.metric("Impuestos Rescate", f"-{resultado_autonomo.impuestos_rescate:,.0f}€")
        st.metric("Capital Neto", f"{resultado_autonomo.capital_neto:,.0f}€")
        st.divider()
        st.metric("🎯 Renta Mensual NETA", f"{resultado_autonomo.renta_mensual_neta:,.0f}€/mes")
    
    with col2:
        st.subheader("🏢 SL + Retención")
        diferencia_capital = resultado_sl_retencion.capital_neto - resultado_autonomo.capital_neto
        st.metric("Capital Bruto", f"{resultado_sl_retencion.capital_bruto:,.0f}€")
        st.metric("Impuestos Rescate", f"-{resultado_sl_retencion.impuestos_rescate:,.0f}€")
        st.metric("Capital Neto", f"{resultado_sl_retencion.capital_neto:,.0f}€", 
                  delta=f"+{diferencia_capital:,.0f}€ vs Autónomo")
        st.divider()
        diferencia_renta = resultado_sl_retencion.renta_mensual_neta - resultado_autonomo.renta_mensual_neta
        st.metric("🎯 Renta Mensual NETA", f"{resultado_sl_retencion.renta_mensual_neta:,.0f}€/mes",
                  delta=f"+{diferencia_renta:,.0f}€/mes")
    
    with col3:
        st.subheader("🏢 SL + Dividendos")
        diferencia_capital = resultado_sl_dividendos.capital_neto - resultado_autonomo.capital_neto
        st.metric("Capital Bruto", f"{resultado_sl_dividendos.capital_bruto:,.0f}€")
        st.metric("Impuestos Rescate", f"-{resultado_sl_dividendos.impuestos_rescate:,.0f}€")
        st.metric("Capital Neto", f"{resultado_sl_dividendos.capital_neto:,.0f}€",
                  delta=f"+{diferencia_capital:,.0f}€ vs Autónomo")
        st.divider()
        diferencia_renta = resultado_sl_dividendos.renta_mensual_neta - resultado_autonomo.renta_mensual_neta
        st.metric("🎯 Renta Mensual NETA", f"{resultado_sl_dividendos.renta_mensual_neta:,.0f}€/mes",
                  delta=f"+{diferencia_renta:,.0f}€/mes")
    
    # Tabla comparativa
    st.header("📋 Tabla Comparativa Completa")
    
    df_comparativa = pd.DataFrame({
        "Métrica": [
            "Capital Bruto Acumulado",
            "Plusvalías Generadas",
            "Impuestos al Rescate",
            "Capital Neto Final",
            "Renta Anual Bruta (4%)",
            "Renta Anual Neta",
            "🎯 RENTA MENSUAL NETA"
        ],
        "Autónomo": [
            f"{resultado_autonomo.capital_bruto:,.0f}€",
            f"{resultado_autonomo.plusvalias:,.0f}€",
            f"{resultado_autonomo.impuestos_rescate:,.0f}€",
            f"{resultado_autonomo.capital_neto:,.0f}€",
            f"{resultado_autonomo.renta_anual_bruta:,.0f}€",
            f"{resultado_autonomo.renta_anual_neta:,.0f}€",
            f"{resultado_autonomo.renta_mensual_neta:,.0f}€/mes"
        ],
        "SL + Retención": [
            f"{resultado_sl_retencion.capital_bruto:,.0f}€",
            f"{resultado_sl_retencion.plusvalias:,.0f}€",
            f"{resultado_sl_retencion.impuestos_rescate:,.0f}€",
            f"{resultado_sl_retencion.capital_neto:,.0f}€",
            f"{resultado_sl_retencion.renta_anual_bruta:,.0f}€",
            f"{resultado_sl_retencion.renta_anual_neta:,.0f}€",
            f"{resultado_sl_retencion.renta_mensual_neta:,.0f}€/mes"
        ],
        "SL + Dividendos": [
            f"{resultado_sl_dividendos.capital_bruto:,.0f}€",
            f"{resultado_sl_dividendos.plusvalias:,.0f}€",
            f"{resultado_sl_dividendos.impuestos_rescate:,.0f}€",
            f"{resultado_sl_dividendos.capital_neto:,.0f}€",
            f"{resultado_sl_dividendos.renta_anual_bruta:,.0f}€",
            f"{resultado_sl_dividendos.renta_anual_neta:,.0f}€",
            f"{resultado_sl_dividendos.renta_mensual_neta:,.0f}€/mes"
        ]
    })
    
    st.dataframe(df_comparativa, use_container_width=True, hide_index=True)
    
    # Gráfico de evolución del capital
    st.header("📈 Evolución del Capital Acumulado")
    
    df_evolucion = pd.DataFrame({
        "Año": [r.año for r in resultado_autonomo.historial],
        "Autónomo": [r.capital_acumulado for r in resultado_autonomo.historial],
        "SL + Retención": [r.capital_acumulado for r in resultado_sl_retencion.historial],
        "SL + Dividendos": [r.capital_acumulado for r in resultado_sl_dividendos.historial]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_evolucion["Año"], y=df_evolucion["Autónomo"], 
                             name="Autónomo", line=dict(color="blue", width=3)))
    fig.add_trace(go.Scatter(x=df_evolucion["Año"], y=df_evolucion["SL + Retención"], 
                             name="SL + Retención", line=dict(color="green", width=3)))
    fig.add_trace(go.Scatter(x=df_evolucion["Año"], y=df_evolucion["SL + Dividendos"], 
                             name="SL + Dividendos", line=dict(color="orange", width=3)))
    
    fig.update_layout(
        xaxis_title="Años",
        yaxis_title="Capital Acumulado (€)",
        hovermode="x unified",
        yaxis_tickformat=",",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de renta mensual neta por año
    st.header("💵 Renta Mensual NETA por Año de Rescate")
    
    rentas = []
    for año in range(1, años + 1):
        r_auto = simular_autonomo(facturacion, gastos_deducibles, gastos_personales, año, rentabilidad, capital_inicial)
        r_sl_ret = simular_sl_retencion(facturacion, gastos_deducibles, gastos_gestoria, salario_administrador, gastos_personales, año, rentabilidad, capital_inicial)
        r_sl_div = simular_sl_dividendos(facturacion, gastos_deducibles, gastos_gestoria, salario_administrador, gastos_personales, año, rentabilidad, capital_inicial)
        
        rentas.append({
            "Año": año,
            "Autónomo": r_auto.renta_mensual_neta,
            "SL + Retención": r_sl_ret.renta_mensual_neta,
            "SL + Dividendos": r_sl_div.renta_mensual_neta
        })
    
    df_rentas = pd.DataFrame(rentas)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df_rentas["Año"], y=df_rentas["Autónomo"], 
                          name="Autónomo", marker_color="blue"))
    fig2.add_trace(go.Bar(x=df_rentas["Año"], y=df_rentas["SL + Retención"], 
                          name="SL + Retención", marker_color="green"))
    fig2.add_trace(go.Bar(x=df_rentas["Año"], y=df_rentas["SL + Dividendos"], 
                          name="SL + Dividendos", marker_color="orange"))
    
    # Línea de objetivo
    fig2.add_hline(y=2000, line_dash="dash", line_color="red", 
                   annotation_text="Objetivo: 2.000€/mes")
    
    fig2.update_layout(
        xaxis_title="Año de Rescate",
        yaxis_title="Renta Mensual Neta (€/mes)",
        barmode="group",
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Tabla detallada año a año
    st.header("📑 Detalle Año a Año")
    
    tab1, tab2, tab3 = st.tabs(["Autónomo", "SL + Retención", "SL + Dividendos"])
    
    with tab1:
        df_auto = pd.DataFrame([{
            "Año": r.año,
            "Aportación": f"{r.aportacion:,.0f}€",
            "Rentabilidad": f"{r.rentabilidad:,.0f}€",
            "Capital Acumulado": f"{r.capital_acumulado:,.0f}€",
            "Impuestos Año": f"{r.impuestos_pagados_año:,.0f}€"
        } for r in resultado_autonomo.historial])
        st.dataframe(df_auto, use_container_width=True, hide_index=True)
    
    with tab2:
        df_sl_ret = pd.DataFrame([{
            "Año": r.año,
            "Aportación SL": f"{r.aportacion:,.0f}€",
            "Rentabilidad": f"{r.rentabilidad:,.0f}€",
            "Capital Acumulado": f"{r.capital_acumulado:,.0f}€",
            "Impuestos Año": f"{r.impuestos_pagados_año:,.0f}€"
        } for r in resultado_sl_retencion.historial])
        st.dataframe(df_sl_ret, use_container_width=True, hide_index=True)
    
    with tab3:
        df_sl_div = pd.DataFrame([{
            "Año": r.año,
            "Aportación": f"{r.aportacion:,.0f}€",
            "Rentabilidad": f"{r.rentabilidad:,.0f}€",
            "Capital Acumulado": f"{r.capital_acumulado:,.0f}€",
            "Impuestos Año": f"{r.impuestos_pagados_año:,.0f}€"
        } for r in resultado_sl_dividendos.historial])
        st.dataframe(df_sl_div, use_container_width=True, hide_index=True)
    
    # Conclusiones
    st.header("📌 Conclusiones")
    
    mejor_opcion = max([
        ("Autónomo", resultado_autonomo.renta_mensual_neta),
        ("SL + Retención", resultado_sl_retencion.renta_mensual_neta),
        ("SL + Dividendos", resultado_sl_dividendos.renta_mensual_neta)
    ], key=lambda x: x[1])
    
    diferencia_vs_autonomo = mejor_opcion[1] - resultado_autonomo.renta_mensual_neta
    
    st.success(f"""
    **🏆 Mejor opción para tu perfil: {mejor_opcion[0]}**
    
    - Renta mensual NETA: **{mejor_opcion[1]:,.0f}€/mes**
    - Diferencia vs Autónomo: **+{diferencia_vs_autonomo:,.0f}€/mes** ({diferencia_vs_autonomo*12:,.0f}€/año)
    """)
    
    if resultado_sl_retencion.renta_mensual_neta >= 2000:
        st.info("✅ Con SL + Retención alcanzas tu objetivo de 2.000€/mes NETOS")
    else:
        # Calcular cuántos años necesitas
        for año_objetivo in range(1, 31):
            r = simular_sl_retencion(facturacion, gastos_deducibles, gastos_gestoria, 
                                     salario_administrador, gastos_personales, año_objetivo, 
                                     rentabilidad, capital_inicial)
            if r.renta_mensual_neta >= 2000:
                st.info(f"⏱️ Necesitas **{año_objetivo} años** para alcanzar 2.000€/mes NETOS con SL + Retención")
                break
    
    # Disclaimer
    st.divider()
    st.caption("""
    ⚠️ **Disclaimer:** Esta simulación es orientativa y utiliza cálculos aproximados. 
    Los impuestos reales pueden variar según tu situación personal, deducciones aplicables, 
    y cambios legislativos. Consulta siempre con un asesor fiscal profesional antes de tomar decisiones.
    """)


if __name__ == "__main__":
    main()