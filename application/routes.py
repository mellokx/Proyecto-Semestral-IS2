"""Rutas de la aplicacion"""
from .consultas import *
from .estructuraInterfaz import *
import json

from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for

from .models import *


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/guardar_admin", methods=['POST'])
def guardar_admin():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        admi_aux = Admin(nombre=nombre, email=email)
        db.session.add(admi_aux)
        db.session.commit()
        return 'received'


@app.route("/ir_a_crear_nueva_encuesta", methods=['GET'])
def crea_nueva_encuesta():
    if db.session.query(Encuesta).order_by(Encuesta.id_encuesta.desc()).first() == None:
        return redirect("/survey/1/preguntas")
    else:
        id_ultima_encuesta = db.session.query(Encuesta).order_by(
            Encuesta.id_encuesta.desc()).first().id_encuesta
        id_nueva = id_ultima_encuesta + 1
        return redirect("/survey/"+str(id_nueva)+"/preguntas")


@app.route("/ir_a_ultima_encuesta", methods=['GET'])
def ir_a_ultima_encuesta():
    if db.session.query(Encuesta).order_by(Encuesta.id_encuesta.desc()).first() == None:
        return redirect("/survey/1/preguntas")
    else:
        id_ultima_encuesta = db.session.query(Encuesta).order_by(
            Encuesta.id_encuesta.desc()).first().id_encuesta
        return redirect("/survey/"+str(id_ultima_encuesta)+"/preguntas")


@app.route("/crear_encuesta", methods=['POST'])
def crear_encuesta():
    if request.method == 'POST':
        surveyData = json.loads(request.form.get("surveyData"))
        return guardar_encuesta(surveyData)
    return redirect("/")


@app.route("/responder_encuesta", methods=['POST'])
def responder_encuesta():
    if request.method == 'POST':
        responses = json.loads(request.form.get("responses"))
        guardar_respuesta(responses)
        return print()
    return redirect("/")


@app.route("/survey/")
@app.route("/survey/<int:id_encuesta>/")
@app.route("/survey/<int:id_encuesta>/<string:section>")
def Survey(id_encuesta, section="preguntas"):
    if db.session.query(Encuesta).filter_by(id_encuesta=id_encuesta).first() == None:
        # if id > 1: (Si no existe forzar redireccionamiento a la que sigue))
        #    return redirect("/")
        dataSurvey = {
            "id": id_encuesta,
            "title": "",
            "description": "",
            "questions": []
        }
        return render_template("admin/survey.html", data={
            "options": ["Preguntas", "Respuestas", "Configuración"],
            "selected": section,
            "id": id_encuesta,
            "dataSurvey": dataSurvey,
            "textButton": "Guardar"
        }
        )
    else:
        dataSurvey = crear_dataSurvey(id_encuesta)
        return render_template("admin/survey.html", data={
            "options": ["Preguntas", "Respuestas", "Configuración"],
            "selected": section,
            "id": id_encuesta,
            "dataSurvey": dataSurvey,
            "textButton": "Modificar"
        }
        )


@ app.route("/answer_survey/<int:id_encuesta>")
def answer_survey(id_encuesta):
    if db.session.query(Encuesta).filter_by(id_encuesta=id_encuesta).first() != None:
        dataSurvey = crear_dataSurvey(id_encuesta)
        print(dataSurvey)
    # dataSurvey = {
    #    "id": 1,
    #    "title": "Encuesta de la Universidad",
    #    "description": "Lorem ipsum dolor sit amet consectetur adipiscing elit, duis et arcu ante aliquam suscipit, integer pulvinar fames accumsan semper aenean. Nibh cursus ullamcorper auctor egestas integer aliquam taciti malesuada faucibus congue risus, duis lacinia lobortis ornare sagittis lectus interdum est semper dapibus venenatis elementum, laoreet facilisis libero tristique class euismod dictumst dignissim rhoncus molestie. Gravida fermentum ad nullam iaculis curae rutrum convallis consequat aptent, vitae risus massa tellus mi sociosqu class senectus vehicula mauris, pellentesque pulvinar nisl at nostra hac inceptos et.",
    #    "questions": [
    #        {
    #            "id": 1,
    #            "statement": "¿Cual es tu nombre?",
    #            "type": "desarrollo",
    #            "alternatives": []
    #        },
    #        {
    #            "id": 2,
    #            "statement": "Indica tu correo electronico",
    #            "type": "desarrollo",
    #            "alternatives": []
    #
    #        },
    #        {
    #            "id": 1,
    #            "statement": "Te gustan los gatos",
    #            "type": "alternativa",
    #            "alternatives": [
    #                {
    #                    "id": 1,
    #                    "textAlt": "Si obvio!"
    #                },
    #                {
    #                    "id": 2,
    #                    "textAlt": "No"
    #                }
    #            ]
    #
    #        },
    #        {
    #            "id": 2,
    #            "statement": "Cual de estos colores te gustan mas",
    #            "type": "alternativa",
    #            "alternatives": [
    #                {
    #                    "id": 3,
    #                    "textAlt": "Azul"
    #                },
    #                {
    #                    "id": 4,
    #                    "textAlt": "Rojo"
    #                },
    #                {
    #                    "id": 5,
    #                    "textAlt": "Morado"
    #                }
    #            ]
    #
    #        }
    #    ]
    # }
        return render_template("user/answer_survey.html", data=dataSurvey)
    else:
        print("Error: Encuesta no existente")
        return redirect("/")
