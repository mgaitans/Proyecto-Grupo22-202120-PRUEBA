from celery import Celery
import subprocess
import requests

celery_app = Celery(__name__, broker='redis://localhost:6379/0')

@celery_app.task(name='convertir_cancion')
def convertir_cancion(id_task,nombre, formato, formatonew):
    print(id_task, nombre, formato, formatonew)
    UPLOAD_FOLDER = './backend/files/uploaded/'
    PROCESSED_FOLDER = './backend/files/processed/'
    respuesta = subprocess.call(['ffmpeg', '-i',UPLOAD_FOLDER+nombre+'.'+formato , PROCESSED_FOLDER+nombre+'.'+formatonew ])
    print(respuesta)
    requests.post('http://172.23.66.131:5000/finConversion',json={'id_task': id_task})
    return {"mensaje":"Convertido"}
    


