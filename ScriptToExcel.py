from google.auth import exceptions
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import gspread



def enviar_a_google_sheets(df):

    credentials_path = 'ruta_a_tu_archivo_json_con_credenciales.json'

    try:
      
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )

 
        if credentials.expired:
            credentials.refresh(Request())

        gc = gspread.authorize(credentials)

     
        spreadsheet_id = ''


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



    except exceptions.GoogleAuthError as e:
        print(f"Error de autenticación con Google Sheets: {e}")




