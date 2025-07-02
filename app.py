import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
from io import BytesIO

# Configuración
st.set_page_config(layout="wide")
st.title("📊 Calculadora Hipotecaria Avanzada")

# Sidebar
with st.sidebar:
    st.header("⚙️ Parámetros")
    loan_amount = st.number_input("Monto del préstamo (€)", min_value=0.0, value=200000.0, step=10000.0)
    interest_rate = st.number_input("Tasa de interés anual (%)", min_value=0.0, value=3.5, step=0.1)
    loan_term = st.number_input("Plazo del préstamo (años)", min_value=1, value=30)
    extra_payment = st.number_input("Pago extra mensual (€)", min_value=0.0, value=0.0)

# Función con debug
def calculate_amortization(loan_amount, annual_rate, years, extra=0):
    monthly_rate = annual_rate / 100 / 12
    periods = years * 12
    payment = npf.pmt(monthly_rate, periods, -loan_amount)
    
    schedule = []
    balance = loan_amount
    
    for month in range(1, periods + 1):
        interest = balance * monthly_rate
        principal = (payment - interest) + extra
        balance -= principal
        
        if balance <= 0:
            actual_payment = principal + balance
            balance = 0
            schedule.append([month, actual_payment, interest, principal - (actual_payment - (payment - interest)), balance])
            break
            
        schedule.append([month, payment + extra, interest, principal, balance])
    
    df = pd.DataFrame(schedule, columns=["Mes", "Pago Total", "Intereses", "Capital", "Deuda Restante"])
    
    # Debug: Verificar datos generados
    st.sidebar.write("🔍 Primeras filas de datos:", df.head(3))
    st.sidebar.write("📊 Total de registros:", len(df))
    
    return df

if st.button("🔄 Calcular"):
    df = calculate_amortization(loan_amount, interest_rate, loan_term, extra_payment)
    
    # Debug: Verificar cálculo básico
    st.sidebar.write("💰 Cuota calculada:", df.iloc[0,1])
    st.sidebar.write("🧮 Meses calculados:", len(df))
    
    # Crear pestañas
    tab1, tab2 = st.tabs(["📈 Gráficos", "📋 Tabla"])
    
    with tab1:

        # --- RESUMEN COMPLETO EN 3 COLUMNAS ---
        st.divider()

        cols = st.columns(3)

        # Columna 1: CUOTA
        with cols[0]:
            total_payments = df['Pago Total'].sum()
            st.metric(
                label="📌 Cuota mensual",
                value=f"€{df.iloc[0,1]:.2f}",
                delta=f"Anual: €{df.iloc[0,1]*12:,.2f} | Global: €{total_payments:,.2f}",
                delta_color="off",
                help=f"""
                • **Mensual**: Pago fijo cada mes\n
                • **Anual**: {df.iloc[0,1]*12:,.2f}€ (12 cuotas)\n
                • **Global**: {total_payments:,.2f}€ (total {len(df)} pagos)\n
                • **Capital/Interés**: {df.iloc[0,3]:.2f}€ / {df.iloc[0,2]:.2f}€
                """
            )

        # Columna 2: INTERESES
        with cols[1]:
            total_interest = df['Intereses'].sum()
            avg_interest = total_interest / len(df)
            st.metric(
                label="💸 Intereses",
                value=f"€{avg_interest:.2f}",
                delta=f"Anual: €{avg_interest*12:,.2f} | Global: €{total_interest:,.2f}",
                delta_color="off",
                help=f"""
                • **Mensual (avg)**: {avg_interest:.2f}€\n
                • **Anual (avg)**: {avg_interest*12:,.2f}€\n
                • **Global**: {total_interest:,.2f}€ ({total_interest/loan_amount*100:.1f}% del préstamo)\n
                • **Primer mes**: {df.iloc[0,2]:.2f}€\n
                • **Último mes**: {df.iloc[-1,2]:.2f}€
                """
            )

        # Columna 3: CAPITAL
        with cols[2]:
            total_capital = df['Capital'].sum()
            avg_capital = total_capital / len(df)
            st.metric(
                label="🏠 Capital",
                value=f"€{avg_capital:.2f}",
                delta=f"Anual: €{avg_capital*12:,.2f} | Global: €{total_capital:,.2f}",
                delta_color="off",
                help=f"""
                • **Mensual (avg)**: {avg_capital:.2f}€\n
                • **Anual (avg)**: {avg_capital*12:,.2f}€\n
                • **Global**: {total_capital:,.2f}€ (100% del préstamo)\n
                • **Primer mes**: {df.iloc[0,3]:.2f}€\n
                • **Último mes**: {df.iloc[-1,3]:.2f}€
                """
            )


        view_option = st.radio("Visualización:", ["Por Meses"], horizontal=True)
        
        # Debug: Mostrar opción seleccionada
        st.sidebar.write("🎚️ Vista seleccionada:", view_option)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfico 1 - Evolución deuda
        deudaRestante = "Deuda Restante"
        if view_option == "Por Años":
            try:
                df['Año'] = (df['Mes'] - 1) // 12 + 1
                plot_df = df.groupby('Año').last().reset_index()
                
                # Debug: Verificar agrupación anual
                st.sidebar.write("📅 Datos anuales (último mes):", plot_df[['Año', deudaRestante]].head())
                
                ax1.plot(plot_df['Año'], plot_df[deudaRestante], color='#FF6B6B')
                ax1.set_xlabel("Años")
            except Exception as e:
                st.sidebar.error(f"❌ Error en gráfico anual: {str(e)}")
        else:
            ax1.plot(df['Mes'], df[deudaRestante], color='#FF6B6B')
            ax1.set_xlabel("Meses")
        
        ax1.set_title("Evolución de la Deuda")
        ax1.grid(True)
        
        # Gráfico 2 - Composición pagos
        if view_option == "Por Años":
            try:
                yearly_sum = df.groupby('Año')[['Capital', 'Intereses']].sum().reset_index()
                
                # Debug: Verificar suma anual
                st.sidebar.write("🧾 Suma anual:", yearly_sum.head())
                
                ax2.bar(yearly_sum['Año'], yearly_sum['Capital'], label="Capital", color='#4ECDC4')
                ax2.bar(yearly_sum['Año'], yearly_sum['Intereses'], bottom=yearly_sum['Capital'], 
                       label="Intereses", color='#FFE66D')
                ax2.set_xlabel("Años")
            except Exception as e:
                st.sidebar.error(f"❌ Error en composición anual: {str(e)}")
        else:
            ax2.bar(df['Mes'], df['Capital'], label="Capital", color='#4ECDC4')
            ax2.bar(df['Mes'], df['Intereses'], bottom=df['Capital'], 
                   label="Intereses", color='#FFE66D')
            ax2.set_xlabel("Meses")
        
        ax2.set_title("Composición de Pagos")
        ax2.legend()
        ax2.grid(True)
        
        st.pyplot(fig)

    with tab2:
        st.dataframe(df.style.format({
            "Pago Total": "€{:.2f}",
            "Intereses": "€{:.2f}",
            "Capital": "€{:.2f}",
            "Deuda Restante": "€{:.2f}"
        }), height=400)

# Mensaje final de debug
st.sidebar.markdown("---")

