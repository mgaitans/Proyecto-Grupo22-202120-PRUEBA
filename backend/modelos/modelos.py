from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from datetime import datetime
import enum


db = SQLAlchemy()

class Formato(enum.Enum):
    MP3 = 1
    ACC = 2
    OGG = 3
    WAV = 4
    WMA = 5

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), )
    contrasena = db.Column(db.String(32), nullable=False)

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    archivo = db.Column(db.String(512), nullable=False)
    formato = db.Column(db.Enum(Formato), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.today())
    estado = db.Column(db.String(15), default="UPLOADED", nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {"llave": value.name, "valor": value.value}

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

class TareaSchema(SQLAlchemyAutoSchema):
    formato = EnumADiccionario(attribute=("formato"))
    class Meta:
        model = Tarea
        include_relationships = True
        load_instance = True