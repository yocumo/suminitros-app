import os
import runapi
import data
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    send_file,
)

app = Flask(__name__)


@app.route("/")
def index():
    print("Request for index page received")
    return render_template("home.html")


@app.route("/hello", methods=["GET"])
def hello():

    try:
        return render_template("hello.html")

    except ValueError as e:
        print(f"Error: {e} -- redirecting to /hello")
        return redirect(url_for("index"))


@app.route("/consulta", methods=["POST"])
def consulta():

    name = str(request.form.get("name"))
    if name:
        print(f"Request for consulta page received with name={name}")
        try:
            df, user_name, eq = runapi.FindUser(name)

            if df is not None:
                styled_df = df.style.applymap(color_diff, subset=["diff"])
                html_table = styled_df.to_html()

                return render_template(
                    "home.html",
                    consulta_result=html_table,
                    name=name,
                    user=user_name,
                    eq=eq,
                )
            else:
                return """<html lang="es">
                     <head>
                        <meta charset="UTF-8">
                        <title>Hola Mundo</title>
                     </head>
                     <body>
                        <h1>¡Ups! al parecer no hay datos para mostrar</h1>
                     </body>
                     </html>"""
        except ValueError as e:
            print(f"Error: {e} -- redirecting to /hello")
            return redirect(url_for("hello"))

    else:
        print(
            "Request for hello page received with no name or blank name -- redirecting"
        )
        return redirect(url_for("index"))


@app.route("/bodega", methods=["GET"])
def bodega():
    try:
        df = data.suministros()
        if df is not None:
            df_html = df.to_html()
            return render_template("almacen.html", df_html=df_html)

        else:
            return """<html lang="es">
                     <head>
                        <meta charset="UTF-8">
                        <title>Hola Mundo</title>
                     </head>
                     <body>
                        <h1>¡Ups! al parecer no hay datos para mostrar</h1>
                     </body>
                     </html>"""
    except ValueError as e:
        print(f"Error: {e} -- redirecting to /hello")
        return redirect(url_for("hello"))


def color_diff(val):
    color = "red" if val < 1 else ""
    return f"background-color: {color}"


if __name__ == "__main__":
    app.run(debug=True)
