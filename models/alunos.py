from sqlalchemy import Column, Integer, String

from ._default_model import DefaultModel
from ._extensions import db


class Aluno(DefaultModel, db.Model):
    __tablename__ = "aluno"

    id = Column(Integer, primary_key=True)

    nome = Column(String(20))

    faltas = Column(Integer)

    @property
    def serialized(self):
        return {"id": self.id, "nome": self.nome, "faltas": self.faltas}
