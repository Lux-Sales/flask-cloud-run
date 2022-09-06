from sqlalchemy import Column, Integer, String

from ._default_model import DefaultModel
from ._extensions import db


class Materia(DefaultModel, db.Model):
    __tablename__ = "materia"

    id = Column(Integer, primary_key=True)

    nome = Column(String(50))

    docente = Column(String(50))

    @property
    def serialized(self):
        return {"id": self.id, "nome": self.nome, "docente": self.docente}
