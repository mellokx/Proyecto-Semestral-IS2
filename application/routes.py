"""Rutas de la aplicacion"""
from datetime import datetime, date
from lib2to3.pgen2.token import OP
from operator import length_hint
from re import I
import json
import numpy

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
        encuesta_aux = Encuesta(titulo=surveyData["title"],descripcion=surveyData["description"],fecha_inicio=date.today(),activa=True)
        db.session.add(encuesta_aux)
        db.session.commit()
        for i in range(0,len(surveyData["questions"])):
            if surveyData["questions"][i]["type"] == "desarrollo":
                pregunta_desarrollo_aux = Pregunta_Desarrollo(enunciado=surveyData["questions"][i]["statement"])
                db.session.add(pregunta_desarrollo_aux)
                db.session.commit()
                desarrollo_encuesta_aux = Desarrollo_Encuesta.insert().values(id_encuesta=encuesta_aux.id_encuesta,id_pregunta_desarrollo=pregunta_desarrollo_aux.id_pregunta_desarrollo)
                db.engine.execute(desarrollo_encuesta_aux)
                db.session.commit()
            else:
                pregunta_alternativa_aux = Pregunta_Alternativa(enunciado=surveyData["questions"][i]["statement"])
                db.session.add(pregunta_alternativa_aux)
                db.session.commit()
                alternativa_encuesta_aux = Alternativa_Encuesta.insert().values(id_encuesta=surveyData["id"],id_pregunta_alternativa=pregunta_alternativa_aux.id_pregunta_alternativa)
                db.engine.execute(alternativa_encuesta_aux)
                db.session.commit()
                for j in range(0,len(surveyData["questions"][i]["alternatives"])):
                    opcion_aux = Opcion(opcion=surveyData["questions"][i]["alternatives"][j]["textAlt"])
                    db.session.add(opcion_aux)
                    db.session.commit()
                    alternativas_aux = Alternativas.insert().values(id_pregunta_alternativa=pregunta_alternativa_aux.id_pregunta_alternativa,id_opcion=opcion_aux.id_opcion)
                    db.engine.execute(alternativas_aux)
                    db.session.commit()
        return "INFORMACION RECIBIDA" #Si llega aquí es porque no hubo problema
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
        """Consulta para obtener datos de preguntas de desarrollo"""
        ids_preguntas_desarrollo = []
        numeros_preguntas_desarrollo = []
        enunciado_preguntas_desarrollo = []
        comentario_preguntas_desarrollo = []
        if db.session.query(Desarrollo_Encuesta).filter_by(id_encuesta=id_encuesta).first() != None:
            tuplas_desarrollo_encuesta = db.session.query(
                Desarrollo_Encuesta).filter_by(id_encuesta=id_encuesta).all()
            for tupla_desarrollo_encuesta in tuplas_desarrollo_encuesta:
                ids_preguntas_desarrollo.append(
                    tupla_desarrollo_encuesta.id_pregunta_desarrollo)
            tuplas_pregunta_desarrollo = db.session.query(Pregunta_Desarrollo).filter(
                Pregunta_Desarrollo.id_pregunta_desarrollo.in_(ids_preguntas_desarrollo)).all()
            for tupla_pregunta_desarrollo in tuplas_pregunta_desarrollo:
                numeros_preguntas_desarrollo.append(
                    tupla_pregunta_desarrollo.numero)
                enunciado_preguntas_desarrollo.append(
                    tupla_pregunta_desarrollo.enunciado)
                comentario_preguntas_desarrollo.append(
                    tupla_pregunta_desarrollo.comentario)
            print("numeros_pd")  # pd -> pregunta desarrollo
            print(numeros_preguntas_desarrollo)
            print("enunciados_pd")
            print(enunciado_preguntas_desarrollo)
            print("comentarios_pd")
            print(comentario_preguntas_desarrollo)

        """Consulta para obtener datos de preguntas de alternativas"""
        ids_preguntas_alternativas = []
        numeros_preguntas_alternativas = []
        enunciado_preguntas_alternativas = []
        comentario_preguntas_alternativas = []
        ids_opciones = []
        string_opciones = []
        if db.session.query(Alternativa_Encuesta).filter_by(id_encuesta=id_encuesta).first() != None:
            tuplas_alternativa_encuesta = db.session.query(
                Alternativa_Encuesta).filter_by(id_encuesta=id_encuesta).all()
            for tupla_alternativa_encuesta in tuplas_alternativa_encuesta:
                ids_preguntas_alternativas.append(
                    tupla_alternativa_encuesta.id_pregunta_alternativa)
            tuplas_pregunta_alternativa = db.session.query(Pregunta_Alternativa).filter(
                Pregunta_Alternativa.id_pregunta_alternativa.in_(ids_preguntas_alternativas)).all()
            for tupla_pregunta_alternativa in tuplas_pregunta_alternativa:
                numeros_preguntas_alternativas.append(
                    tupla_pregunta_alternativa.numero)
                enunciado_preguntas_alternativas.append(
                    tupla_pregunta_alternativa.enunciado)
                comentario_preguntas_alternativas.append(
                    tupla_pregunta_alternativa.comentario)
            print("numeros_pa")  # pa -> pregunta alternativa
            print(numeros_preguntas_alternativas)
            print("enunciados_pa")
            print(enunciado_preguntas_alternativas)
            print("comentarios_pa")
            print(comentario_preguntas_alternativas)
            cantidad_opciones = 0
            for id_pregunta_alternativa in ids_preguntas_alternativas:
                if db.session.query(Alternativas).filter_by(id_pregunta_alternativa=id_pregunta_alternativa).first() != None:
                    cantidad_aux = db.session.query(Alternativas).filter_by(
                        id_pregunta_alternativa=id_pregunta_alternativa).count()
                    if cantidad_aux > cantidad_opciones:
                        cantidad_opciones = cantidad_aux
            # Cada fila de la matriz corresponde a un id_pregunta_alternativa
            # Cada elemento en la fila corresponde al id_opcion de las opciones de la pregunta
            # Si casilla esta en 0 es porque no existe esa opcion
            matriz_id_opciones = numpy.zeros(
                (len(ids_preguntas_alternativas), cantidad_opciones), int)
            i = 0
            j = 0
            for id_pregunta_alternativa in ids_preguntas_alternativas:
                if db.session.query(Alternativas).filter_by(id_pregunta_alternativa=id_pregunta_alternativa).first() != None:
                    tuplas_alternativas_aux = db.session.query(Alternativas).filter_by(
                        id_pregunta_alternativa=id_pregunta_alternativa).all()
                    for tupla_alternativa in tuplas_alternativas_aux:
                        matriz_id_opciones[i, j] = tupla_alternativa.id_opcion
                        j = j + 1
                    i = i + 1
                    j = 0
            print("matriz ids opciones")
            print(matriz_id_opciones)
            for id_pregunta_alternativa in ids_preguntas_alternativas:
                if db.session.query(Alternativas).filter_by(id_pregunta_alternativa=id_pregunta_alternativa).first() != None:
                    tuplas_alternativas_aux = db.session.query(Alternativas).filter_by(
                        id_pregunta_alternativa=id_pregunta_alternativa).all()
                    for tupla_alternativa in tuplas_alternativas_aux:
                        ids_opciones.append(tupla_alternativa.id_opcion)
            print("ids opciones")
            print(ids_opciones)
            tuplas_opcion = db.session.query(Opcion).filter(
                Opcion.id_opcion.in_(ids_opciones)).all()
            for tupla_opcion in tuplas_opcion:
                string_opciones.append(tupla_opcion.opcion)
            print("string opciones")
            print(string_opciones)
            # id_opciones[i] y string_opciones[i] es una i-esima opcion

        questions = []

        # Primero almacenaremos las preguntas de desarrollo.
        tam = len(ids_preguntas_desarrollo)
        i = 0
        while i < tam:
            data = {
                "id": ids_preguntas_desarrollo[i],
                "type": "desarrollo",
                "statement": enunciado_preguntas_desarrollo[i],
                "alternatives": []
            }
            questions.append(data)
            i += 1

        # Segundo almacenaremos las preguntas de desarrollo.
        tam = len(ids_preguntas_alternativas)
        i = 0
        indexOp = 0
        while i < tam:
            data = {
                "id": ids_preguntas_alternativas[i],
                "type": "alternativa",
                "statement": enunciado_preguntas_alternativas[i],
                "alternatives": []
            }
            tamAlt = numpy.count_nonzero(matriz_id_opciones[i])
            j = 0
            while j < tamAlt:
                dataOption = {
                    "id": ids_opciones[indexOp],
                    "textAlt": string_opciones[indexOp]
                }
                data["alternatives"].append(dataOption)
                j += 1
                print(string_opciones[indexOp])
                print(indexOp)
                indexOp += 1
            indexOp = j
            questions.append(data)
            i += 1

        dataSurvey = {
            "id": id_encuesta,
            "title": db.session.query(Encuesta).filter_by(id_encuesta=id_encuesta).first().titulo,
            "description": db.session.query(Encuesta).filter_by(id_encuesta=id_encuesta).first().descripcion,
            "questions": questions
        }

    # dataSurvey = {
    #     "id": 1,
    #     "title": "Titulo 1",
    #     "description": "Descripcion 1",
    #     "questions": [
    #         {
    #             "id": 1,
    #             "statement": "Pregunta desarrollo 1",
    #             "type": "desarrollo",
    #             "alternatives": []
    #         },
    #         {
    #             "id": 2,
    #             "statement": "Pregunta desarrollo 2",
    #             "type": "desarrollo",
    #             "alternatives": []

    #         },
    #         {
    #             "id": 1,
    #             "statement": "Pregunta alternativa 1",
    #             "type": "alternativa",
    #             "alternatives": [
    #                 {
    #                     "id": 1,
    #                     "textAlt": "Opcion 1"
    #                 },
    #                 {
    #                     "id": 2,
    #                     "textAlt": "Opcion 2"
    #                 }
    #             ]

    #         },
    #         {
    #             "id": 2,
    #             "statement": "Pregunta alternativa 2",
    #             "type": "alternativa",
    #             "alternatives": [
    #                 {
    #                     "id": 3,
    #                     "textAlt": "Opcion 3"
    #                 },
    #                 {
    #                     "id": 4,
    #                     "textAlt": "Opcion 4"
    #                 }
    #             ]

    #         }
    #     ]
    # }
        return render_template("admin/survey.html", data={
            "options": ["Preguntas", "Respuestas", "Configuración"],
            "selected": section,
            "id": id_encuesta,
            "dataSurvey": dataSurvey,
            "textButton": "Modificar"
        }
    )


