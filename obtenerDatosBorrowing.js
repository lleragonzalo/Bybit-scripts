function escribirDatosEnHoja(dataSets) {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName("Datos de Préstamos");

  // Encabezados de columna, incluyendo la nueva columna
  var headers = ["Moneda", "Prestable", "Relación Colateral", "Tasa de Interés Horaria", "Orden de Liquidación", "Garantía Adicional", "Monto Máximo de Préstamo", "Tasa de Interés Anual", "Tasa de Interés Anual (%)"];

  // Asegúrate de que la hoja tenga los encabezados
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  // Escribe los datos en la hoja de cálculo
  for (var i = 0; i < dataSets.length; i++) {
    var rowData = [
      dataSets[i].currency,
      dataSets[i].borrowable,
      dataSets[i].collateralRatio,
      dataSets[i].hourlyBorrowRate,
      dataSets[i].liquidationOrder,
      dataSets[i].marginCollateral,
      dataSets[i].maxBorrowingAmount,
      dataSets[i].annualBorrowRate,
      dataSets[i].annualBorrowRate * 100
    ];
    sheet.appendRow(rowData);
  }
}

function jsonToDataArray(json) {
  function flattenObject(ob) {
    var result = {};
    for (var i in ob) {
      if ((typeof ob[i]) === 'object' && !Array.isArray(ob[i])) {
        var temp = flattenObject(ob[i]);
        for (var j in temp) {
          result[i + '.' + j] = temp[j];
        }
      } else {
        result[i] = ob[i];
      }
    }
    return result;
  }

  if (typeof json === 'object') {
    var flatObject = flattenObject(json);
    var keys = Object.keys(flatObject);
    var data = keys.map(function(key) {
      return flatObject[key];
    });

    console.log("Datos procesados correctamente:", JSON.stringify(data, null, 2));  // Agregado para depurar

    return { data: [data], keys: keys };  // Nota: Se envuelve 'data' en un array para mantener la consistencia con la estructura de salida de jsonToDataArray
  } else {
    console.error("El argumento no es un objeto JSON válido.");
    return null;
  }
}

function obtenerDatosBorrowing() {
  var API_KEY = "JT1y5FvxnyjqfVvVHs";
  var API_SECRET = "vw14SB2Qw6vhMLs7Da9F4QsP2V6jtK4mcTA6";

  var monedas = ['USDT', 'BTC', 'ETH'];

  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName("Datos de Préstamos");


   var dataSets = []; // Almacena todos los conjuntos de datos

  for (var i = 0; i < monedas.length; i++) {
    var symbol = monedas[i];
    var borrowingData = obtenerDatosBorrowingPorMoneda(symbol, API_KEY, API_SECRET);

    if (borrowingData && borrowingData.result && borrowingData.result.vipCoinList && borrowingData.result.vipCoinList[0] && borrowingData.result.vipCoinList[0].list) {
      console.log("Datos completos para " + symbol + ":", borrowingData);

      var listData = borrowingData.result.vipCoinList[0].list;

      if (listData.length > 0) {
        for (var rowIndex = 0; rowIndex < listData.length; rowIndex++) {
          var rowData = listData[rowIndex];
          var dataSet = {
            currency: rowData.currency,
            borrowable: rowData.borrowable,
            collateralRatio: rowData.collateralRatio,
            hourlyBorrowRate: rowData.hourlyBorrowRate,
            liquidationOrder: rowData.liquidationOrder,
            marginCollateral: rowData.marginCollateral,
            maxBorrowingAmount: rowData.maxBorrowingAmount,
            annualBorrowRate: rowData.hourlyBorrowRate * 24 * 365
          };

          dataSets.push(dataSet); // Agrega el conjunto de datos al arreglo
        }
      } else {
        console.error("La lista de préstamos para " + symbol + " está vacía.");
      }
    } else {
      console.error("No se pudieron obtener los datos de borrowing para " + symbol + ".");
      if (borrowingData) {
        console.error("Datos obtenidos:", borrowingData);
      }
    }
  }

  console.log("Todos los dataSets:", dataSets); // Muestra todos los conjuntos de datos al final

  escribirDatosEnHoja(dataSets); // Escribe los datos en la hoja de cálculo
}


function obtenerDatosBorrowingPorMoneda(symbol, apiKey, apiSecret) {
  var endpoint = 'https://oracle.yolodc.com/relay?url=https://api.bybit.com/v5/spot-margin-trade/data';

  try {
    var coin = symbol.slice(0, -4);
    var timestamp = new Date().getTime();
    var queryParams = 'timestamp=' + timestamp + '&api_key=' + apiKey + '&coin=' + coin;
    var message = 'GET ' + endpoint + '?' + queryParams;
    var signature = Utilities.computeHmacSha256Signature(message, apiSecret);
    var signatureHex = Utilities.base64Encode(signature);
    var headers = {
      'api-key': apiKey,
      'timestamp': timestamp,
      'sign': signatureHex
    };

    var options = {
      'method': 'get',
      'headers': headers
    };

    var response = UrlFetchApp.fetch(endpoint + '?' + queryParams, options);

    var responseCode = response.getResponseCode();
    var contentText = response.getContentText();

    if (responseCode === 200) {
      try {
        var responseData = JSON.parse(contentText);
        return responseData;
      } catch (e) {
        console.error("Error al analizar la respuesta JSON para " + coin + ": " + e);
        console.error("Respuesta JSON no válida:", contentText);
        return null;
      }
    } else {
      console.error("Error en la solicitud para " + coin + ". Código de estado: " + responseCode);
      console.error("Mensaje de error:", contentText);
      return null;
    }
  } catch (error) {
    console.error("Error general en la solicitud para " + coin + ": " + error);
    return null;
  }
}