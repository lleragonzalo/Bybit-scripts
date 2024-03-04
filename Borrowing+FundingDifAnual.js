function escribirDatosEnHoja(dataSets, fundingRates) {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = "Datos totales";
  var sheet = spreadsheet.getSheetByName(sheetName);

  if (!sheet) {
    Logger.log("La hoja con el nombre '" + sheetName + "' no se encontró.");
    return;
  }

  var headers = ["Currency", "Borrowable", "Collateral Ratio", "Hourly Borrow Rate", "Liquidation Order", "Margin Collateral", "Max Borrowing Amount", "Anual Borrow Rate", "Anual Borrow Rate (%)", "Funding Rate", "Sum B+F"];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);


  for (var i = 0; i < dataSets.length; i++) {
    var sumaTasa = dataSets[i].hourlyBorrowRate + (obtenerFundingRate(fundingRates, dataSets[i].currency) || 0);

    var rowData = [
      dataSets[i].currency,
      dataSets[i].borrowable,
      dataSets[i].collateralRatio,
      dataSets[i].hourlyBorrowRate,
      dataSets[i].liquidationOrder,
      dataSets[i].marginCollateral,
      dataSets[i].maxBorrowingAmount,
      dataSets[i].annualBorrowRate,
      dataSets[i].annualBorrowRate * 100,
      obtenerFundingRate(fundingRates, dataSets[i].currency) || 0,
      sumaTasa
    ];

    sheet.appendRow(rowData);
  }
}


function obtenerDatosFundingRates() {
  var fundingApiUrl = 'https://oracle.yolodc.com/relay?url=https://api.bybit.com/v5/market/tickers&category=linear';
  var fundingResponse = UrlFetchApp.fetch(fundingApiUrl);

  if (fundingResponse.getResponseCode() == 200) {
    var fundingData = JSON.parse(fundingResponse.getContentText());
    Logger.log("Datos de Funding: " + JSON.stringify(fundingData));

    var dataSets = obtenerDatosBorrowing();

    // Asegurémonos de que dataSets sea un array antes de llamar a map
    if (!Array.isArray(dataSets)) {
      Logger.log("Error: dataSets no es un array.");
      return;
    }

    var commonCurrencies = dataSets.map(function(data) {
      return data.currency;
    }).filter(function(currency) {
      return fundingData.result.list.some(function(pair_data) {
        return pair_data.symbol.replace("USDT", "") === currency.replace("USDT", "");
      });
    });

    Logger.log("Monedas comunes encontradas: " + commonCurrencies.join(', '));

    var hojaCalculo = SpreadsheetApp.getActiveSpreadsheet();
    var nombreHoja = "Datos totales";
    var hojaDatos = hojaCalculo.getSheetByName(nombreHoja);

    if (!hojaDatos) {
      hojaDatos = hojaCalculo.insertSheet(nombreHoja);
    } else {
      hojaDatos.clear();
    }

    hojaDatos.appendRow(["Currency", "Borrowable", "Collateral Ratio", "Hourly Borrow Rate", "Liquidation Order", "Margin Collateral", "Max Borrowing Amount", "Anual Borrow Rate", "Anual Borrow Rate (%)", "Funding Rate"]);

    var monedasProcesadas = new Set();

commonCurrencies.forEach(function(currency) {
  // Verifica si la moneda ya ha sido procesada
  if (!monedasProcesadas.has(currency)) {
    var dataSet = dataSets.find(function(data) {
      return data.currency.replace("USDT", "") === currency.replace("USDT", "");
    });

    if (dataSet) {
      var fundingRate = fundingData.result.list.find(function(pair_data) {
        return pair_data.symbol && pair_data.symbol.replace("USDT", "") === currency.replace("USDT", "");
      });

      if (fundingRate) {
        // Agrega la fila solo si la moneda no ha sido procesada previamente
        hojaDatos.appendRow([
          dataSet.currency,
          dataSet.borrowable,
          dataSet.collateralRatio,
          dataSet.hourlyBorrowRate,
          dataSet.liquidationOrder,
          dataSet.marginCollateral,
          dataSet.maxBorrowingAmount,
          dataSet.annualBorrowRate,
          dataSet.annualBorrowRate * 100,
          parseFloat(fundingRate.fundingRate) || 0
        ]);

        // Agrega la moneda al conjunto de monedas procesadas
        monedasProcesadas.add(currency);
      }
    }
  }
});

  } else {
    Logger.log("Error en la solicitud de funding. Código de respuesta: " + fundingResponse.getResponseCode());
  }
}