@ app.route("/survey/<int:id_encuesta>/preguntas/<int:id_encuestado>")
def SurveyAns(id_encuesta, id_encuestado):
    print()


@ app.route("/answer_survey/<int:id_encuesta>")
def answer_survey(id_encuesta):
    dataSurvey = {
        "id": 1,
        "title": "Encuesta de la Universidad",
        "description": "Lorem ipsum dolor sit amet consectetur adipiscing elit, duis et arcu ante aliquam suscipit, integer pulvinar fames accumsan semper aenean. Nibh cursus ullamcorper auctor egestas integer aliquam taciti malesuada faucibus congue risus, duis lacinia lobortis ornare sagittis lectus interdum est semper dapibus venenatis elementum, laoreet facilisis libero tristique class euismod dictumst dignissim rhoncus molestie. Gravida fermentum ad nullam iaculis curae rutrum convallis consequat aptent, vitae risus massa tellus mi sociosqu class senectus vehicula mauris, pellentesque pulvinar nisl at nostra hac inceptos et.",
        "questions": [
            {
                "id": 1,
                "statement": "¿Cual es tu nombre?",
                "type": "desarrollo",
                "alternatives": []
            },
            {
                "id": 2,
                "statement": "Indica tu correo electronico",
                "type": "desarrollo",
                "alternatives": []

            },
            {
                "id": 1,
                "statement": "Te gustan los gatos",
                "type": "alternativa",
                "alternatives": [
                    {
                        "id": 1,
                        "textAlt": "Si obvio!"
                    },
                    {
                        "id": 2,
                        "textAlt": "No"
                    }
                ]

            },
            {
                "id": 2,
                "statement": "Cual de estos colores te gustan mas",
                "type": "alternativa",
                "alternatives": [
                    {
                        "id": 3,
                        "textAlt": "Azul"
                    },
                    {
                        "id": 4,
                        "textAlt": "Rojo"
                    },
                    {
                        "id": 5,
                        "textAlt": "Morado"
                    }
                ]

            }
        ]
    }
    return render_template("user/answer_survey.html", data=dataSurvey)
