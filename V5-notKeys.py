import requests
import pandas as pd


def obtener_activos_collateral():
    endpoint = 'https://api.bybit.com/v5/public/tickers'
    url = endpoint

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("Respuesta de la API:", data)

        activos_collateral = data.get('result', [])
        return activos_collateral
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return None
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        return None


def obtener_tasas_financiamiento():
    endpoint = 'https://api.bybit.com/v5/public/tickers'
    url = endpoint

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        tasas_financiamiento = {}
        for ticker in data.get('result', []):
            if isinstance(ticker, dict):
                tasas_financiamiento[ticker.get('symbol')] = ticker.get('funding_rate')

        return tasas_financiamiento
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return {}
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        return {}


def crear_dataframe(activos_collateral, tasas_financiamiento):
    data = {'Asset/Collateral': [], 'Funding Rate Actual': []}

    for asset in activos_collateral:
        if isinstance(asset, dict):
            base_asset = asset.get('symbol')
            funding_rate = tasas_financiamiento.get(base_asset)

            data['Asset/Collateral'].append(base_asset)
            data['Funding Rate Actual'].append(funding_rate)

    df = pd.DataFrame(data)
    return df


def guardar_en_excel(df, nombre_archivo='bybit_v5_no_login.xlsx'):
    df.to_excel(nombre_archivo, index=False)
    print(f"Archivo Excel '{nombre_archivo}' guardado con éxito.")


def main():
    print("Análisis de Activos y Tasas de Financiamiento")
    print("Esta aplicación muestra información sobre activos y tasas de financiamiento de Bybit.")

    activos_collateral = obtener_activos_collateral()
    if activos_collateral is None:
        return

    tasas_financiamiento = obtener_tasas_financiamiento()
    df = crear_dataframe(activos_collateral, tasas_financiamiento)

    print("\nDatos del DataFrame:")
    print(df)

    # Guardar en un archivo Excel
    print("\nGuardar en un archivo Excel...")
    guardar_en_excel(df)


if __name__ == "__main__":
    main()
