from celery import Celery
import subprocess
import requests
import smtplib 
celery_app = Celery(__name__, broker='redis://localhost:6379/0')

@celery_app.task(name='convertir_cancion')
def convertir_cancion(id_task,nombre, formato, formatonew,correo):
    print(id_task, nombre, formato, formatonew)
    UPLOAD_FOLDER = './backend/files/uploaded/'
    PROCESSED_FOLDER = './backend/files/processed/'
    respuesta = subprocess.call(['ffmpeg', '-i',UPLOAD_FOLDER+nombre+'.'+formato , PROCESSED_FOLDER+nombre+'.'+formatonew ])
    print(respuesta)
    enviar_mail(correo)
    requests.post('http://172.23.66.131:5000/finConversion',json={'id_task': id_task})
    return {"mensaje":"Convertido"}
    


@celery_app.task(name='enviar_mail')
def enviar_mail(correo):
    message = 'Su archivo se ha covertido!'
    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login("pintoandres2014a@gmail.com", "Andres1193")
    server.sendmail("pintoandres2014a@gmail.com",correo,message)
    return {"mensaje":"Email enviado"}