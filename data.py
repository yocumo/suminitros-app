from flask import json, jsonify
import requests
import pandas as pd
from io import BytesIO

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Token 52cca904974d60be2dd4f5d3024bcb5d2135ec8a",
    "Organization": "164",
}


# conexión a la api y conversión de rebote de excel a dataframe
def RunApi(URL):
    api_url = URL
    try:
        response = requests.get(api_url, headers=headers)

        if response.status_code in [200, 201]:
            excel_data = BytesIO(response.content)
            df = pd.read_excel(excel_data)
            return df
        else:
            data = response.json()
            print("Datos de la API:", data)
            return ("Datos de la API:", data)

    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud a la API: {str(e)}")
        return f"Error al realizar la solicitud a la API: {str(e)}"

    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")
        return f"Ocurrió un error: {str(e)}"


# ETL cartera bodega
def suministros():
    api = "https://app.sytex.io/api/materialstocktotaldata?org_id=164&should_list_in_warehouse_stock=467&virtual_warehouse_stock=467"
    ln = RunApi(api)
    df_bodega = ln.sort_values(by="Tipo de material")
    json_data = df_bodega.to_json(orient="records")
    return jsonify(json.loads(json_data))