// Función auxiliar para obtener la tasa de financiamiento correspondiente a la moneda, ignorando "USDT"
function obtenerFundingRate(fundingRates, currency) {
  // Busca la moneda en fundingRates, ignorando "USDT"
  var cleanedCurrency = currency.replace("USDT", "");
  return fundingRates && Object.prototype.hasOwnProperty.call(fundingRates, cleanedCurrency) ? fundingRates[cleanedCurrency] : undefined;
}

function obtenerFundingRatesAsObject(sheet) {
  var fundingRates = {};
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    fundingRates[data[i][0]] = data[i][1];
  }
  return fundingRates;
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

    console.log("Datos procesados correctamente:", JSON.stringify(data, null, 2));

    return { data: [data], keys: keys };
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
  var sheet = spreadsheet.getSheetByName("Datos totales");

  var dataSets = []; // Almacena todos los conjuntos de datos

  for (var i = 0; i < monedas.length; i++) {
    var symbol = monedas[i];
    var borrowingData = obtenerDatosBorrowingPorMoneda(symbol, API_KEY, API_SECRET);

    if (borrowingData && borrowingData.result && borrowingData.result.vipCoinList && borrowingData.result.vipCoinList[0] && borrowingData.result.vipCoinList[0].list) {
      console.log("Datos completos para " + symbol + ":", borrowingData);

      var listData = borrowingData.result.vipCoinList[0].list;

      // ...

if (listData.length > 0) {
  for (var rowIndex = 0; rowIndex < listData.length; rowIndex++) {
  var rowData = listData[rowIndex];
  console.log("rowData: " + JSON.stringify(rowData));

  var dataSet = {
    currency: rowData.currency,
    borrowable: rowData.borrowable,
    collateralRatio: rowData.collateralRatio,
    hourlyBorrowRate: rowData.hourlyBorrowRate,
    liquidationOrder: rowData.liquidationOrder,
    marginCollateral: rowData.marginCollateral,
    maxBorrowingAmount: rowData.maxBorrowingAmount,
    annualBorrowRate: rowData.hourlyBorrowRate * 24 * 365 * -1
  };

  console.log("dataSet: " + JSON.stringify(dataSet));

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

  // Si dataSets está vacío o no es un array, regresa un array vacío
  return Array.isArray(dataSets) ? dataSets : [];
}

function columnaSumatoria() {
  var hojaCalculo = SpreadsheetApp.getActiveSpreadsheet();
  var nombreHoja = "Datos totales";
  var hoja = hojaCalculo.getSheetByName(nombreHoja);

  if (!hoja) {
    Logger.log("La hoja con el nombre '" + nombreHoja + "' no se encontró.");
    return;
  }

  // Obtener datos actuales
  var datos = hoja.getDataRange().getValues();

  // Añadir encabezado de nueva columna
  var nuevaColumnaIndex = datos[0].length + 1;
  hoja.getRange(1, nuevaColumnaIndex).setValue("Borrowing + Funding");

  // Calcular y añadir la sumatoria para cada fila
  for (var i = 1; i < datos.length; i++) {
    var tasaInteresHoraria = datos[i][3]; // Suponiendo que la Tasa de Interés Horaria está en la cuarta columna
    var tasaFinanciacion = datos[i][9]; // Suponiendo que la Tasa de Financiación está en la décima columna

    var sumaTasa = tasaInteresHoraria + tasaFinanciacion;
    hoja.getRange(i + 1, nuevaColumnaIndex).setValue(sumaTasa);
  }

  Logger.log("Se ha añadido la columna de sumatoria correctamente.");
}

function columnaFundingRateAnual() {
  var hojaCalculo = SpreadsheetApp.getActiveSpreadsheet();
  var nombreHoja = "Datos totales";
  var hoja = hojaCalculo.getSheetByName(nombreHoja);

  if (!hoja) {
    Logger.log("La hoja con el nombre '" + nombreHoja + "' no se encontró.");
    return;
  }

  // Obtener datos actuales
  var datos = hoja.getDataRange().getValues();

  // Añadir encabezado de nueva columna
  var nuevaColumnaIndex = datos[0].length + 1;
  hoja.getRange(1, nuevaColumnaIndex).setValue("Funding Rate Anual");

  // Calcular y añadir la tasa de financiamiento anual para cada fila
  for (var i = 1; i < datos.length; i++) {
    var tasaFinanciacion = datos[i][9]; // Suponiendo que la Tasa de Financiación está en la décima columna

    // Suponiendo que la Tasa de Financiación es anual, de lo contrario, ajusta la fórmula según tu necesidad
    var tasaFinanciacionAnual = tasaFinanciacion * 365 * 24;

    hoja.getRange(i + 1, nuevaColumnaIndex).setValue(tasaFinanciacionAnual);
  }

  Logger.log("Se ha añadido la columna de Funding Rate Anual correctamente.");
}

function columnaFundingRateAnualPorcentaje() {
  var hojaCalculo = SpreadsheetApp.getActiveSpreadsheet();
  var nombreHoja = "Datos totales";
  var hoja = hojaCalculo.getSheetByName(nombreHoja);

  if (!hoja) {
    Logger.log("La hoja con el nombre '" + nombreHoja + "' no se encontró.");
    return;
  }

  // Obtener datos actuales
  var datos = hoja.getDataRange().getValues();

  // Añadir encabezado de nueva columna
  var nuevaColumnaIndex = datos[0].length + 1;
  hoja.getRange(1, nuevaColumnaIndex).setValue("Funding Rate Anual (%)");

  // Calcular y añadir la tasa de financiamiento anual en porcentaje para cada fila
  for (var i = 1; i < datos.length; i++) {
    var tasaFinanciacionAnual = datos[i][datos[0].length - 1]; // Tomar el valor de la columna de Funding Rate Anual

    // Convertir la tasa de financiamiento anual a porcentaje
    var tasaFinanciacionAnualPorcentaje = tasaFinanciacionAnual * 100;

    hoja.getRange(i + 1, nuevaColumnaIndex).setValue(tasaFinanciacionAnualPorcentaje);
  }

  Logger.log("Se ha añadido la columna de Funding Rate Anual en Porcentaje correctamente.");
}

function columnaDiferenciaFundingBorrowRates() {
  var hojaCalculo = SpreadsheetApp.getActiveSpreadsheet();
  var nombreHoja = "Datos totales";
  var hoja = hojaCalculo.getSheetByName(nombreHoja);

  if (!hoja) {
    Logger.log("La hoja con el nombre '" + nombreHoja + "' no se encontró.");
    return;
  }

  // Obtener datos actuales
  var datos = hoja.getDataRange().getValues();

  // Añadir encabezado de nueva columna
  var nuevaColumnaIndex = datos[0].length + 1;
  hoja.getRange(1, nuevaColumnaIndex).setValue("Diferencia Funding-Borrow Rates");

  // Calcular y añadir la diferencia para cada fila
  for (var i = 1; i < datos.length; i++) {
    var tasaFundingAnualPorcentaje = datos[i][datos[0].length - 2]; // Obtener la tasa de financiamiento anual en porcentaje
    var tasaBorrowAnualPorcentaje = datos[i][datos[0].length - 3]; // Obtener la tasa de préstamo anual en porcentaje


    // Calcular la diferencia sumando las tasas
      var diferencia = tasaFundingAnualPorcentaje - tasaBorrowAnualPorcentaje;
      hoja.getRange(i + 1, nuevaColumnaIndex).setValue(diferencia);
  }

  Logger.log("Se ha añadido la columna de Diferencia Funding-Borrow Rates correctamente.");
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