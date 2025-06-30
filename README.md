# Calculadora de Préstamos Hipotecarios
Una aplicación en Streamlit para calcular pagos de hipotecas.

## Instalación
1. Clona el repositorio: `git clone https://github.com/bbvedf/mortgage_calculator.git`
2. Crea un entorno virtual: `python -m venv .venv`
3. Activa el entorno: `.venv\Scripts\activate` (Windows)
4. Instala dependencias: `pip install -r requirements.txt`
Básicamente, 
    streamlit>=1.29.0
    pandas>=2.1.0
    numpy>=1.26.0
    numpy-financial>=1.0.0
    matplotlib>=3.8.0
    xlsxwriter>=3.1.0
5. Ejecuta la app: `streamlit run app.py`

## Uso
Ingresa el monto del préstamo, tasa de interés y plazo para calcular los pagos mensuales.
