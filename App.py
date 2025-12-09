import telebot
from telebot import types

TOKEN = '7969800787:AAEU1974A9AsWT-zznh2lVWel9fonaZAS-U'
bot = telebot.TeleBot(TOKEN)

PREGUNTAS = {
    1: ("¿Quien es el conyugue de Cesar?", 
        ["Gabriel", "Kennyth", "No tiene conyugue"], 
        "Kennyth"),
    2: ("¿Cómo se llama la librería de Telegram que estamos utilizando?", 
        ["Requests", "Flask", "pyTelegramBotAPI"], 
        "pyTelegramBotAPI"),
    3: ("¿En que lugar quedo la reina de la UTS?", 
        ["Reina de los estudiantes universitarios", "3era finalista", "1era finalista"], 
        "1era finalista")
}

# (pregunta actual, puntaje)
# {chat_id: {'puntaje': 0, 'pregunta_actual': 1}}
datos_usuario = {}


def crear_teclado_opciones(id_pregunta):
    marcado = types.InlineKeyboardMarkup()
    
    _, opciones, _ = PREGUNTAS[id_pregunta]
    
    boton1 = types.InlineKeyboardButton(
        text=opciones[0], 
        callback_data=f"P{id_pregunta}_R{opciones[0]}"
    )
    
    boton2 = types.InlineKeyboardButton(
        text=opciones[1], 
        callback_data=f"P{id_pregunta}_R{opciones[1]}"
    )
    
    boton3 = types.InlineKeyboardButton(
        text=opciones[2], 
        callback_data=f"P{id_pregunta}_R{opciones[2]}"
    )
    
    marcado.add(boton1)
    marcado.add(boton2)
    marcado.add(boton3)
        
    return marcado


@bot.message_handler(commands=['start', 'inicio'])
def enviar_bienvenida(mensaje):
    id_chat = mensaje.chat.id
    
    datos_usuario[id_chat] = {'puntaje': 0, 'pregunta_actual': 1}
    
    bot.send_message(id_chat, 
                     f"¡Hola {mensaje.from_user.first_name}!\n"
                     f"Bienvenido al **Quiz de Raul**.\n\n"
                     f"¡Usa los botones para responder!",
                     parse_mode="Markdown")
    
    enviar_pregunta(id_chat, datos_usuario[id_chat]['pregunta_actual'])


def enviar_pregunta(id_chat, id_pregunta):
    
    if id_pregunta not in PREGUNTAS:
        puntaje_final = datos_usuario[id_chat]['puntaje']
        total_preguntas = len(PREGUNTAS)
        
        bot.send_message(id_chat, 
                         f"🎉 **¡Fin del Quiz de Raul!** 🎉\n"
                         f"Tu puntaje final es: **{puntaje_final} / {total_preguntas}**.\n\n"
                         f"Puedes empezar de nuevo con /start",
                         parse_mode="Markdown")
        del datos_usuario[id_chat]
        return

    texto_pregunta, _, _ = PREGUNTAS[id_pregunta]
    
    teclado = crear_teclado_opciones(id_pregunta)
    
    bot.send_message(id_chat, 
                     f"**Pregunta {id_pregunta}:**\n{texto_pregunta}", 
                     reply_markup=teclado,
                     parse_mode="Markdown")



@bot.callback_query_handler(func=lambda llamada: True)
def manejador_callback(llamada):
    id_chat = llamada.message.chat.id
    
    if id_chat not in datos_usuario:
        bot.send_message(id_chat, "Por favor, usa /start para comenzar el quiz.")
        return
        
    try:
        datos_callback = llamada.data.split('_')
        id_pregunta_actual = int(datos_callback[0][1:])  # Obtiene el número de pregunta (ej: 1)
        respuesta_usuario = datos_callback[1][1:]        # Obtiene el texto de la respuesta (ej: 'Python')

        _, _, respuesta_correcta = PREGUNTAS[id_pregunta_actual]
        
        es_correcto = (respuesta_usuario == respuesta_correcta)
        
        if es_correcto:
            datos_usuario[id_chat]['puntaje'] += 1
        
        
        mensaje_feedback = f"✅ **¡Correcto!**" if es_correcto else f"❌ **Incorrecto.** La respuesta era: **{respuesta_correcta}**"
        
        texto_pregunta_original = PREGUNTAS[id_pregunta_actual][0]
        
        bot.edit_message_text(chat_id=id_chat, 
                              message_id=llamada.message.message_id, 
                              text=f"**Pregunta {id_pregunta_actual}:**\n{texto_pregunta_original}\n\n"
                                   f"Tu respuesta elegida: **{respuesta_usuario}**\n"
                                   f"{mensaje_feedback}",
                              parse_mode="Markdown")
        
        siguiente_id = id_pregunta_actual + 1
        datos_usuario[id_chat]['pregunta_actual'] = siguiente_id
        
        enviar_pregunta(id_chat, siguiente_id)

    except Exception as e:
        print(f"Error procesando callback: {e}")
        bot.send_message(id_chat, "Ocurrió un error al procesar tu respuesta.")


print("Bot de Quiz inicializado y corriendo...")
bot.infinity_polling()