from google.auth.transport.requests import Request
from google.oauth2 import service_account
import gspread
import pandas as pd
import requests

API_KEY = 'JT1y5FvxnyjqfVvVHs'
API_SECRET = 'vw14SB2Qw6vhMLs7Da9F4QsP2V6jtK4mcTA6'

BASE_URL = 'https://oracle.yolodc.com/relay?url=https://api.bybit.com/v5/market/tickers&category=linear'

def obtener_activos_collateral():
    endpoint = '/v2/public/symbols'
    url = BASE_URL + endpoint

    response = requests.get(url)
    data = response.json()

    activos_collateral = data.get('result', {}).get('list', [])

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
        base_asset = asset.get('base_asset')
        funding_rate = tasas_financiamiento.get(base_asset)

        data['Asset/Collateral'].append(base_asset)
        data['Funding Rate Actual'].append(funding_rate)

    df = pd.DataFrame(data)
    return df

def enviar_a_google_sheets(df):
    credentials_path = 'ruta_al_archivo_json.json'

    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        if credentials.expired:
            credentials.refresh(Request())

        gc = gspread.authorize(credentials)

        spreadsheet_id = '1QzXKS9Wk3Hd_vT5haAY2z2yo01ouQ50S8Ilr5IVaOLc'

        worksheet = gc.open_by_key(spreadsheet_id).sheet1

        print("Antes de enviar a Google Sheets")
        print(df)

        if df.empty:
            print("El DataFrame está vacío. No se enviarán datos a Google Sheets.")
        else:
            print("Después de enviar a Google Sheets")
            worksheet.clear()
            gc.import_pandas(df, worksheet.id)

            print("Después de enviar a Google Sheets")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    activos_collateral = obtener_activos_collateral()
    tasas_financiamiento = obtener_tasas_financiamiento()
    df = crear_dataframe(activos_collateral, tasas_financiamiento)

    enviar_a_google_sheets(df)

