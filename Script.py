import requests
import pandas as pd

API_KEY = 'JT1y5FvxnyjqfVvVHs'
API_SECRET = 'vw14SB2Qw6vhMLs7Da9F4QsP2V6jtK4mcTA6'

BASE_URL = 'https://oracle.yolodc.com/relay?url=https://api.bybit.com/v5/market/tickers&category=linear'  # Reemplaza con tu URL específica de la API de Bybit

def obtener_activos_collateral():
    endpoint = '/v2/public/symbols'
    url = BASE_URL + endpoint

    response = requests.get(url)
    data = response.json()

    print(data)

    activos_collateral = data.get('result', {}).get('list', [])

    return activos_collateral

def obtener_tasas_financiamiento():
    endpoint = '/v2/public/tickers'
    url = BASE_URL + endpoint

    response = requests.get(url)
    data = response.json()

    print(data['result'])
    tasas_financiamiento = {}
    for ticker in data['result']:
        if isinstance(ticker, dict):
            tasas_financiamiento[ticker.get('symbol')] = ticker.get('funding_rate')

    return tasas_financiamiento

def crear_dataframe(activos_collateral, tasas_financiamiento):
    data = {'Asset/Collateral': [], 'Funding Rate Actual': []}

    for asset in activos_collateral:
        base_asset = asset.get('base_asset')
        funding_rate = tasas_financiamiento.get(base_asset)

        data['Asset/Collateral'].append(base_asset)
        data['Funding Rate Actual'].append(funding_rate)

    df = pd.DataFrame(data)
    return df


#Función principal
def main():
    activos_collateral = obtener_activos_collateral()
    tasas_financiamiento = obtener_tasas_financiamiento()
    df = crear_dataframe(activos_collateral, tasas_financiamiento)

    print(df)

    # Guardar en un archivo Excel
    df.to_excel('bybit_datos.xlsx', index=False)

if __name__ == "__main__":
    main()



