import hashlib
import hmac
import requests
import time
from pandas import json_normalize

<<<<<<< HEAD
# Define tus claves API aquí
API_KEY = ""
API_SECRET = ""
def obtener_datos_borrowing_contratos_futuros(symbol):
    endpoint = 'https://api.bybit.com/v5/spot-margin-trade/data'

    try:
        coin = symbol[:-4]
        params = {'symbol': coin}

        headers = {
            'api_key': API_KEY,
            'timestamp': str(int(time.time() * 1000)),
        }

        sign = hmac.new(API_SECRET.encode('utf-8'), "&".join([f"{k}={v}" for k, v in sorted(params.items())]).encode('utf-8'), hashlib.sha256).hexdigest()
        headers['sign'] = sign

        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            borrowing_data = data.get('result', {})
            return borrowing_data
        else:
            print(f"Error en la solicitud para {symbol}. Código de estado: {response.status_code}")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP {response.status_code}: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Error en la solicitud para {symbol}: {req_err}")
        return None
    except requests.exceptions.JSONDecodeError as json_err:
        print(f"Error al decodificar JSON para {symbol}: {json_err}")
        return None

def main():
    print("Análisis de Datos de Borrowing en Bybit para Contratos de Futuros")
    print("Esta aplicación muestra información sobre préstamos (borrowing) en Bybit para cada contrato de futuro.")

    contratos_futuros = ['SOLUSDT', 'BTCUSDT', 'ETHUSDT']

    for symbol in contratos_futuros:
        borrowing_data = obtener_datos_borrowing_contratos_futuros(symbol)

        if borrowing_data is not None:
            print(f"\nDatos de Borrowing para {symbol}:")
            print(f"Borrowing Data: {borrowing_data}")
        else:
            print(f"No se pudieron obtener los datos de borrowing para {symbol}.")

if __name__ == "__main__":
    main()
