import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página 
st.title("Calculadora de Préstamos Hipotecarios") 
 
# Entradas del usuario
loan_amount = st.number_input("Monto del préstamo (€)", min_value=0.0, value=100000.0)
interest_rate = st.number_input("Tasa de interés anual (%)", min_value=0.0, value=3.0)
loan_term = st.number_input("Plazo del préstamo (años)", min_value=1, value=30)

# Cálculo del pago mensual
def calculate_monthly_payment(loan_amount, interest_rate, loan_term):
    monthly_rate = interest_rate / 100 / 12
    num_payments = loan_term * 12
    if monthly_rate == 0:
        return loan_amount / num_payments
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    return monthly_payment

if st.button("Calcular"):
    monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, loan_term)
    st.subheader(f"Pago mensual: €{monthly_payment:.2f}")