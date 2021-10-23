import os, pathlib, random
from operator import contains
from flask import request, send_from_directory
from ..modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime
from werkzeug.utils import secure_filename 
import subprocess
import shutil
import os

usuario_schema = UsuarioSchema()
tarea_schema = TareaSchema()
 
# end point: /api/tasks
class VistaTareas(Resource):
    def post(self):
        usuario_id = 1
        # Carpeta de subida    
        UPLOAD_FOLDER = '../backend/files/uploaded/'
        # obtenemos el archivo del input "fileName" de postman 
        f = request.files['fileName'] 
        
        filename = secure_filename(f.filename)
        nombre_archivo = filename.split(".")
        nombre = nombre_archivo[len(nombre_archivo)-2]+'_'+str(usuario_id)
        formatoant = (nombre_archivo[len(nombre_archivo)-1]).upper()
        print(filename)
        path = pathlib.Path(UPLOAD_FOLDER + filename)
        # obtenemos el input "fileName" de postman con el Formato al que desea cambiar el archivo cargado
        
        formato = request.form["newFormat"]
        
        #Si entrada está vacio, se ejecuta el if
        if not f:
            return {"mensaje":"INGRESE ARCHIVO A CONVERTIR"}
        elif not formato:
            return {"mensaje":"INGRESE FORMATO A CONVERTIR EL ARCHIVO"}
        else:         
            
            # Guardamos el archivo en el directorio "UPLOAD_FOLDER"
            f.save(os.path.join(UPLOAD_FOLDER, nombre+'.'+formatoant))
            
            # Retornamos una respuesta satisfactoria
            
            Filename = path.name
            
            nueva_tarea = Tarea(
            archivo = Filename,
            formato = formatoant,
            fecha = datetime.today(),
            estado = "UPLOADED",
            usuario_id = usuario_id)            
            db.session.add(nueva_tarea)
            db.session.commit()
            token_de_acceso = create_access_token(identity = usuario_id)

            return {"mensaje":"La tarea fue creada exitosamente", "token":token_de_acceso}


    
             
# end point: /api/tasks/<int:id_task>
class VistaTarea(Resource):
    def get(self, id_task):
        exit_tarea = Tarea.query.filter(Tarea.id == id_task).first()
        db.session.commit()
        if exit_tarea is None:
            return {"mensaje":"La tarea no existe, no se puede consultar"}
        else:
            return tarea_schema.dump(Tarea.query.get_or_404(id_task))

    def put(self, id_task):
        task_download = Tarea.query.get_or_404(id_task)
        UPLOAD_FOLDER = '../backend/files/uploaded/'
        PROCESSED_FOLDER = '../backend/files/processed/'
        formato = request.form["newFormat"]
        #Si entrada está vacio, se ejecuta el if
        if not formato:
            return {"mensaje":"INGRESE FORMATO A CONVERTIR EL ARCHIVO"}
        else:    
            if task_download.formatonew != formato:
                print(task_download.formatonew.name)
                if task_download.estado == 'PROCESSED':
                    os.remove(os.path.join(PROCESSED_FOLDER, task_download.nombre+'.'+task_download.formatonew.name))
                task_download.formatonew = formato
                task_download.estado = 'UPLOADED'
                task_download.fecha = datetime.today()
                db.session.commit()
            return {"mensaje":"La tarea fue actualizada exitosamente"}

class VistaDescarga(Resource):
    def get(self, id_task, tipo_task):
        print('holaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        task_download = Tarea.query.filter(Tarea.id == id_task).first()
        if task_download is None:
            return {"mensaje":"La tarea no existe!"},401
        if tipo_task == 2:
            if task_download.estado == 'PROCESSED':
                return send_from_directory(directory='files/processed', filename=task_download.nombre+'.'+task_download.formatonew.name, as_attachment=True)
            else:
                return {"mensaje":"El archivo aun no se ha procesado!"},401

        elif tipo_task == 1:
            return send_from_directory(directory='files/uploaded', filename=task_download.nombre+'.'+task_download.formato.name, as_attachment=True)
        else:
            return {"mensaje":"El tipo de archivo que quiere descargar no existe!"},500      

    def post(self, id_task):
        usuario_id = 1
        # Carpeta de subida    
        UPLOAD_FOLDER = 'files\\uploaded'
        DOWNLOAD_FOLDER = 'files\\download'

        f = request.files['fileName'] 
        
        filename = secure_filename(f.filename)
        path = pathlib.Path(UPLOAD_FOLDER + filename)
        formato = request.form["newFormat"]
        

        if not f:
            return {"mensaje":"INGRESE ARCHIVO A CONVERTIR"}
        elif not formato:
            return {"mensaje":"INGRESE FORMATO A CONVERTIR EL ARCHIVO"}
        else:
            FFMPEG_BIN = "ffmpeg.exe"   
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            dfile = '{}.{}'.format(os.path.splitext(filename)[0], str(format)) 
            inputF = os.path.join(UPLOAD_FOLDER, filename)
            outputF = os.path.join(DOWNLOAD_FOLDER, dfile)
            convertCMD = [FFMPEG_BIN, '-y', '-i', inputF, outputF]
            executeOrder66 = subprocess.Popen(convertCMD)
            print('pasa')
            return {"mensaje":"La tarea fue creada exitosamente"}
# endpoint /api/auth/signup
class VistaSignUp(Resource):

    def post(Self):
        user_exist = Usuario.query.filter(Usuario.usuario == request.json["email"]).all()
        if len(user_exist) > 0:
            return{"mensaje":"El usuario ya existe.","estado":0}, 400
        new_user = Usuario(usuario=request.json["nombre"],email=request.json["email"],contrasena=request.json["contrasena"])
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity = new_user.id)
        return {"mensaje":"Usuario creado exitosamente", "estado":1, "token":access_token}, 200

class VistaUser(Resource):

    def get(self, id_usuario):
        return usuario_schema.dump(Usuario.query.get_or_404(id_usuario))

# endpoint /api/auth/login
class VistaLogIn(Resource):
    def post(self):
        user = Usuario.query.filter(Usuario.usuario == request.json["email"], Usuario.contrasena == request.json["contrasena"]).first()
        db.session.commit()
        if user is None:
            return {"mensaje":"El usuario no existe"}, 404
        else:
            access_token = create_access_token(identity = user.id)
            return {"mensaje":"Inicio de sesión exitoso", "token":access_token}




