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
port=9559
nao_audio_file="/home/nao/recording.wav"
local_audio_file= "./recording.wav"
nao_username="nao"
nao_password="udm2021"

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
    time.sleep(2)
    tts.say("Veux-tu que je texplique comment jouer au jeu ?")
    record_audio()
    transfer_audio_file()
    reponse = speech_to_text()
    if "oui" in reponse or "ouais" in reponse:
        regles() 
    else :
        return




# Fonction pour énoncer les règles du jeu
def regles():
    tts.say("Voici les règles du jeu, je vais décrire plusieurs animaux marins et tu devras deviner lequel c'est. Tu auras trois chances pour répondre correctement. Si tu réponds bien tu auras un point, si tu réponds faux, tu ne gagnes aucun point")
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

mot =["dauphin", "baleine", "tortue de mer", "murène", "poisson-perroquet", "poisson-clown", "crabe", "raie", "pieuvre", "requin"]

nombreAleatoire=[]
nombreAleatoire = random.sample(range(5), 5) #On stocke une liste de nombre aléatoire

#dictionnaire des choix
choix = {
        0: lambda: (tts.say("Question, je suis un mammifère marin, intelligent et qui aiment sauter hors de l'eau. Je me trouve assez souvent à Tamarin. Qui suis je ?"), verification(mot[0], pts)),#utilisation de lambda pour exécuter une fonction après la prise de parole

        1: lambda: (tts.say("Question, Je suis un gigantesque mammifère marin et je peux être aussi long que les bus de port louis. Je me trouve assez souvent à Tamarin. Qui suis je ?"), verification(mot[1], pts)),

        2: lambda: (tts.say("Question, j'ai une grosse carapace dur sur le dos pour me protéger dans l'océan. Je suis de couleur verte et mes pattes ressemblent à des nageoires de poisson. Je vis généralement à îles aux cerfs. Qui suis je ?"), verification(mot[2], pts)),

        3: lambda: (tts.say("Question, Je suis un prédateur qui ressemble à un serpent. J'aime me cacher en dessous des rochers mais j'en sors seulement pour chasser des poissons. Je vis généralement soit à Tamarin soit à Blue Bay. Qui suis je ?"), verification(mot[3], pts)),

        4: lambda: (tts.say("Question, Je suis un poisson coloré qui ressemble un peu à un perroquet à cause de ma bouche en forme de bec. Je me trouve auprès des récifs coraliens de flic en flac et îles aux cerfs. Qui suis je ?"), verification(mot[4], pts)),

        5: lambda: (tts.say("Question, Je suis un petit poisson coloré à rayures blanches qui aime bien me cacher dans des anémones de mer. Je suis souvent comparé à Nemo. Je vis aux alentours des coraux de Blue bay Qui suis je ?"), verification(mot[5], pts)),

        6: lambda: (tts.say("Question, J'ai une carapace tout le long de mon corps, j'ai des pinces qui me servent à attraper ma nourriture et me défendre. Je vis généralement dans un trou sur une plage. Qui suis je ?"), verification(mot[6], pts)),

        7: lambda: (tts.say("Question, Je suis un poisson marin avec un corps plat, en forme d'aile. J'aime me poser sur le sable au fond de l'eau. Je vis particulièrement au sud de l'île entre Le morne et Bel Ombre. Qui suis je ?"), verification(mot[7], pts)),

        8: lambda: (tts.say("Question, Je suis un animal intelligent avec un corps mou et une tête ronde. J'ai huit bras longs qui ressemblent à des tentacules. Je peux aussi changer de couleur pour me camoufler des prédateurs. Je vis un peu partout autour de l'île. Qui suis je ?"), verification(mot[8], pts)),

        9: lambda: (tts.say("Question, Je suis un prédateur avec une nageoire sur mon dos qui fait peur. Je possède une rangée de dents pointues. Mais pas d'inquiétude, je ne suis pas très souvent présent à Maurice. Qui suis je ?"), verification(mot[9], pts)),
}

#Pour chaque nombre aléatoire générer dans la liste, on exécute la question correspondante
for nombre in nombreAleatoire:
    pts=choix.get(nombre, lambda: print("Choix invalide"))() #On stocke ensuite le nombre de points dans pts



tts.say("Tu as donc {} points sur 5.".format(pts))

session.close()
print("Connexion fermée")