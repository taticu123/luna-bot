from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, date
import os
import json

app = Flask(__name__)

# ============================================================
# BASE DE DATOS (en memoria para test)
# ============================================================
users = {}

# ============================================================
# FASES DEL CICLO
# ============================================================
phases = [
    {
        "name": "Menstruación",
        "season": "Invierno interior",
        "emoji": "🌑",
        "days": (1, 5),
        "morning": "Hoy ve despacio, amor. Tu cuerpo hace un trabajo sagrado 🌑",
        "body": "Tu cuerpo libera lo que ya no necesita. No es debilidad — es la fase más poderosa del ciclo. El útero trabaja, el sistema nervioso pide quietud.",
        "emotions": "🌊 Las emociones fluyen sin filtros\n🔮 La intuición habla más fuerte\n🕯️ Querer estar sola es una necesidad, no un problema\n💫 Las revelaciones llegan en silencio",
        "warning": "⚠️ Si ahora sientes que todo está mal y quieres cambiarlo todo — no lo hagas. Espera 5 días. No es la realidad, son las hormonas. Escríbelo y vuelve.",
        "work": "Evita decisiones importantes hoy. Es el mejor momento para descansar la mente, revisar, reflexionar — no para firmar ni comprometerte.",
        "relations": "No te expliques demasiado. Solo di 'necesito estar sola' — eso no es egoísmo, es autocuidado. Evita conversaciones difíciles con tu pareja estos días.",
        "ritual": "Acuéstate temprano. Baño caliente, vela, silencio. Nada de pantallas antes de dormir. Tu cuerpo pide oscuridad y descanso profundo.",
        "food": "Chocolate negro 70% · Lentejas · Té de jengibre · Remolacha · Frambuesas",
        "sport": "Yoga nidra · Stretching suave · Caminata contemplativa",
        "affirmation": "«Me permito descansar. Mi cuerpo hace un trabajo extraordinario y sagrado.»",
        "response": "Te escucho, amor 🫀\n\nEstás en *Menstruación* — tu invierno interior 🌑\n\nLo que sientes tiene sentido. Las lágrimas, el cansancio, querer estar sola — todo es biología, no debilidad.\n\nTu intuición está en su punto más alto ahora mismo. No estás rota. Estás completa."
    },
    {
        "name": "Folicular",
        "season": "Primavera interior",
        "emoji": "🌱",
        "days": (6, 13),
        "morning": "Buenos días ✨ Tu energía está despertando. Es tu primavera interior 🌱",
        "body": "El estrógeno empieza a subir y con él tu energía. El cerebro entra en modo creativo. Más claridad mental, más ganas de empezar cosas nuevas.",
        "emotions": "🌸 Optimismo espontáneo sin razón aparente\n💡 Las ideas llegan solas — úsalas\n🤸 Ganas de conectar, socializar, explorar\n🌟 La confianza regresa de forma natural",
        "warning": "⚠️ Puedes querer hacer demasiado — todo parece posible ahora. Anota las ideas pero no te comprometas con todo de una vez.",
        "work": "Es el mejor momento para empezar proyectos nuevos, hacer pitches, tener conversaciones importantes. Tu cerebro analítico está en su punto más alto.",
        "relations": "Momento ideal para conversaciones honestas — estás más abierta y menos reactiva. Reconecta con personas que no ves hace tiempo.",
        "ritual": "Puedes acostarte un poco más tarde esta semana. Por las mañanas, 10 minutos sin teléfono — las mejores ideas llegan en silencio.",
        "food": "Huevos · Brócoli · Aguacate · Semillas de lino · Limón",
        "sport": "HIIT · Pilates · Cardio · Pesas ligeras",
        "affirmation": "«Soy nueva cada día. Mi energía florece con cada paso que doy.»",
        "response": "¡Hola! 🌱\n\nEstás en *Fase Folicular* — tu primavera interior.\n\nTu energía está creciendo, las ideas fluyen, quieres conectar con el mundo. Todo eso tiene sentido ahora mismo.\n\nEs tu momento de plantar semillas 🌸"
    },
    {
        "name": "Ovulación",
        "season": "Verano interior",
        "emoji": "☀️",
        "days": (14, 16),
        "morning": "¡Buenos días! Hoy brillas más que nunca ☀️ Estás en tu verano interior.",
        "body": "Pico de estrógeno y testosterona. Eres más carismática, comunicativa y presente. Tu voz suena diferente. La biología te pone en el centro.",
        "emotions": "✨ Te sientes vista, escuchada, deseada\n🔥 La creatividad y el deseo están en máximos\n💛 La generosidad fluye — quieres dar y compartir\n👑 Tu presencia ocupa espacio sin disculpas",
        "warning": "⚠️ Puedes dar demasiado de ti misma — tu tiempo, energía, atención. Recuerda que después del verano viene el otoño. Guarda algo para ti.",
        "work": "Firma contratos, haz presentaciones, graba videos, haz lives. Estás literalmente brillando — la gente lo siente. Úsalo.",
        "relations": "El mejor momento para la intimidad, para pedir algo importante, para tener conversaciones difíciles. Eres más convincente y magnética ahora.",
        "ritual": "Puedes dormir menos y sentirte bien. Baila, muévete, estate con gente — tu cuerpo fue diseñado para esto ahora mismo.",
        "food": "Salmón · Espinacas frescas · Frutos rojos · Almendras · Mango",
        "sport": "Fuerza · Running · Deportes en grupo · Baile libre",
        "affirmation": "«Irradio luz. Mi presencia transforma todo lo que toco.»",
        "response": "¡Eso tiene todo el sentido! ☀️\n\nEstás en *Ovulación* — tu verano interior.\n\nEres la versión más magnética y extrovertida de ti misma ahora mismo. Sin esfuerzo.\n\nEres la protagonista. Úsalo 👑"
    },
    {
        "name": "Lútea",
        "season": "Otoño interior",
        "emoji": "🍂",
        "days": (17, 28),
        "morning": "Buenos días 🍂 Hoy ve hacia adentro. Estás en tu otoño interior.",
        "body": "La progesterona domina. La energía va hacia adentro. Eres más perceptiva, más crítica, más sensible a lo que está y a lo que falta.",
        "emotions": "🍃 Las emociones se vuelven más profundas y reales\n🙏 La gratitud se siente con todo el cuerpo\n💧 Las lágrimas llegan más fácil — y eso sana\n🫀 El corazón se vuelve más suave y abierto\n🌙 Aparece la necesidad de sentido y propósito",
        "warning": "⚠️ Si en los días 22-26 sientes que no eres suficiente, que todo se derrumba, que la relación está mal — espera. No es un diagnóstico. Es la progesterona. En unos días esto pasa.",
        "work": "Ideal para terminar, editar, mejorar. No empieces cosas nuevas — cierra lo que tienes pendiente. Tu ojo para los detalles está en su punto más alto.",
        "relations": "Evita conversaciones difíciles en los días 24-28 — puedes percibir todo más intenso de lo que es. Si algo te molestó, escríbelo y habla después de la menstruación.",
        "ritual": "Tu cuerpo pide más sueño. Acuéstate más temprano. Escribe en un diario — en esta fase sale lo más honesto y profundo de ti.",
        "food": "Batata asada · Pollo al horno · Nueces · Manzana con canela · Avena",
        "sport": "Pilates · Natación · Yoga dinámico · Caminatas largas en silencio",
        "affirmation": "«Confío en mi proceso. Todo lo que sembré está creciendo, aunque aún no lo vea.»",
        "response": "Te escucho 🍂\n\nEstás en *Fase Lútea* — tu otoño interior.\n\nLas emociones más profundas, las lágrimas que llegan solas, querer ir más despacio — todo eso es real y tiene sentido.\n\nEsto no es depresión. Es profundidad. Es el otoño antes del invierno. Y el invierno antes de la primavera 🌱"
    }
]

