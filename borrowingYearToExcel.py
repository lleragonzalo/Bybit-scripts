import hashlib
import hmac
import requests
import time
import pandas as pd

API_KEY = ""
API_SECRET = ""


def obtener_datos_borrowing(symbol):
    endpoint = 'https://api.bybit.com/v5/spot-margin-trade/data'

    try:
        coin = symbol[:-4] 
        timestamp = str(int(time.time() * 1000))
        query_params = f'timestamp={timestamp}&api_key={API_KEY}&coin={coin}'
        message = f'GET{endpoint}?{query_params}'
        signature = hmac.new(API_SECRET.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {
            'api-key': API_KEY,
            'timestamp': timestamp,
            'sign': signature,
        }

        response = requests.get(endpoint, headers=headers, params={'coin': coin})
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            return data.get('result', {})
        else:
            print(f"Error en la solicitud para {coin}. Código de estado: {response.status_code}")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP {response.status_code}: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Error en la solicitud para {coin}: {req_err}")
        return None
    except requests.exceptions.JSONDecodeError as json_err:
        print(f"Error al decodificar JSON para {coin}: {json_err}")
        return None


def main():
    print("Análisis de Datos de Borrowing en Bybit")
    print("Esta aplicación muestra información sobre préstamos (borrowing) en Bybit para varias monedas.")

    
    monedas = ['USDT', 'BTC', 'ETH', 'USDC', 'XRP', 'EOS', 'LTC', 'LINK', 'XLM', 'DAI', 'USDD', 'MANA', 'DOT', 'ADA',
               'DOGE', 'BNB', 'SHIB', 'BCH', 'SAND', 'AVAX', 'APE', 'MATIC', 'TRX', 'ZRX', 'CHZ', 'ATOM', 'STETH',
               'GMT', 'UNI', 'IMX', 'WAVES', 'YFI', 'FTM', 'AXS', 'AAVE', 'NEAR', 'ALGO', 'OP', 'GALA', 'DYDX', 'SUSHI',
               'FLOW', 'FIL', 'BAT', 'ETC', 'JASMY', 'CRV', 'COMP', 'SLP', 'ICP', 'GRT', 'EGLD', 'ENS', 'ZIL', 'THETA',
               'BICO', 'QNT', 'MNT', 'LUNC', 'APT', 'MASK', 'AR', 'SOL', 'TWT', 'CORE', 'BLUR', 'HFT', 'MAGIC', 'LDO',
               'ARB', 'SUI', 'PEPE', 'AGIX', 'RNDR', 'WLD', 'SEI', 'CYBER', 'ARKM', 'HBAR', 'INJ']

  
    dataframes = []

    for symbol in monedas:
        borrowing_data = obtener_datos_borrowing(symbol)

        if borrowing_data is not None:
            print(f"Cantidad de filas para {symbol}: {len(borrowing_data['vipCoinList'][0]['list'])}")

            df = pd.json_normalize(borrowing_data['vipCoinList'][0]['list'])

            # Agrega una nueva columna con la tasa de préstamo anual
            df['annualBorrowRate'] = df['hourlyBorrowRate'] * 24 * 365

            dataframes.append(df)
        else:
            print(f"No se pudieron obtener los datos de borrowing para {symbol}.")




    result_df = pd.concat(dataframes, keys=monedas)


    result_df['hourlyBorrowRate'] = result_df['hourlyBorrowRate'].fillna(0)


    result_df['hourlyBorrowRate'] = pd.to_numeric(result_df['hourlyBorrowRate'], errors='coerce')


    result_df['annualBorrowRate'] = result_df['hourlyBorrowRate'] * 24 * 365


    result_df['annualBorrowRatePercentage'] = result_df['annualBorrowRate'] * 100


    result_df['annualBorrowRate'] = result_df['annualBorrowRate'].apply(lambda x: '{:.16f}'.format(x))
    result_df['annualBorrowRatePercentage'] = result_df['annualBorrowRatePercentage'].apply(
        lambda x: '{:.16f}'.format(x))

    # Guarda el DataFrame en un archivo Excel
    result_df.to_excel('datos_borrowing_bybit_anual.xlsx', index=False)
    print("Datos guardados en 'datos_borrowing_bybit_anual.xlsx'.")


if __name__ == "__main__":
    main()















