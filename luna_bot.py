from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, date, timedelta
import os
import random

app = Flask(__name__)

# Base de datos en memoria
users = {}

# ============================================================
# HUMOR
# ============================================================

humor = {
    "menstruacion": [
        "Hoy el cuerpo pide tres cosas: silencio, cobija y que nadie quiera nada. 🛋️",
        "Si hoy quieres cancelar todos los planes — quizás no es pereza. Es sabiduría.",
        "El mejor deporte de hoy: llegar a la cocina y volver. Cuenta.",
        "Hoy tu superpoder es no hacer nada sin culpa. Úsalo bien.",
        "Vela + té + cobija = programa completo de desarrollo personal. 🕯️",
    ],
    "folicular": [
        "El cerebro volvió a funcionar. Como una computadora después de actualizar. 💻",
        "La energía regresa. Todavía con cuidado, pero ya con curiosidad.",
        "El humor hoy es como el de alguien que encontró el cargador del teléfono. 🔋",
        "Hoy es buen día para ideas. Aunque la mitad sean un poco locas.",
        "El mundo vuelve a verse como un lugar donde se puede inventar algo.",
    ],
    "ovulacion": [
        "Hoy hay posibilidades de sentirte como la protagonista de una película. 🎬",
        "Hoy la gente de repente parece más agradable que de costumbre.",
        "Si hoy quieres vestirte bonito — no es casualidad. Son las hormonas. ✨",
        "Hoy la carisma funciona sin esfuerzo extra. Aprovéchalo.",
        "Si hoy quieres coquetear con la vida — es simplemente el verano de tu ciclo. ☀️",
    ],
    "lutea": [
        "Hoy el cerebro puede notar todo: el vaso sucio, la vieja conversación y la imperfección del universo. 🍂",
        "Si hoy la paciencia se acaba más rápido — son las hormonas probando los límites.",
        "Hoy puede llegar el deseo de orden, chocolate y un poco de soledad. Todo al mismo tiempo.",
        "Si hoy quieres cancelar a media humanidad — es parte normal de la revisión otoñal.",
        "Hoy el alma dice: vamos a ser honestas. 🌙",
        "Si hoy quieres despedir a todo el mundo — quizás es solo la fase lútea hablando.",
    ]
}

wisdom = [
    "La energía femenina no tiene que ser igual todos los días. La ciclicidad no es debilidad — es navegación. 🌙",
    "No todas las emociones son verdad. Algunas son solo hormonas. Y eso también está bien.",
    "Durante la ovulación las mujeres toman decisiones más valientes. No es coincidencia.",
    "El ciclo no es un problema a resolver. Es un mapa para vivir.",
    "Tu cuerpo no está roto. Está cíclico. Hay diferencia.",
    "Descansar en invierno no es perder el tiempo. Es prepararse para la primavera.",
    "La intuición habla más fuerte en los días de menstruación. Vale la pena escucharla.",
    "Cada fase tiene su inteligencia. Ninguna es mejor que otra.",
    "El ciclo te enseña que no tienes que ser la misma todos los días para ser suficiente.",
]

checkin_responses = {
    "tranquila": "Qué bien 🌤 La calma también es energía. Aprovecha esta claridad de hoy.",
    "irritación": "La irritación tiene sentido en esta fase 🔥 Respira. No tienes que reaccionar a todo.",
    "irritacion": "La irritación tiene sentido en esta fase 🔥 Respira. No tienes que reaccionar a todo.",
    "tristeza": "La tristeza es válida 😔 No tienes que arreglarla. Solo permitirte sentirla.",
    "cansancio": "El cansancio en esta fase es biológico, no personal 😵 Descansa sin culpa.",
    "inspiración": "¡Aprovecha esa inspiración! ✨ Anota todo — en esta fase las ideas tienen calidad.",
    "inspiracion": "¡Aprovecha esa inspiración! ✨ Anota todo — en esta fase las ideas tienen calidad.",
    "amor": "Qué hermoso sentirse así 💖 Comparte esa energía con las personas que quieres.",
    "apatía": "La apatía también es información 😶 Tu energía está guardada para algo. No te fuerces hoy.",
    "apatia": "La apatía también es información 😶 Tu energía está guardada para algo. No te fuerces hoy.",
}

