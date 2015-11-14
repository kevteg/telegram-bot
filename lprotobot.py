#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import telegram
import urllib
import random
import foto
import os

LAST_UPDATE_ID = None

'''
brief: Método principal donde se crea el bot
'''

def main():
    #Variable glbal que mantiene al bot actualizado en el último chat
    global LAST_UPDATE_ID

    #Variable login para hacer debug
    logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    token = open("token", "r")
    #Se crea el bot con el token que se encuentra en el archivo token
    bot = telegram.Bot(token.read().rstrip('\n'))

    try:
        print bot.getMe()
        LAST_UPDATE_ID = bot.getUpdates()[-1].update_id
    except IndexError:
        LAST_UPDATE_ID = None

    while True:
        echo(bot)

'''
brief: Método que se encarga de analizar los últimos mensajes que llegan al bot
param: bot: bot recién creado con el token
'''
def echo(bot):
    global LAST_UPDATE_ID
    comandos = {"/start": 0, "/foto": 1, "/help": 2, "/habla": 3,}

    # Se hacen las peticiones de actualizaciones a partir del último update
    for update in bot.getUpdates(offset=LAST_UPDATE_ID, timeout=10):
        #Se buscan entre todas las actualizaciones y se procesa cada mensaje
        message = update.message.text.encode('utf-8')
        if (message):
            ej_comando     = False
            alias          = update.message.from_user.username
            nombre_usuario = update.message.from_user.first_name
            print nombre_usuario + " (" + alias + "): " + message.decode('utf-8')

            for comando in comandos.keys():
                if comando in message and not ej_comando:
                    ejecutarComando(comandos[comando], bot, update)
                    ej_comando = True

            if(not(ej_comando)):
                enviarMensaje(bot, update, ed(message))

            # Se actualiza el último update
            LAST_UPDATE_ID = update.update_id + 1
'''
brief: Método que envia mensaje de inicio
param: bot:        bot que esta en funcionamiento
       update:     actualización que llamo el comando
'''
def inicio(bot, update):
    chat_id = update.message.chat_id
    nombre = update.message.from_user.username
    enviarMensaje(bot, update, "Hola @" + nombre + ", @keeeevin es mi padre")
    enviarMensaje(bot, update, "Soy un bot de control de acceso del laboratorio de prototipos, pero también podemos charlar")
'''
brief: Método que envia foto de la cámara n-ésima
param: bot:        bot que esta en funcionamiento
       update:     actualización que llamo el comando
'''
def tomarFoto(bot, update):
    num_camaras = 2
    message = update.message.text.encode('utf-8')
    camara  = message[len(message) - 1: len(message)]
    chat_id = update.message.chat_id
    nombre_usuario = update.message.from_user.first_name
    if camara.isdigit():
        camara = int(camara)
        if camara >= 0 and camara <= num_camaras - 1:
            enviarMensaje(bot, update, "Tomaré la foto " + nombre_usuario.encode('utf-8') +". Espera un momento")
            foto.toma(camara)
            #Se hace creer que el bot esta tomando una foto
            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
            if(not(os.system("[ -f Foto.png ]"))):
                bot.sendPhoto(chat_id=chat_id, photo=open('Foto.png', 'r'))
        else:
            enviarMensaje(bot, update, "Lo siento " + nombre_usuario.encode('utf-8') +", no reconozco ese número de cámara")
    else:
        enviarMensaje(bot, update, "Lo siento " + nombre_usuario.encode('utf-8') + ", no ha enviado número de cámara")
'''
brief: Método que envia información sobre comandos y el bot
param: bot:        bot que esta en funcionamiento
       update:     actualización que llamo el comando
'''
def ayuda(bot, update):
    nombre_usuario = update.message.from_user.first_name
    enviarMensaje(bot, update, "Hola " + nombre_usuario.encode('utf-8') + ", soy un bot de control de acceso del laboratorio de prototipos")
    enviarMensaje(bot, update, "Por ahora tengo estos comandos: \n\
                                /foto n: Envio una foto de la cámara n-ésima de la computadora donde me encuentre\n\
                                /habla frase: envio un mensaje de voz con la frase que envies\n\
                                /ayuda: explico mis comandos y razón de ser")


'''
brief: Método que envia el texto que recibe despues de /habla
param: bot:        bot que esta en funcionamiento
       update:     actualización que llamo el comando
'''
def habla(bot, update):
    message        = update.message.text.encode('utf-8')
    chat_id        = update.message.chat_id
    nombre_usuario = update.message.from_user.first_name
    texto          = message[6: len(message)]

    if(len(texto) > 1):
        print texto
        os.system("rm audio.mp3")
        if("\"" not in texto and not(os.system("espeak -v es-la \"" + texto + "\" --stdout | ffmpeg -i - -ar 44100 -ac 2 -ab 192k -f mp3 audio.mp3"))):
            bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_AUDIO)
            bot.sendVoice(chat_id=chat_id, voice=open('audio.mp3', 'r'))
        else:
            enviarMensaje(bot, update, "No puedo decir eso " + nombre_usuario.encode('utf-8'))
    else:
        enviarMensaje(bot, update, "Disculpe " + nombre_usuario.encode('utf-8') + ", debe enviar algo que yo pueda decir "+telegram.Emoji.DISAPPOINTED_FACE)

'''
brief: Método que se encarga de ejecutar el comando dado por id_comando
param: ic_comando: id del comando que se ejecutara
       bot:        bot que esta en funcionamiento
       update:     actualización que llamo el comando
'''
def ejecutarComando(id_comando, bot, update):
    if id_comando == 0:
        inicio(bot, update)
    elif id_comando == 1:
        tomarFoto(bot, update)
    elif id_comando == 2:
        ayuda(bot, update)
    elif id_comando == 3:
        habla(bot, update)
'''
brief: Método que envia una respuesta al update
param: bot:        bot que esta en funcionamiento
       update:     actualización que llamo el comando
       respuesta:  respuesta a enviar
'''
def enviarMensaje(bot, update, respuesta):
    chat_id = update.message.chat_id
    nombre_usuario = update.message.from_user.first_name
    print "Protobot dice a " + nombre_usuario+ ": " + respuesta
    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    bot.sendMessage(chat_id=chat_id, text=respuesta)

'''
brief: Método que retorna texto aleatorio al usuario
param: text: texto que envia el usuario
'''
def ed(text):
    res = ["Si", "No", "Depende", "Gerardo desaparecio", "I'm sorry Dave, I'm afraid I can't do that", "robots", "Whatsapp sucks", "I am cool", "Kevin es cul", "Chabe vive", "Bate para Jesus"];
    data = res[random.randint(1, len(res) - 1)];

    return data.strip()

if __name__ == '__main__':
    main()
