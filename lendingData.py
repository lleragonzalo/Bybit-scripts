import pandas as pd
import requests
import time
import hashlib
import hmac
from urllib.parse import urlencode

def obtener_datos_lendbook(api_key, api_secret):
    endpoint = 'https://api.bybit.com/v5/lending/info'

    try:
        # Obtener el timestamp actual en milisegundos
        timestamp = str(int(time.time() * 1000))

        # Crear el mensaje para firmar
        query_params = urlencode({'api_timestamp': timestamp, 'apiKey': api_key})
        message = f'GET/realtime?{query_params}'

        # Crear la firma usando HMAC y SHA256
        signature = hmac.new(api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

        # Configurar los encabezados de autenticación
        headers = {
            'api-key': api_key,
            'timestamp': timestamp,
            'sign': signature
        }

        # Realizar la solicitud a la API
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            print("Datos de Lendings Recibidos:", data)

            lendbook_data = data.get('result', {})
            return lendbook_data
        else:
            print(f"Error en la solicitud. Código de estado: {response.status_code}")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Error en la solicitud: {req_err}")
        return None
    except requests.exceptions.JSONDecodeError as json_err:
        print(f"Error al decodificar JSON: {json_err}")
        return None

def procesar_datos_lendbook(lendbook_data):
    # Implementar el procesamiento de datos según la estructura real
    print("\nDatos de Lendbook:")
    print(lendbook_data)

    # Ejemplo: Crear un DataFrame si los datos son adecuados.
    if isinstance(lendbook_data, dict):
        df = pd.DataFrame.from_dict(lendbook_data)
        print("\nDatos del DataFrame:")
        print(df)

def main():
    print("Análisis de Datos de Lendings en Bybit")
    print("Esta aplicación muestra información sobre lendings en Bybit.")

    api_key = input("Ingrese su API Key: ")
    api_secret = input("Ingrese su API Secret: ")

    lendbook_data = obtener_datos_lendbook(api_key, api_secret)
    if lendbook_data is not None:
        procesar_datos_lendbook(lendbook_data)

if __name__ == "__main__":
    main()
