#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import telegram
import urllib
import random
import foto
import os
import sys



'''
brief: Método principal donde se crea el bot
'''
class probot:
    def __init__ (self):
        #Variable glbal que mantiene al bot actualizado en el último chat
        self.LAST_UPDATE_ID = None
        #Variable login para hacer debug
        logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.num_camaras = len(sys.argv) - 1
        #Lista que será el teclado

        self.nombre_camaras = {}
        for n_cam in range(0, self.num_camaras):
            self.nombre_camaras[n_cam] = sys.argv[n_cam + 1]
        self.nombre_camaras[self.num_camaras] = telegram.Emoji.WARNING_SIGN + " Cancelar " + telegram.Emoji.WARNING_SIGN

        self.teclado_foto = list()
        for n_cam in range(0, self.num_camaras + 1):
            self.teclado_foto.append(list())
            self.teclado_foto[n_cam].append(self.nombre_camaras[n_cam])
        self.comandos = {"/start": 0, "/foto": 1, "/ayuda": 2, "/habla": 3,}
        self.main()

    def main(self):
        token = open("token", "r")
        #Se crea el bot con el token que se encuentra en el archivo token
        self.bot = telegram.Bot(token.read().rstrip('\n'))
        try:
            print self.bot.getMe()
            self.LAST_UPDATE_ID = self.bot.getUpdates()[-1].update_id
        except IndexError:
            self.LAST_UPDATE_ID = None

        while True:
            self.echo()
            #try:
            #    self.echo()
            #except TelegramError("Timed out"):
            #    self.echo()

    '''
    brief: Método que se encarga de analizar los últimos mensajes que llegan al bot
    '''
    def echo(self):
        cola_foto = open("cola_fotos", "a+")
        cola_audio = open("cola_audio", "a+")
        # Se hacen las peticiones de actualizaciones a partir del último update
        for update in self.bot.getUpdates(offset=self.LAST_UPDATE_ID, timeout=10):
            #Se buscan entre todas las actualizaciones y se procesa cada mensaje
            message = update.message.text.encode('utf-8')
            if (message):
                ej_comando     = False
                alias          = update.message.from_user.username
                nombre_usuario = update.message.from_user.first_name
                chat_id        = update.message.chat_id

                print nombre_usuario.encode('utf-8') + " (" + alias.encode('utf-8') + "): " + message.decode('utf-8')

                if(str(chat_id) + "\n" in cola_foto):
                    self.enviarFoto(update)
                elif(str(chat_id) + "\n" in cola_audio):
                    self.habla(message, chat_id)
                else:
                    for comando in self.comandos.keys():
                        if comando in message and not ej_comando:
                            self.ejecutarComando(self.comandos[comando], update)
                            ej_comando = True

                    if(not(ej_comando)):
                        self.enviarMensaje(update, self.ed(message))

                # Se actualiza el último update
                self.LAST_UPDATE_ID = update.update_id + 1
        cola_foto.close()
    '''
    brief: Método que envia mensaje de inicio
    param: bot:        bot que esta en funcionamiento
           update:     actualización que llamo el comando
    '''
    def inicio(self, update):
        chat_id = update.message.chat_id
        nombre = update.message.from_user.username
        self.enviarMensaje(update, "Hola @" + nombre + ", @keeeevin es mi padre")
        self.enviarMensaje(update, "Soy un bot de control de acceso del laboratorio de prototipos, pero también podemos charlar")
    '''
    brief: Método que envia foto de la cámara n-ésima
    param: update:     actualización que llamo el comando
    '''
    def peticionFoto(self, update):
        #Número de cámaras conectadas al bot
        message = update.message.text.encode('utf-8')
        #camara  = message[len(message) - 1: len(message)]
        chat_id = update.message.chat_id
        mess_id = update.message.message_id

        reply_markup = telegram.ReplyKeyboardMarkup(self.teclado_foto, one_time_keyboard = True, selective = True)
        self.bot.sendMessage(chat_id=chat_id, text="Selecciona la cámara que quieres",reply_to_message_id=mess_id, reply_markup=reply_markup)
        cola_foto = open("cola_fotos", "a+")
        if(not(str(chat_id) + "\n" in cola_foto)):
            cola_foto.seek(2, 0)
            cola_foto.write(str(chat_id) + "\n")
        cola_foto.close()

    def enviarFoto(self, update):
        camara = "no"
        message = update.message.text.encode('utf-8')
        chat_id = update.message.chat_id
        nombre_usuario = update.message.from_user.first_name
        #camara  = message[len(message) - 1: len(message)]
        print "ID: ", chat_id
        print "Mensaje ", message
        for val, nombre in self.nombre_camaras.iteritems():
            if message == nombre:
                camara = val

        if type(camara) is int or camara.isdigit():
            if type(camara) is not int:
                camara = int(camara)
            if camara >= 0 and camara <= self.num_camaras - 1:
                self.enviarMensaje(update, "Tomaré la foto " + nombre_usuario.encode('utf-8') + ". Espera un momento")
                foto.toma(camara)
                #Se hace creer que el bot esta tomando una foto
                self.bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
                if(not(os.system("[ -f Foto.png ]"))):
                    self.bot.sendPhoto(chat_id=chat_id, photo=open('Foto.png', 'r'))
                else:
                    self.enviarMensaje(update, "Lo siento " + nombre_usuario.encode('utf-8') +" hubo un problema interno")
                self.borrarChatIdLista(chat_id, "cola_fotos")
            elif camara == self.num_camaras:
                self.enviarMensaje(update, "Vale. No tomaré ninguna foto")
                self.borrarChatIdLista(chat_id, "cola_fotos")
            else:
                self.enviarMensaje(update, "Lo siento " + nombre_usuario.encode('utf-8') +", no reconozco esa cámara")
        else:
            mess_id = update.message.message_id
            reply_markup = telegram.ReplyKeyboardMarkup(self.teclado_foto, one_time_keyboard = True, selective = True)
            self.bot.sendMessage(chat_id=chat_id, text="Esa cámara no existe, por favor, selecciona la cámara que quieres",reply_to_message_id=mess_id, reply_markup=reply_markup)
    '''
    brief: Método que borra un chat_id de la lista de ids que han solicitado fotos
    param: chat_id:     id del chat a sacar de la lista
    '''
    def borrarChatIdLista(self, chat_id, lista):
        #cola_fotos
        cola = open(lista, "r")
        ids = cola.readlines()
        cola.close()
        cola = open(lista, "w")
        for i_id in ids:
            if i_id != str(chat_id) + "\n":
                cola.write(i_id)
        cola.close()
    '''
    brief: Método que envia información sobre comandos y el bot
    param: update:     actualización que llamo el comando
    '''
    def ayuda(self, update):
        nombre_usuario = update.message.from_user.first_name
        self.enviarMensaje(update, "Hola " + nombre_usuario.encode('utf-8') + ", soy un bot de control de acceso del laboratorio de prototipos")
        self.enviarMensaje(update, "Por ahora tengo estos comandos: \n\
                                    /foto: Envio una foto de la cámara que selecciones\n\
                                    /habla: envio un mensaje de voz con la frase que envies\n\
                                    /ayuda: explico mis comandos y razón de ser")


    '''
    brief: Método que envia el texto que recibe despues de /habla
    param: update:     actualización que llamo el comando
    '''
    def peticionHabla(self, update):
        message        = update.message.text.encode('utf-8')
        chat_id        = update.message.chat_id
        nombre_usuario = update.message.from_user.first_name
        if("@lprotobot" in message):
            n          = len("@lprotobot/Habla")
        else:
            n          = len("/habla")
        print n
        texto          = message[n: len(message)]
        print "AQUIII"
        print texto
        if(len(texto) > 1):
            self.habla(texto, chat_id)
        else:
            self.enviarMensaje(update, "¿Qué quieres que diga " + nombre_usuario.encode('utf-8') + "?")
            cola_audio = open("cola_audio", "a+")
            if(not(str(chat_id) + "\n" in cola_audio)):
                cola_audio.seek(2, 0)
                cola_audio.write(str(chat_id) + "\n")
            cola_audio.close()

    def habla(self, texto, chat_id):
        os.system("rm audio.mp3")
        if("\"" not in texto and not(os.system("espeak -v es-la \"" + texto + "\" --stdout | ffmpeg -i - -ar 44100 -ac 2 -ab 192k -f mp3 audio.mp3"))):
            print "Enviaré audio con: " + texto
            self.bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_AUDIO)
            self.bot.sendVoice(chat_id=chat_id, voice=open('audio.mp3', 'r'))
        else:
            self.enviarMensaje(update, "No puedo decir eso " + nombre_usuario.encode('utf-8'))
        self.borrarChatIdLista(chat_id, "cola_audio")
    '''
    brief: Método que se encarga de ejecutar el comando dado por id_comando
    param: id_comando: id del comando que se ejecutara
           update:     actualización que llamo el comando
    '''
    def ejecutarComando(self, id_comando, update):
        if id_comando == 0:
            self.inicio(update)
        elif id_comando == 1:
            self.peticionFoto(update)
        elif id_comando == 2:
            self.ayuda(update)
        elif id_comando == 3:
            self.peticionHabla(update)
    '''
    brief: Método que envia una respuesta al update
    param: update:     actualización que llamo el comando
           respuesta:  respuesta a enviar
    '''
    def enviarMensaje(self, update, respuesta):
        chat_id = update.message.chat_id
        nombre_usuario = update.message.from_user.first_name
        alias          = update.message.from_user.username
        print "Protobot dice a " + nombre_usuario.encode('utf-8') + " (" + alias.encode('utf-8') + "): " + respuesta
        reply_markup = telegram.ReplyKeyboardHide(hide_keyboard = True)
        self.bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        self.bot.sendMessage(chat_id=chat_id, text=respuesta, reply_markup=reply_markup)

    '''
    brief: Método que retorna texto aleatorio al usuario
    param: text: texto que envia el usuario
    '''
    def ed(self, text):
        res = ["Si", "No", "Depende", "Gerardo desaparecio", "I'm sorry Dave, I'm afraid I can't do that", "robots", "Whatsapp sucks", "I am cool", "Kevin es cul", "Chabe vive", "Bate para Jesus"];
        data = res[random.randint(1, len(res) - 1)];

        return data.strip()
pbot = probot()
