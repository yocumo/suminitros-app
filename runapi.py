import requests
import pandas as pd


headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Token 52cca904974d60be2dd4f5d3024bcb5d2135ec8a",
    "Organization": "164",
}

stock_maximo = pd.read_csv("stock_maximos.csv")
stock_maximo["CODIGO"] = stock_maximo["CODIGO"].astype(str)


# conexión a la api
def RunApi(URL):
    api_url = URL
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code in [200, 201]:
            return response.json()
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


# ETL dataframe cartera tecnicos y cruce con csv stock_maximos = tope
def consulta(user_id):
    api = "https://app.sytex.io/api/materialstock/?staff=" + str(user_id) + "&limit=100"
    ln = RunApi(api)

    try:
        if ln["results"]:
            df = ln["results"]
            data = []

            for i in df:
                data.append(
                    {
                        "Tipo": i["material"]["material_type"]["name"],
                        "Código de material": i["material_code"],
                        "Nombre de material": i["material_name"],
                        "Ubicación": i["location"]["name"],
                        "Cantidad": i["quantity"],
                    }
                )

            df2 = pd.DataFrame(data).sort_values(by="Tipo")
            user_name = df2.iloc[0]["Ubicación"]
            df_g = (
                df2.groupby("Código de material")
                .agg(
                    {
                        "Tipo": "first",
                        "Nombre de material": "first",
                        "Cantidad": "sum",
                    }
                )
                .reset_index()
            )

            df_g = df_g.sort_values(by="Tipo")

            merged_df = pd.merge(
                df_g,
                stock_maximo,
                left_on="Código de material",
                right_on="CODIGO",
                how="left",
            )
            df_stock = merged_df.drop(columns=["CODIGO", "MATERIAL"])
            df_stock.fillna(0, inplace=True)
            df_stock = df_stock.rename(columns={"TECNICOS": "Tope"}).astype(
                {"Tope": int}
            )

            df_stock["diff"] = df_stock.apply(
                lambda i: (
                    i["Tope"] - i["Cantidad"] if i["Tope"] != 0 else i["Cantidad"]
                ),
                axis=1,
            )
            equipos = df_stock.loc[df_stock["Tipo"] == "Equipos", "Cantidad"].sum()

            return df_stock, user_name, equipos
        else:
            print("User_id no existe " + user_id)
            return "Usuer_id no existe " + user_id

    except Exception as e:
        print(f"error : {str(e)}" + " al encontrar al usuario " + str(user_id))
        return f"error : {str(e)}" + " al encontrar al usuario " + str(user_id)


# Encontrar codigo de usuario=tecnico para encontrar los datos de sus cartera en def consulta
def FindUser(User):
    api = "https://app.sytex.io/api/staff/?q=" + str(User)
    User = RunApi(api)
    try:
        if User["results"][0]["id"]:
            user_id = User["results"][0]["id"]
            send_ui = consulta(user_id)
            return send_ui
        else:
            print("Usuario no existe " + User)
            return "Usuario no existe " + User

    except Exception as e:
        print(f"error : {str(e)}" + " al encontrar al usuario " + str(User))
        return f"error : {str(e)}" + " al encontrar al usuario " + str(User)
