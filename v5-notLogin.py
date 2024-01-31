import streamlit as st
import requests
import pandas as pd

BASE_URL = 'https://api.bybit.com/'

def obtener_activos_collateral():
    endpoint = 'v2/public/tickers'
    url = BASE_URL + endpoint

    response = requests.get(url)
    data = response.json()

    activos_collateral = data.get('result', [])

    return activos_collateral


def obtener_tasas_financiamiento():
    endpoint = '/v2/public/tickers'
    url = BASE_URL + endpoint

    response = requests.get(url)
    data = response.json()

    tasas_financiamiento = {}
    for ticker in data['result']:
        if isinstance(ticker, dict):
            tasas_financiamiento[ticker.get('symbol')] = ticker.get('funding_rate')

    return tasas_financiamiento

def crear_dataframe(activos_collateral, tasas_financiamiento):
    data = {'Asset/Collateral': [], 'Funding Rate Actual': []}

    for asset in activos_collateral:
        base_asset = asset.get('symbol')
        funding_rate = tasas_financiamiento.get(base_asset)

        data['Asset/Collateral'].append(base_asset)
        data['Funding Rate Actual'].append(funding_rate)

    df = pd.DataFrame(data)
    return df

def main():
    st.title("Análisis de Activos y Tasas de Financiamiento")
    st.write("Esta aplicación muestra información sobre activos y tasas de financiamiento de Bybit.")

    activos_collateral = obtener_activos_collateral()
    tasas_financiamiento = obtener_tasas_financiamiento()
    df = crear_dataframe(activos_collateral, tasas_financiamiento)

    st.write("### Datos del DataFrame:")
    st.write(df)

    # Guardar en un archivo Excel
    st.write("### Guardar en un archivo Excel...")
    df.to_excel('bybit_v5_no_login.xlsx', index=False)
    st.write("### Archivo Excel guardado con éxito.")

if __name__ == "__main__":
    main()