# ============================================================
# FUNCIONES
# ============================================================

def get_phase(last_period_str):
    """Calcula la fase actual basándose en la fecha del último período"""
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
    """Intenta parsear la fecha en varios formatos"""
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%d %m %Y", "%d/%m/%y"]
    for fmt in formats:
        try:
            return datetime.strptime(text.strip(), fmt).strftime("%d/%m/%Y")
        except:
            continue
    return None

def send_reply(text):
    resp = MessagingResponse()
    resp.message(text)
    return str(resp)

# ============================================================
# ESTADOS DEL BOT
# ============================================================
# Estado: new → asking_name → asking_date → active

def handle_message(phone, text):
    text = text.strip()
    text_lower = text.lower()
    
    user = users.get(phone, {"state": "new", "name": "", "fecha": ""})

    # ── NUEVO USUARIO ──────────────────────────────────────────
    if user["state"] == "new":
        users[phone] = {"state": "asking_name", "name": "", "fecha": ""}
        return """¡Hola! Soy *Luna* 🌙
Tu guía de ciclo consciente.

Estoy aquí para ayudarte a entender tu cuerpo, tus emociones y tu energía según tu ciclo.

¿Cómo te llamas?"""

    # ── PIDIENDO NOMBRE ────────────────────────────────────────
    if user["state"] == "asking_name":
        user["name"] = text.capitalize()
        user["state"] = "asking_date"
        users[phone] = user
        return f"""¡Hola {user['name']}! 💜

Para calcular tu ciclo necesito saber una cosa:

📅 ¿Cuándo comenzó tu último período?

Escríbeme la fecha así:
*15/03/2025*"""

    # ── PIDIENDO FECHA ─────────────────────────────────────────
    if user["state"] == "asking_date":
        parsed = parse_date(text)
        if not parsed:
            return f"""Hmm, no entendí la fecha 😊

Escríbela así: *15/03/2025*
(día/mes/año)"""
        
        phase, cycle_day = get_phase(parsed)
        if not phase:
            return "No pude calcular tu ciclo. Intenta con el formato: 15/03/2025"
        
        user["fecha"] = parsed
        user["state"] = "active"
        users[phone] = user
        
        return f"""Perfecto {user['name']} 🌙

Calculé tu ciclo ✨
Hoy estás en el *día {cycle_day}* — *{phase['name']}*
{phase['emoji']} {phase['season']}

A partir de mañana te escribo cada mañana con tu plan del día 💜

¿Quieres ver tu plan de hoy?
Responde: *plan*"""

    # ── USUARIO ACTIVO ─────────────────────────────────────────
    if user["state"] == "active":
        phase, cycle_day = get_phase(user["fecha"])
        name = user["name"]
        
        if not phase:
            return "Hubo un error calculando tu ciclo. Escribe tu fecha de nuevo: 15/03/2025"

        # RESET CICLO
        if any(w in text_lower for w in ["me bajó", "empecé", "llegó", "nuevo ciclo", "me llegó", "empezó"]):
            today = date.today().strftime("%d/%m/%Y")
            user["fecha"] = today
            users[phone] = user
            return f"""Gracias por avisarme {name} 🌑

Reinicié tu ciclo desde hoy.
*Día 1 — Menstruación, invierno interior.*

Descansa. No te exijas. Tu cuerpo hace un trabajo sagrado 💜"""

        # PLAN DEL DÍA
        if any(w in text_lower for w in ["plan", "hoy", "qué hago", "que hago"]):
            return f"""Tu plan de hoy, {name} {phase['emoji']}

*Día {cycle_day} — {phase['name']}*
_{phase['season']}_

¿Qué quieres ver?

Responde con una palabra:
• *cuerpo* — cuerpo y emociones
• *trabajo* — trabajo y decisiones  
• *relaciones* — relaciones y sexualidad
• *ritual* — ritual de noche
• *todo* — ver todo"""

        # CUERPO Y EMOCIONES
        if any(w in text_lower for w in ["cuerpo", "emocion", "emoción", "siento", "física"]):
            return f"""🫀 *Cuerpo y emociones — Día {cycle_day}*

{phase['body']}

*Lo que es normal sentir ahora:*
{phase['emotions']}

{phase['warning']}

{phase['affirmation']}"""

        # TRABAJO
        if any(w in text_lower for w in ["trabajo", "decisión", "decision", "proyecto"]):
            return f"""🧠 *Trabajo y decisiones — Día {cycle_day}*

{phase['work']}

{phase['warning']}

{phase['affirmation']}"""

        # RELACIONES
        if any(w in text_lower for w in ["relacion", "relación", "pareja", "sexo", "intimidad"]):
            return f"""💑 *Relaciones — Día {cycle_day}*

{phase['relations']}

{phase['affirmation']}"""

        # RITUAL
        if any(w in text_lower for w in ["ritual", "noche", "dormir", "sueño"]):
            return f"""🕯️ *Ritual de noche — Día {cycle_day}*

{phase['ritual']}

💪 *Movimiento ideal:* {phase['sport']}
🌿 *Nutrición:* {phase['food']}

{phase['affirmation']}"""

        # TODO
        if "todo" in text_lower:
            return f"""{phase['emoji']} *Tu día completo — Día {cycle_day}*
*{phase['name']} · {phase['season']}*

🫀 *Cuerpo:* {phase['body']}

*Emociones:*
{phase['emotions']}

🧠 *Trabajo:* {phase['work']}

💑 *Relaciones:* {phase['relations']}

🕯️ *Ritual:* {phase['ritual']}

💪 {phase['sport']}
🌿 {phase['food']}

{phase['affirmation']}"""

        # CÓMO TE SIENTES (respuesta emocional)
        emotional_words = ["triste", "lloro", "llorando", "cansada", "agotada", "ansiosa", 
                          "ansiedad", "mal", "horrible", "irritada", "enojada", "depre",
                          "no puedo", "todo mal", "no sé", "confundida", "rara", "extraña",
                          "energía", "bien", "feliz", "contenta", "motivada"]
        
        if any(w in text_lower for w in emotional_words):
            return f"""{phase['response']}

Estás en el *día {cycle_day}* de tu ciclo.

{phase['warning']}

{phase['affirmation']}"""

        # MI FASE
        if any(w in text_lower for w in ["fase", "ciclo", "día", "dia", "estoy en"]):
            return f"""Hoy estás en el *día {cycle_day}* {name} {phase['emoji']}

*{phase['name']} — {phase['season']}*
_{phase['energy']}_

{phase['morning']}

Escribe *plan* para ver tu plan completo de hoy 💜"""

        # AFFIRMACION
        if any(w in text_lower for w in ["afirmacion", "afirmación", "frase"]):
            return f"""{phase['emoji']} *Tu afirmación de hoy:*

{phase['affirmation']}

Día {cycle_day} — {phase['name']} 💜"""

        # AYUDA / MENU
        if any(w in text_lower for w in ["ayuda", "help", "menu", "menú", "hola", "hi", "buenas"]):
            return f"""Hola {name} 🌙

Estás en el *día {cycle_day}* — {phase['name']} {phase['emoji']}

Puedes escribirme:
• *plan* — tu plan de hoy
• *cuerpo* — cuerpo y emociones
• *trabajo* — trabajo y decisiones
• *relaciones* — relaciones
• *ritual* — ritual de noche
• *todo* — ver todo
• *fase* — ver en qué fase estás
• *me bajó* — reiniciar ciclo

O simplemente cuéntame cómo te sientes 💜"""

        # RESPUESTA DEFAULT
        return f"""{phase['response']}

Estás en el *día {cycle_day}* — {phase['name']} {phase['emoji']}

Escribe *plan* para ver tu plan de hoy
o *ayuda* para ver todas las opciones 💜"""

# ============================================================
# WEBHOOK
# ============================================================

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    phone = request.values.get("From", "")
    
    reply = handle_message(phone, incoming_msg)
    return send_reply(reply)

@app.route("/", methods=["GET"])
def index():
    return "Luna Bot está activa 🌙"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
