from google.auth import exceptions
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import gspread

def enviar_a_google_sheets(df):
    # Ruta al archivo JSON con las credenciales
    credentials_path = 'ruta_a_tu_archivo_json_con_credenciales.json'

    try:
        # Autenticación con Google Sheets
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=["", ""]
        )

        # Verifica si las credenciales están expiradas y actualízalas si es necesario
        if credentials.expired:
            credentials.refresh(Request())

        gc = gspread.authorize(credentials)

        # ID de tu hoja de cálculo de Google Sheets
        spreadsheet_id = ''

        # Abre la hoja de cálculo
        worksheet = gc.open_by_key(spreadsheet_id).sheet1

        # Antes de enviar a Google Sheets
        print("Antes de enviar a Google Sheets")
        print(df)

        # Verifica si el DataFrame está vacío
        if df.empty:
            print("El DataFrame está vacío. No se enviarán datos a Google Sheets.")
        else:
            # Después de enviar a Google Sheets
            print("Después de enviar a Google Sheets")
            
        worksheet.clear()

        # Envía el DataFrame a Google Sheets
        gc.import_pandas(df, worksheet.id)

        # Después de enviar a Google Sheets
        print("Después de enviar a Google Sheets")



    except exceptions.GoogleAuthError as e:
        print(f"Error de autenticación con Google Sheets: {e}")



