# -*- coding: utf-8 -*-
#Mathieu Baba
#Projet robotique Nao 
import time
import paramiko
import qi
import speech_recognition as sr
from naoqi import ALProxy
import random


ip_robot = "11.0.0.76" #ip du robot
port=9559 #port associé au Nao
nao_audio_file="/home/nao/recording.wav" #le fichier audio du Nao
local_audio_file= "./recording.wav" #le fichier audio en local sur la machine
nao_username="nao"
nao_password="udm2021"
fichier="Questions.txt"



#Fonction pour écouter les réponses des utilisateurs
def record_audio():
    audio_recorder= ALProxy("ALAudioRecorder", ip_robot, port)

    try:
        audio_recorder.stopMicrophonesRecording()  # Arrête tout enregistrement en cours
    except RuntimeError:
        pass  # Ignorer l'erreur si aucun enregistrement n'est actif

    print("Enregistrement de l'audio...")
    audio_recorder.startMicrophonesRecording(nao_audio_file, "wav", 16000, (0,0,1,0))
    time.sleep(5)
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
            text = recognizer.recognize_google(audio, language="fr-FR", show_all=False)  # Détection en français et on évite d'affiche les transcriptions de speech_recognition
            print("Tu as dit : " + text)
            return text
        except sr.UnknownValueError:
            print("Nao n'a pas compris.")
            return None
        except sr.RequestError:
            print("Erreur de connexion à Google Speech Recognition.")
            return None




#Fonction de présentation de Nao
def presentation():
    tts.say("Salut, je m'appele Nao, On va jouer au jeu du Qui-suis je")
    time.sleep(0.5)
    tts.say("Veux-tu que je texplique comment jouer au jeu ?")
    while(True) :
        record_audio()
        transfer_audio_file()
        reponse = speech_to_text()
        if "oui" in reponse or "ouais" in reponse:
            regles() 
            break
        elif "non" in reponse :
            break
        else :
            tts.say("je n'ai pas très bien compris, peux tu me répondre par oui ou par non ?")




# Fonction pour énoncer les règles du jeu
def regles():
    tts.say("Voici les règles du jeu, je vais décrire plusieurs animaux marins et tu devras deviner lequel c'est. Tu auras trois chances pour répondre correctement. Si tu réponds bien tu auras un point, si tu réponds faux, tu ne gagnes aucun point")
    time.sleep(0.5)
    tts.say("As-tu compris ?")
    record_audio()
    transfer_audio_file()
    reponse = speech_to_text()
    if "non" in reponse:
        return 
    else :
        tts.say("Alors je vais reformuler, tu devras deviner l'animal que je vais décrire. Mais attention tu n'as que 3 chances seulement de répondre juste. Tu as un point si tu as la bonne réponse et pas de points si tu réponds pas bien")




#Fonction de validation des réponses
def verification(mot, pts):
    tentative=3
    while(tentative>0):
        record_audio()
        transfer_audio_file()
        reponse = speech_to_text()
        if reponse is None:
            tts.say("Je n'ai pas très bien compris, redis moi")
            continue
        if mot in reponse :
            tts.say("Bonne réponse, tu gagnes 1 points")
            pts+=1
            return pts
        else:
            tentative-=1
            if(tentative>0):
                tts.say("C'est pas la bonne réponse! Allez tu as encore {} tentatives.".format(tentative))
            else:
                tts.say("Oups, c'est dommage, c'était {} la réponse".format(mot))
    return pts



#Fonction pour parcourir un fichier texte avec les informations sur les questions et la réponse associée
def get_question_reponse(fichier, numero_question):
    numero_question = str(numero_question)

    with open(fichier, "r") as file:
        lignes = file.readlines()  # Lire toutes les lignes du fichier
    
    question = None
    reponse = None
    question_en_cours = []  # Liste pour accumuler les lignes de la question

    for i, ligne in enumerate(lignes):
        if ligne.strip().startswith(numero_question):  # Vérifie si la ligne commence par le numéro
            question_en_cours.append(ligne.split(";")[1].strip())  # Ajoute la ligne de la question
            # Continue à ajouter les lignes suivantes tant que ce n'est pas une réponse
            j = i + 1
            while j < len(lignes) and "Réponse" not in lignes[j]:
                question_en_cours.append(lignes[j].strip())
                j += 1
            question = " ".join(question_en_cours)  # Fusionne toutes les lignes de la question

            if j < len(lignes) and "Réponse" in lignes[j]:
                reponse = lignes[j].split(":")[1].strip()  # Prend la réponse suivante
            break
    

    return question, reponse




#Programme principal

#Connexion au Nao
session=qi.Session()

try :
    session.connect("tcp://{}:{}".format(ip_robot, port))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot")

tts = session.service("ALTextToSpeech")
tts.setLanguage("French")

pts=0


presentation()


nombreAleatoire=[]
nombreAleatoire = random.sample(range(1, 11), 5) #On stocke une liste de nombre aléatoire


for nombre in nombreAleatoire:
    question, reponse = get_question_reponse(fichier, nombre)
    tts.say(question)
    pts=verification(reponse, pts)


tts.say("Tu as donc {} points sur 5.".format(pts))

session.close()
print("Connexion fermée")