import logging
import os
from posixpath import dirname, join
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel

from .models import Aluno

dotenv_path = join(dirname(__file__), '.env')  # Path to .env file
load_dotenv(dotenv_path)


app = Flask(__name__)

if os.environ.get('DB_INSTANCE_NAME'):
    app.config['SQLALCHEMY_DATABASE_URI']= (
        f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@/{os.environ.get('DB_NAME')}?unix_socket=/cloudsql/{os.environ.get('DB_INSTANCE_NAME')}"
    )
else:
    app.config['SQLALCHEMY_DATABASE_URI']= (
        f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
    )

db = SQLAlchemy(app)

# metadata_obj = MetaData()

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


### Schemas ####

class AlunoSchema(BaseModel):
    nome: str
    faltas: float
    
class AlunoUpdateSchema(BaseModel):
    nome: Optional[str]
    faltas: Optional[float]
    



@app.route('/alunos/home/')
def home():
    return 'Home do serviço 1'

@app.route('/alunos/', methods = ['GET'])
def get_alunos():
    get_alunos = Aluno.query.all()
    alunos = []
    for aluno in get_alunos:
        alunos.append(aluno.serialized)
    return make_response(jsonify({"Alunos": alunos}))


@app.route('/alunos/', methods = ['POST'])
def register_aluno():
    data = request.get_json()
    validated_data = AlunoSchema(**data)
    aluno = create_or_update_entity_with_data(Aluno, validated_data.dict())
    db.session.add(aluno)
    db.session.commit()
    return make_response(jsonify({"Aluno": aluno.serialized}),200)

@app.route('/alunos/<aluno_id>/', methods = ['PUT'])
def update_aluno(aluno_id):
    data = request.get_json()
    aluno_dict = basic_get_by_id(Aluno, aluno_id).serialized
    if AlunoUpdateSchema(**data).dict():
        for key in data.keys():
            aluno_dict[key] = data[key]
        aluno = create_or_update_entity_with_data(Aluno, aluno_dict, aluno_id)
        db.session.commit()
        return make_response(jsonify({"Aluno": aluno.serialized}),200)

@app.route('/alunos/<aluno_id>/', methods = ['DELETE'])
def delete_aluno(aluno_id):
    aluno = basic_get_by_id(Aluno, aluno_id)
    db.session.delete(aluno)
    db.session.commit()
    return make_response(jsonify({"Deleted": True}),200)



@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
