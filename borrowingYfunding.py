import logging
import requests
import json
import pandas as pd

# Configurar el sistema de registro
logging.basicConfig(filename='registro.log', level=logging.DEBUG)

def obtener_funding_rates():
    try:
        # URL de la API para obtener datos de funding
        funding_api_url = 'https://oracle.yolodc.com/relay?url=https://api.bybit.com/v5/market/tickers&category=linear'

        # Realizar la solicitud a la API de funding
        funding_response = requests.get(funding_api_url)

        # Verificar si la solicitud de funding fue exitosa (código de respuesta 200)
        if funding_response.status_code == 200:
            funding_data = funding_response.json()
            logging.info("Datos de Funding: %s", json.dumps(funding_data, indent=2))

            # URL de la API para obtener datos de borrowing
            borrowing_api_url = 'https://oracle.yolodc.com/relay?url=https://api.bybit.com/v5/spot-margin-trade/data'

            # Realizar la solicitud a la API de borrowing
            borrowing_response = requests.get(borrowing_api_url)

            # Verificar si la solicitud de borrowing fue exitosa (código de respuesta 200)
            if borrowing_response.status_code == 200:
                borrowing_data = borrowing_response.json()
                logging.info("Datos de Borrowing: %s", json.dumps(borrowing_data, indent=2))

                # Obtener tasas de borrowing para todos los símbolos antes de iterar sobre los de funding
                borrowing_rates = obtener_tasas_de_borrowing(borrowing_data)
                logging.info("Tasas de borrowing: %s", json.dumps(borrowing_rates, indent=2))

                # Filtrar los símbolos que coinciden en ambas APIs y excluir el USDT
                symbols_in_both_apis = set(funding_data['result']['list']).intersection(borrowing_rates.keys()) - {'USDT'}
                logging.info("Símbolos en ambas APIs (sin USDT): %s", symbols_in_both_apis)

                # Verificar si hay símbolos en ambas APIs antes de continuar
                if not symbols_in_both_apis:
                    logging.warning("No hay símbolos coincidentes en ambas APIs. El script finalizará sin procesar datos.")
                else:
                    logging.info("Procesando datos para los símbolos coincidentes.")

                    # Diccionario para almacenar la información acumulada
                    data_aggregated = {}

                    # Iterar sobre la lista de pares de trading de funding
                    for symbol in symbols_in_both_apis:
                        logging.info("Iterando sobre el símbolo: %s", symbol)
                        try:
                            # Verificar si el símbolo está presente en los datos de financiamiento
                            if symbol in funding_data['result']['list']:
                                funding_rate_str = funding_data['result']['list'][symbol].get('fundingRate', '')

                                try:
                                    # Intentar convertir a float si la cadena no está vacía
                                    if funding_rate_str.strip() and funding_rate_str.replace('.', '', 1).isdigit():
                                        funding_rate = float(funding_rate_str)
                                    else:
                                        funding_rate = 0
                                except ValueError as ve:
                                    logging.error("Error al convertir a float en el símbolo %s: %s. Valor de la cadena: %s",
                                                  symbol, ve, funding_rate_str)
                                    funding_rate = 0
                            else:
                                funding_rate = 0

                            # Verificar si el símbolo está presente en las tasas de préstamos
                            if symbol in borrowing_rates:
                                borrowing_rate = borrowing_rates[symbol]
                            else:
                                borrowing_rate = {'currency': symbol, 'hourlyBorrowRate': 0}

                            # Agregar datos al diccionario acumulado
                            if symbol not in data_aggregated:
                                data_aggregated[symbol] = {'funding_rate_sum': 0, 'borrowing_rate_sum': 0}

                            data_aggregated[symbol]['funding_rate_sum'] += funding_rate
                            data_aggregated[symbol]['borrowing_rate_sum'] += borrowing_rate['hourlyBorrowRate']

                        except ValueError as ve:
                            logging.error("Error al convertir a float en el símbolo %s: %s", symbol, ve)
                        except Exception as e:
                            logging.error("Se produjo un error en el símbolo %s: %s", symbol, str(e))

                    # Crear un DataFrame de pandas con los datos acumulados
                    df = pd.DataFrame.from_dict(data_aggregated, orient='index')
                    df.index.name = 'Par'
                    df.reset_index(inplace=True)

                    # Guardar el DataFrame en un archivo Excel
                    df.to_excel("datos_agregados.xlsx", index=False)
                    logging.info("Datos guardados en el archivo 'datos_agregados.xlsx'.")

            else:
                logging.error("Error en la solicitud de borrowing. Código de respuesta: %s", borrowing_response.status_code)
        else:
            logging.error("Error en la solicitud de funding. Código de respuesta: %s", funding_response.status_code)

    except ValueError as ve:
        logging.error("Error al convertir a float: %s", ve)
    except Exception as e:
        logging.error("Se produjo un error: %s", str(e))

def obtener_tasas_de_borrowing(borrowing_data):
    rates = {}
    for category in borrowing_data['result']['vipCoinList']:
        for item in category['list']:
            currency = item['currency'].lower()
            rates[currency] = {
                'currency': currency,
                'hourlyBorrowRate': float(item['hourlyBorrowRate']) if 'hourlyBorrowRate' in item else 0
            }
    return rates

# Ejecutar la función principal
obtener_funding_rates()

