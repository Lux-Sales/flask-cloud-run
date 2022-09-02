# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
from datetime import datetime
import json
import logging
import os
from posixpath import dirname, join
from typing import Optional
from uuid import uuid1
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from dotenv import load_dotenv
from sqlalchemy import MetaData
from pydantic import BaseModel
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.mysql import BIGINT, DOUBLE
from flask_migrate import Migrate


dotenv_path = join(dirname(__file__), '.env')  # Path to .env file
load_dotenv(dotenv_path)



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

metadata_obj = MetaData()

def basic_get_by_id(model: db.Model, obj_id: str) -> db.Model:
    resp = db.session.query(model).filter(model.id == obj_id).first()
    if resp:
        return resp
    raise dict(
            [
                ("code", 404),
                ("message", "The requested entity could not be found."),
                ("error_code", "entity_not_found"),
            ]
        )

def create_or_update_entity_with_data(model: db.Model, data: dict, model_id: str = None) -> db.Model:
    if model_id:
        obj = basic_get_by_id(model, model_id)
    else:
        obj = model()
    for k in data.keys():
        obj.__setattr__(k, data.get(k))
    return obj

###Models####
def generate_uuid() -> int:
    return uuid1().int >> 100


class DefaultModel(object):

    __mapper_args__ = {"always_refresh": True, "confirm_deleted_rows": False}

    id = db.Column(BIGINT, primary_key=True, autoincrement=False)

    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def id_(self):
        return str(self.id)

    def __init__(self, **kwargs):
        self.id = generate_uuid()
        for k, val in kwargs.items():
            self.__setattr__(k, val)
            
class Aluno(DefaultModel, db.Model):
    __tablename__ = "aluno"
    
    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(20))
    
    faltas = db.Column(db.Integer)
    
    @property
    def serialized(self):
        return{
            'id':self.id,
            'nome':self.nome,
            'faltas':self.faltas
        }

class AlunoSchema(BaseModel):
    nome: str
    faltas: float
    
class AlunoUpdateSchema(BaseModel):
    nome: Optional[str]
    faltas: Optional[float]
    



@app.route('/')
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
