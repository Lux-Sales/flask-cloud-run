
import logging
import os
from posixpath import dirname, join
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel
from sqlalchemy import MetaData

from models import Materia

dotenv_path = join(dirname(__file__), '.env')  # Path to .env file
load_dotenv(dotenv_path)



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
db = SQLAlchemy(app)

metadata_obj = MetaData()

def basic_get_by_id(model: db.Model, obj_id: str) -> db.Model:
    resp = db.session.query(model).filter(model.id == obj_id).first()
    if resp:
        return resp
    raise Exception(dict(
        [
            ("code", 404),
            ("message", "The requested entity could not be found."),
            ("error_code", "entity_not_found"),
        ]
    ))

def create_or_update_entity_with_data(model: db.Model, data: dict, model_id: str = None) -> db.Model:
    if model_id:
        obj = basic_get_by_id(model, model_id)
    else:
        obj = model()
    for k in data.keys():
        obj.__setattr__(k, data.get(k))
    return obj

class MateriaSchema(BaseModel):
    nome: str
    docente: str
    
class MateriaUpdateSchema(BaseModel):
    nome: Optional[str]
    docente: Optional[str]
    



@app.route('/')
def home():
    return 'Home do serviço 2'

@app.route('/materias/', methods = ['GET'])
def get_materias():
    get_materias = Materia.query.all()
    materias = []
    for materia in get_materias:
        materias.append(materia.serialized)
    return make_response(jsonify({"Materias": materias}))


@app.route('/materias/', methods = ['POST'])
def register_materia():
    data = request.get_json()
    validated_data = MateriaSchema(**data)
    materia = create_or_update_entity_with_data(Materia, validated_data.dict())
    db.session.add(materia)
    db.session.commit()
    return make_response(jsonify({"Materia": materia.serialized}),200)

@app.route('/materias/<materia_id>/', methods = ['PUT'])
def update_materia(materia_id):
    data = request.get_json()
    materia_dict = basic_get_by_id(Materia, materia_id).serialized
    if MateriaUpdateSchema(**data).dict():
        for key in data.keys():
            materia_dict[key] = data[key]
        materia = create_or_update_entity_with_data(Materia, materia_dict, materia_id)
        db.session.commit()
        return make_response(jsonify({"Materia": materia.serialized}),200)

@app.route('/materias/<materia_id>/', methods = ['DELETE'])
def delete_materia(materia_id):
    materia = basic_get_by_id(Materia, materia_id)
    db.session.delete(materia)
    db.session.commit()
    return make_response(jsonify({"Deleted": True}),200)



@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