phases = [
    {
        "key": "menstruacion",
        "name": "Menstruación",
        "season": "Invierno interior",
        "emoji": "🌑",
        "days": (1, 5),
        "morning_options": [
            "Hoy ve despacio, amor. Tu cuerpo hace un trabajo sagrado 🌑\nNo tienes que demostrar nada hoy.",
            "Buenos días 🌑 Estás en tu invierno interior.\nEl descanso de hoy es productivo. En serio.",
            "Hola 🌑 Hoy el cuerpo manda. Escúchalo.\nNo es debilidad — es inteligencia.",
        ],
        "body": "Tu cuerpo libera lo que ya no necesita. No es debilidad — es la fase más poderosa del ciclo. El útero trabaja, el sistema nervioso pide quietud.",
        "emotions": "🌊 Las emociones fluyen sin filtros\n🔮 La intuición habla más fuerte\n🕯️ Querer estar sola es una necesidad, no un problema\n💫 Las revelaciones llegan en silencio",
        "warning": "⚠️ Si ahora sientes que todo está mal — no lo cambies. Espera 5 días. No es la realidad, son las hormonas.",
        "work": "🧠 Evita decisiones importantes hoy. Si algo parece una catástrofe — escríbelo y vuelve en 5 días.",
        "relations": "💑 No te expliques demasiado. Solo di 'necesito estar sola'. Evita conversaciones difíciles estos días.",
        "selfesteem": "👑 Tu autoestima puede sentirse más baja ahora — es hormonal, no real.",
        "ritual": "🕯️ Acuéstate temprano. Baño caliente, vela, silencio. Tu cuerpo pide oscuridad y descanso profundo.",
        "food": "🌿 Chocolate negro 70% · Lentejas · Té de jengibre · Remolacha · Frambuesas",
        "sport": "💪 Yoga nidra · Stretching suave · Caminata contemplativa",
        "content": "📲 Stories íntimas · Reflexiones · Behind the scenes tranquilo",
        "meditation": "🧘 _Pongo la mano en el vientre. Agradezco a mi cuerpo. No necesito hacer nada ahora mismo. Estoy segura._",
        "affirmation": "✨ «Me permito descansar. Mi cuerpo hace un trabajo extraordinario y sagrado.»",
        "response": "Te escucho 🫀\n\nEstás en *Menstruación* — tu invierno interior 🌑\n\nLas lágrimas, el cansancio, querer estar sola — todo es biología, no debilidad.\n\nNo estás rota. Estás completa.",
    },
    {
        "key": "folicular",
        "name": "Folicular",
        "season": "Primavera interior",
        "emoji": "🌱",
        "days": (6, 13),
        "morning_options": [
            "Buenos días 🌱 Tu energía está despertando.\n¡Aprovecha este impulso de primavera!",
            "Hola 🌱 El cerebro está encendido hoy.\nBuen momento para empezar algo nuevo.",
            "Buenos días ✨ Tienes buenos días por delante — úsalos bien.",
        ],
        "body": "El estrógeno sube y con él tu energía. El cerebro entra en modo creativo. Más claridad mental, más ganas de empezar cosas nuevas.",
        "emotions": "🌸 Optimismo espontáneo sin razón aparente\n💡 Las ideas llegan solas — úsalas\n🤸 Ganas de conectar, socializar, explorar\n🌟 La confianza regresa de forma natural",
        "warning": "⚠️ Puedes querer hacer demasiado — todo parece posible. Anota las ideas pero no te comprometas con todo.",
        "work": "🧠 Empieza proyectos nuevos ahora. Pitches, negociaciones, primeros pasos — todo aquí.",
        "relations": "💑 Momento ideal para conversaciones honestas — estás más abierta y menos reactiva.",
        "selfesteem": "👑 La confianza regresa naturalmente. Es buen momento para hacer cosas que antes parecían difíciles.",
        "ritual": "🕯️ Puedes acostarte un poco más tarde. Mañana, 10 minutos sin teléfono — las mejores ideas llegan en silencio.",
        "food": "🌿 Huevos · Brócoli · Aguacate · Semillas de lino · Limón",
        "sport": "💪 HIIT · Pilates · Cardio · Pesas ligeras",
        "content": "📲 Tutoriales · Reels con energía · Nuevos proyectos · Es tu mejor momento para crear",
        "meditation": "🧘 _Siento cómo algo en mí despierta. Estoy abierta a lo nuevo. Confío en mi energía._",
        "affirmation": "✨ «Soy nueva cada día. Mi energía florece con cada paso que doy.»",
        "response": "🌱 Estás en *Fase Folicular* — tu primavera interior.\n\nTu energía está creciendo, las ideas fluyen.\n\nEs tu momento de plantar semillas 🌸",
    },
    {
        "key": "ovulacion",
        "name": "Ovulación",
        "season": "Verano interior",
        "emoji": "☀️",
        "days": (14, 16),
        "morning_options": [
            "¡Buenos días! Hoy brillas más que nunca ☀️\nEstás en tu verano interior. Úsalo.",
            "Hola ☀️ Hoy eres magnética. Sin esfuerzo.",
            "Buenos días 👑 Pico de energía y carisma. Hoy es día de aparecer.",
        ],
        "body": "Pico de estrógeno y testosterona. Eres más carismática, comunicativa y presente. La biología te pone en el centro del mundo.",
        "emotions": "✨ Te sientes vista, escuchada, deseada\n🔥 La creatividad y el deseo están en máximos\n💛 La generosidad fluye — quieres dar y compartir\n👑 Tu presencia ocupa espacio sin disculpas",
        "warning": "⚠️ Puedes dar demasiado de ti misma. Después del verano viene el otoño. Guarda algo para ti.",
        "work": "🧠 Firma contratos, haz presentaciones, graba videos, haz lives. Estás literalmente brillando — úsalo.",
        "relations": "💑 El mejor momento para la intimidad y para pedir algo importante. Eres más convincente ahora.",
        "selfesteem": "👑 Tu autoestima está en su punto más alto. Es buen momento para hacer cosas que requieren valentía.",
        "ritual": "🕯️ Puedes dormir menos y sentirte bien. Baila, muévete, estate con gente.",
        "food": "🌿 Salmón · Espinacas frescas · Frutos rojos · Almendras · Mango",
        "sport": "💪 Fuerza · Running · Deportes en grupo · Baile libre",
        "content": "📲 Lives · Colaboraciones · Videos de cara · Contenido de máximo impacto · HOY es el día",
        "meditation": "🧘 _Me permito brillar. Mi presencia es un regalo. Recibo la atención con gratitud._",
        "affirmation": "✨ «Irradio luz. Mi presencia transforma todo lo que toco.»",
        "response": "☀️ Estás en *Ovulación* — tu verano interior.\n\nEres la versión más magnética de ti misma ahora mismo. Sin esfuerzo.\n\nEres la protagonista. Úsalo 👑",
    },
    {
        "key": "lutea",
        "name": "Lútea",
        "season": "Otoño interior",
        "emoji": "🍂",
        "days": (17, 28),
        "morning_options": [
            "Buenos días 🍂 Hoy ve hacia adentro.\nEstás en tu otoño interior. Es tiempo de profundidad.",
            "Hola 🍂 Hoy la energía va hacia dentro.\nNo es mal día — es un día diferente.",
            "Buenos días 🌙 Tu otoño interior está aquí.\nEs tiempo de terminar, reflexionar y soltar.",
        ],
        "body": "La progesterona domina. La energía va hacia adentro. Eres más perceptiva, más crítica, más sensible a lo que está y a lo que falta.",
        "emotions": "🍃 Las emociones se vuelven más profundas y reales\n🙏 La gratitud se siente con todo el cuerpo\n💧 Las lágrimas llegan más fácil — y eso sana\n🫀 El corazón se vuelve más suave y abierto\n🌙 Aparece la necesidad de sentido y propósito",
        "warning": "⚠️ Si sientes que no eres suficiente, que todo se derrumba — espera. No es un diagnóstico. Es la progesterona. En unos días esto pasa.",
        "work": "🧠 Ideal para terminar, editar, mejorar. No empieces cosas nuevas — cierra lo pendiente.",
        "relations": "💑 Evita conversaciones difíciles en los días 24-28. Si algo te molestó, escríbelo y habla después de la menstruación.",
        "selfesteem": "👑 Tu autoestima puede fluctuar ahora. Lo que sientes sobre ti misma en estos días no es la verdad completa.",
        "ritual": "🕯️ Tu cuerpo pide más sueño. Acuéstate más temprano. Escribe en un diario — sale lo más honesto de ti.",
        "food": "🌿 Batata asada · Pollo al horno · Nueces · Manzana con canela · Avena",
        "sport": "💪 Pilates · Natación · Yoga · Caminatas largas en silencio",
        "content": "📲 Edición · Planificación · Contenido reflexivo y honesto · Responder comentarios",
        "meditation": "🧘 _Pongo la mano en el corazón. Me permito sentir todo lo que hay. Mis emociones son mi profundidad. Estoy segura._",
        "affirmation": "✨ «Confío en mi proceso. Todo lo que sembré está creciendo, aunque aún no lo vea.»",
        "response": "Te escucho 🍂\n\nEstás en *Fase Lútea* — tu otoño interior.\n\nLas emociones profundas, las lágrimas, querer ir más despacio — todo tiene sentido.\n\nEsto no es depresión. Es profundidad. El otoño antes del invierno 🌱",
    }
]

