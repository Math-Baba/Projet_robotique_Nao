# -*- coding: utf-8 -*-
#Mathieu Baba
#Fichier test de programme
import time
import paramiko
import qi
import speech_recognition as sr
from naoqi import ALProxy


ip_robot = "11.0.0.76" #ip du robot
port=9559
nao_audio_file="/home/nao/recording.wav"
local_audio_file= "./recording.wav"
nao_username="nao"
nao_password="udm2021"


#Fonction pour écouter les réponses des utilisateurs
def record_audio():
    audio_recorder= ALProxy("ALAudioRecorder", ip_robot, port)

    print("Enregistrement de l'audio...")
    audio_recorder.startMicrophonesRecording(nao_audio_file, "wav", 16000, (0,0,1,0))
    time.sleep(8)
    audio_recorder.stopMicrophonesRecording()
    print("Fin de l'enregistrement")

#Fonction pour transférer le fichier audio localement
def transfer_audio_file():
    print("Transfert du fichier de Nao à la machine local...")

    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_robot, username=nao_username, password=nao_password)

    scp=paramiko.SFTPClient.from_transport(ssh.get_transport())
    scp.get(nao_audio_file, local_audio_file)
    scp.close()
    print("Transfert complété")




#Fonction pour convertir l'audio en texte
def speech_to_text():
    recognizer = sr.Recognizer()

    # Charger le fichier audio enregistré par Nao
    with sr.AudioFile(local_audio_file) as source:
        print("Analyse de l'audio...")
        recognizer.adjust_for_ambient_noise(source)  # Ajuste au bruit
        try:
            audio = recognizer.record(source)  # Récupère tout l'audio
            text = recognizer.recognize_google(audio, language="fr-FR")  # Détection en français
            print("Tu as dit : " + text)
            return text
        except sr.UnknownValueError:
            print("Nao n'a pas compris.")
            return None
        except sr.RequestError:
            print("Erreur de connexion à Google Speech Recognition.")
            return None



#Fonction main
session=qi.Session()

try :
    session.connect("tcp://{}:{}".format(ip_robot, port))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot")

tts = session.service("ALTextToSpeech")
tts.setLanguage("French")

tts.say("Salut ça va ?")
record_audio()
transfer_audio_file()
speech_to_text()