def get_phase(last_period_str):
    try:
        last_period = datetime.strptime(last_period_str, "%d/%m/%Y").date()
        today = date.today()
        diff = (today - last_period).days
        cycle_day = (diff % 28) + 1
        for phase in phases:
            if phase["days"][0] <= cycle_day <= phase["days"][1]:
                return phase, cycle_day
        return phases[3], cycle_day
    except:
        return None, None

def parse_date(text):
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d %m %Y"]:
        try:
            return datetime.strptime(text.strip(), fmt).strftime("%d/%m/%Y")
        except:
            continue
    return None

def get_forecast(last_period_str):
    try:
        last_period = datetime.strptime(last_period_str, "%d/%m/%Y").date()
        today = date.today()
        lines = ["🔮 *Tus próximos 5 días:*\n"]
        labels = ["Mañana", "En 2 días", "En 3 días", "En 4 días", "En 5 días"]
        for i in range(1, 6):
            future = today + timedelta(days=i)
            diff = (future - last_period).days
            cycle_day = (diff % 28) + 1
            for phase in phases:
                if phase["days"][0] <= cycle_day <= phase["days"][1]:
                    lines.append(f"{phase['emoji']} *{labels[i-1]}* — Día {cycle_day} · {phase['name']}")
                    break
        return "\n".join(lines) + "\n\n_Planifica tu semana según tu ciclo 💜_"
    except:
        return "No pude calcular el pronóstico."

def send_reply(text):
    resp = MessagingResponse()
    resp.message(text)
    return str(resp)

def handle_message(phone, text):
    text = text.strip()
    text_lower = text.lower()

    user = users.get(phone, {"name": "", "fecha_periodo": "", "state": "new"})

    if user["state"] == "new":
        users[phone] = {"name": "", "fecha_periodo": "", "state": "asking_name"}
        return "¡Hola! Soy *Taina* 🌙\nTu compañera de ciclo consciente.\n\nEstoy aquí para ayudarte a entender tu cuerpo, tus emociones y tu energía según tu ciclo.\n\n¿Cómo te llamas? 💜\n\n_⚠️ Taina es una guía de bienestar. No reemplaza la consulta médica._"

    if user["state"] == "asking_name":
        name = text.capitalize()
        users[phone] = {"name": name, "fecha_periodo": "", "state": "asking_date"}
        return f"¡Hola {name}! 💜\n\nPara acompañarte necesito saber una cosa:\n\n📅 ¿Cuándo comenzó tu último período?\n\nEscríbeme la fecha así:\n*15/03/2025*"

    if user["state"] == "asking_date":
        parsed = parse_date(text)
        if not parsed:
            return "Hmm, no entendí la fecha 😊\n\nEscríbela así: *15/03/2025*\n(día/mes/año)"
        phase, cycle_day = get_phase(parsed)
        if not phase:
            return "No pude calcular tu ciclo. Intenta con el formato: *15/03/2025*"
        users[phone] = {"name": user["name"], "fecha_periodo": parsed, "state": "active"}
        humor_msg = random.choice(humor[phase["key"]])
        return f"Perfecto {user['name']} 🌙\n\nCalculé tu ciclo ✨\nHoy estás en el *día {cycle_day}* — *{phase['name']}*\n{phase['emoji']} {phase['season']}\n\n😄 _{humor_msg}_\n\nEscribe *menú* para ver todo lo que puedo hacer por ti 💜"

    if user["state"] == "active":
        phase, cycle_day = get_phase(user["fecha_periodo"])
        name = user["name"]
        if not phase:
            return "Hubo un error. Escríbeme tu fecha: *15/03/2025*"

        humor_msg = random.choice(humor[phase["key"]])
        wisdom_msg = random.choice(wisdom)

        # RESET
        if any(w in text_lower for w in ["me bajó", "empecé", "llegó", "nuevo ciclo", "me llegó", "empezó", "me vino"]):
            today_str = date.today().strftime("%d/%m/%Y")
            users[phone] = {"name": name, "fecha_periodo": today_str, "state": "active"}
            return f"Gracias por avisarme {name} 🌑\n\nReinicié tu ciclo desde hoy.\n*Día 1 — Menstruación, invierno interior.*\n\nDescansa. No te exijas.\nTu cuerpo hace un trabajo sagrado 💜\n\n😄 _{random.choice(humor['menstruacion'])}_"

        # CHECKIN
        for key, response in checkin_responses.items():
            if key in text_lower:
                return f"{response}\n\nEstás en el *día {cycle_day}* — {phase['name']} {phase['emoji']}\n\n{phase['affirmation']}\n\n_🌙 {wisdom_msg}_"

        # MENÚ
        if any(w in text_lower for w in ["menú", "menu", "ayuda", "help", "hola", "hi", "buenas", "buenos"]):
            return f"Hola {name} 🌙\n\nEstás en el *día {cycle_day}* — {phase['name']} {phase['emoji']}\n_{phase['season']}_\n\n¿Qué necesitas hoy?\n\n📋 *plan* — tu plan completo\n🫀 *cuerpo* — cuerpo y emociones\n🧠 *trabajo* — trabajo y decisiones\n💑 *relaciones* — relaciones\n🕯️ *ritual* — ritual de noche\n👑 *autoestima* — cómo está tu autoestima\n🔮 *próximos* — pronóstico 5 días\n😄 *sonrisa* — humor del día\n✨ *afirmación* — tu frase de hoy\n✅ *checkin* — ¿cómo te sientes?\n🔄 *me bajó* — reiniciar ciclo"

        # PLAN
        if any(w in text_lower for w in ["plan", "hoy", "todo", "completo"]):
            return f"{phase['emoji']} *Día {cycle_day} — {phase['name']}*\n_{phase['season']}_\n\n{phase['body']}\n\n*Lo que es normal sentir:*\n{phase['emotions']}\n\n{phase['work']}\n\n{phase['ritual']}\n\n{phase['food']}\n{phase['sport']}\n{phase['content']}\n\n{phase['affirmation']}\n\n😄 _{humor_msg}_\n\n_🌙 {wisdom_msg}_"

        # CUERPO
        if any(w in text_lower for w in ["cuerpo", "emocion", "física", "fisico"]):
            return f"🫀 *Cuerpo y emociones — Día {cycle_day}*\n\n{phase['body']}\n\n*Lo que es normal sentir:*\n{phase['emotions']}\n\n{phase['warning']}\n\n{phase['meditation']}\n\n{phase['affirmation']}"

        # TRABAJO
        if any(w in text_lower for w in ["trabajo", "decisión", "decision", "proyecto"]):
            return f"🧠 *Trabajo y decisiones — Día {cycle_day}*\n\n{phase['work']}\n\n{phase['warning']}\n\n{phase['affirmation']}\n\n😄 _{humor_msg}_"

        # RELACIONES
        if any(w in text_lower for w in ["relacion", "pareja", "sexo", "intimidad", "amor"]):
            return f"💑 *Relaciones — Día {cycle_day}*\n\n{phase['relations']}\n\n{phase['selfesteem']}\n\n{phase['affirmation']}"

        # RITUAL
        if any(w in text_lower for w in ["ritual", "noche", "dormir", "sueño", "descanso"]):
            return f"🕯️ *Ritual de noche — Día {cycle_day}*\n\n{phase['ritual']}\n\n{phase['food']}\n{phase['sport']}\n\n{phase['meditation']}\n\n{phase['affirmation']}"

        # AUTOESTIMA
        if any(w in text_lower for w in ["autoestima", "seguridad", "confianza", "fea", "no me gusto"]):
            return f"👑 *Autoestima — Día {cycle_day}*\n\n{phase['selfesteem']}\n\n{phase['warning']}\n\n{phase['affirmation']}\n\n_🌙 {wisdom_msg}_"

        # PRÓXIMOS
        if any(w in text_lower for w in ["próximos", "proximos", "pronóstico", "pronostico", "semana"]):
            return get_forecast(user["fecha_periodo"])

        # HUMOR
        if any(w in text_lower for w in ["sonrisa", "humor", "chiste"]):
            return f"😄 *Tu sonrisa de hoy:*\n\n_{humor_msg}_\n\nDía {cycle_day} — {phase['name']} {phase['emoji']}"

        # AFIRMACIÓN
        if any(w in text_lower for w in ["afirmación", "afirmacion", "frase", "motivación"]):
            return f"{phase['emoji']} *Tu afirmación de hoy:*\n\n{phase['affirmation']}\n\n_🌙 {wisdom_msg}_"

        # CHECKIN PROMPT
        if any(w in text_lower for w in ["checkin", "check", "estado"]):
            return f"¿Cómo te sientes hoy {name}? {phase['emoji']}\n\nEscribe una palabra:\n\n🌤 tranquila\n🔥 irritación\n😔 tristeza\n😵 cansancio\n✨ inspiración\n💖 amor\n😶 apatía"

        # EMOCIONAL
        emotional_words = ["triste", "lloro", "llorando", "cansada", "agotada", "ansiosa",
                           "ansiedad", "mal", "horrible", "irritada", "enojada", "depre",
                           "no puedo", "todo mal", "confundida", "rara", "sola", "frustrada", "bloqueada"]
        if any(w in text_lower for w in emotional_words):
            return f"{phase['response']}\n\nEstás en el *día {cycle_day}* de tu ciclo.\n\n{phase['warning']}\n\n{phase['affirmation']}\n\n_🌙 {wisdom_msg}_"

        # DEFAULT
        return f"Hola {name} {phase['emoji']}\n\nEstás en el *día {cycle_day}* — {phase['name']}, {phase['season']}.\n\n{random.choice(phase['morning_options'])}\n\nEscribe *menú* para ver todo lo que puedo hacer por ti 💜"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    phone = request.values.get("From", "")
    reply = handle_message(phone, incoming_msg)
    return send_reply(reply)

@app.route("/", methods=["GET"])
def index():
    return "Taina está activa 🌙"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
