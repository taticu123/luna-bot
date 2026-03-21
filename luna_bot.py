from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, date, timedelta
import os
import random

app = Flask(__name__)

# Base de datos en memoria
users = {}

# ============================================================
# HUMOR — automático, no por menú
# ============================================================

humor = {
    "menstruacion": [
        "El gimnasio de hoy es llegar al refrigerador y volver. Cuenta. 🛋️",
        "Si hoy quieres cancelar todo — quizás no es pereza. Es sabiduría.",
        "Hoy tu superpoder es no hacer nada sin culpa.",
        "Vela + té + cobija = programa completo de desarrollo personal.",
        "Si alguien te molesta hoy — imagínate que eres un oso hibernando. 🐻",
        "Hoy el mundo puede esperar. Tú no tienes que.",
    ],
    "folicular": [
        "El cerebro volvió. Como una computadora después de actualizar. 💻",
        "Hoy las ideas llegan solas. Algunas serán brillantes. Otras, solo tuyas.",
        "El humor hoy es como el de alguien que encontró el cargador del teléfono. 🔋",
        "Hoy es buen día para empezar algo. O al menos para abrir una lista nueva.",
        "El mundo vuelve a verse como un lugar donde se puede inventar algo.",
    ],
    "ovulacion": [
        "Hoy la gente de repente parece más agradable. No es tu imaginación. Son las hormonas. ✨",
        "Si hoy quieres vestirte bonito — escúchate. Tu cuerpo sabe.",
        "Hoy la carisma funciona sin esfuerzo. Aprovéchalo.",
        "Hoy hay posibilidades de sentirte como la protagonista. Porque lo eres. 🎬",
        "Si hoy quieres coquetear con la vida — es simplemente tu verano. ☀️",
    ],
    "lutea": [
        "Hoy el cerebro nota todo: el vaso sucio, la vieja conversación y la imperfección del universo. 🍂",
        "Si hoy la paciencia se acaba rápido — son las hormonas probando los límites. No tú.",
        "Hoy puede llegar el deseo de orden, chocolate y soledad. Todo al mismo tiempo.",
        "Si hoy quieres reorganizar tu vida — empieza por el cajón de la cocina.",
        "Si hoy quieres cancelar a media humanidad — es parte normal de la revisión otoñal.",
        "Hoy el alma dice: vamos a ser honestas. 🌙",
        "Si el humor cambia más rápido que el clima — es solo el viento lúteo.",
    ]
}

wisdom = [
    "La energía femenina no tiene que ser igual todos los días. La ciclicidad no es debilidad — es navegación.",
    "No todas las emociones son verdad. Algunas son solo hormonas. Y eso también está bien.",
    "Durante la ovulación las mujeres toman decisiones más valientes. No es coincidencia.",
    "El ciclo no es un problema a resolver. Es un mapa para vivir.",
    "Tu cuerpo no está roto. Está cíclico. Hay diferencia.",
    "Descansar en invierno no es perder el tiempo. Es prepararse para la primavera.",
    "La intuición habla más fuerte en los días de menstruación. Vale la pena escucharla.",
    "Cada fase tiene su inteligencia. Ninguna es mejor que otra.",
    "El ciclo te enseña que no tienes que ser la misma todos los días para ser suficiente.",
    "Tu sensibilidad no es un defecto. Es información.",
]

# ============================================================
# FASES
# ============================================================

phases = [
    {
        "key": "menstruacion",
        "name": "Menstruación",
        "season": "Invierno interior",
        "emoji": "🌑",
        "days": (1, 5),

        # Mensaje de mañana — 3 partes separadas
        "morning_1": [
            "Día {day} 🌑 Tu invierno interior.\nHoy el cuerpo hace trabajo sagrado. No tienes que demostrar nada.",
            "Día {day} 🌑 Estás en tu invierno.\nDescansa sin culpa. El descanso de hoy es productivo.",
            "Día {day} 🌑 Invierno interior.\nHoy el cuerpo manda. Escúchalo — no es debilidad, es inteligencia.",
        ],
        "morning_3": [
            "Me permito descansar. Mi cuerpo hace un trabajo extraordinario y sagrado. 💜",
            "Estoy completa, incluso en silencio. Incluso en reposo. 💜",
            "No necesito hacer nada hoy para merecer descanso. Ya lo merezco. 💜",
        ],

        # Bloques de contenido
        "cuerpo": "Cuerpo hoy 🌑\n\nTu útero trabaja. El sistema nervioso pide quietud. Esto es inteligencia biológica — no debilidad.\n\nNormal sentir:\n🌊 Emociones sin filtros\n🔮 Intuición más fuerte\n🕯️ Ganas de estar sola\n💫 Revelaciones en silencio\n\n_Pongo la mano en el vientre. No necesito hacer nada ahora mismo. Estoy segura._",

        "trabajo": "Trabajo hoy 🌑\n\nEvita decisiones importantes.\nSi algo parece catástrofe — escríbelo y vuelve en 5 días.\nProbablemente no es una catástrofe.\n\n⚠️ Lo que sientes sobre ti misma en estos días no es la verdad completa.",

        "relaciones": "Relaciones hoy 🌑\n\nNo te expliques demasiado.\nSolo di 'necesito estar sola' — eso no es egoísmo.\n\nEvita conversaciones difíciles estos días.\nSi algo te molestó — escríbelo. Habla después.",

        "ritual": "Noche hoy 🌑\n\nAcuéstate temprano.\nBaño caliente, vela, silencio.\nNada de pantallas antes de dormir.\n\n🌿 Come: chocolate negro, lentejas, té de jengibre, remolacha\n💪 Muévete: yoga suave, caminata tranquila",

        "autoestima": "Autoestima hoy 🌑\n\nPuede sentirse más baja ahora.\nEso es hormonal — no real.\n\nLo que piensas sobre ti misma en estos días no es la verdad completa.\nEspera unos días. La perspectiva regresa.",

        "warning": "⚠️ Si ahora sientes que todo está mal y quieres cambiarlo todo — espera 5 días. No es la realidad. Son las hormonas.",

        "response_emotional": "Te escucho 🫀\n\nEstás en tu invierno interior 🌑 Día {day}.\n\nLas lágrimas, el cansancio, querer estar sola — todo es biología, no debilidad.\n\nNo estás rota. Estás completa.\n\n⚠️ Si sientes que todo está mal — espera 5 días. No es la realidad.",
    },
    {
        "key": "folicular",
        "name": "Folicular",
        "season": "Primavera interior",
        "emoji": "🌱",
        "days": (6, 13),

        "morning_1": [
            "Día {day} 🌱 Tu primavera interior.\nLa energía despierta. Las ideas llegan. Es tu momento.",
            "Día {day} 🌱 Primavera interior.\nEl cerebro está encendido. Buen momento para empezar algo nuevo.",
            "Día {day} 🌱 Tu energía regresa.\nAprovecha este impulso — dura unos días.",
        ],
        "morning_3": [
            "Soy nueva cada día. Mi energía florece con cada paso. 💜",
            "Estoy abierta a lo nuevo. Confío en mi energía. 💜",
            "Lo que quiero crear ya está en mí. Solo necesito empezar. 💜",
        ],

        "cuerpo": "Cuerpo hoy 🌱\n\nEl estrógeno sube — y con él tu energía y claridad mental.\nMás ganas de empezar cosas. El cuerpo se siente más ligero.\n\nNormal sentir:\n🌸 Optimismo sin razón aparente\n💡 Ideas que llegan solas\n🤸 Ganas de conectar y explorar\n🌟 Confianza que regresa\n\n_Siento cómo algo en mí despierta. Confío en mi energía._",

        "trabajo": "Trabajo hoy 🌱\n\nEmpieza proyectos nuevos ahora.\nPitches, negociaciones, primeros pasos — todo aquí.\nTu cerebro analítico está en su punto más alto.\n\n⚠️ Puedes querer hacer demasiado. Anota las ideas pero no te comprometas con todo.",

        "relaciones": "Relaciones hoy 🌱\n\nMomento ideal para conversaciones honestas.\nEstás más abierta y menos reactiva.\n\nReconecta con personas que no ves hace tiempo.\nBuen momento para decir lo que tienes pendiente.",

        "ritual": "Noche hoy 🌱\n\nPuedes acostarte un poco más tarde esta semana.\n10 minutos sin teléfono por la mañana — las mejores ideas llegan en silencio.\n\n🌿 Come: huevos, brócoli, aguacate, semillas de lino\n💪 Muévete: HIIT, pilates, pesas ligeras",

        "autoestima": "Autoestima hoy 🌱\n\nLa confianza regresa de forma natural ahora.\n\nEs buen momento para hacer cosas que antes parecían difíciles.\nTu voz merece espacio.",

        "warning": "⚠️ Puedes querer hacer demasiado — todo parece posible. Anota las ideas pero no te comprometas con todo de una vez.",

        "response_emotional": "Tiene sentido lo que sientes 🌱\n\nEstás en tu primavera interior. Día {day}.\n\nTu energía está creciendo — y con ella la claridad, las ganas, el optimismo.\n\nEs tu momento de plantar semillas 🌸",
    },
    {
        "key": "ovulacion",
        "name": "Ovulación",
        "season": "Verano interior",
        "emoji": "☀️",
        "days": (14, 16),

        "morning_1": [
            "Día {day} ☀️ Tu verano interior.\nHoy brillas. Sin esfuerzo. Úsalo.",
            "Día {day} ☀️ Verano interior.\nPico de energía y carisma. Hoy es día de aparecer.",
            "Día {day} ☀️ Eres magnética hoy.\nLa biología trabaja para ti. Aprovéchalo.",
        ],
        "morning_3": [
            "Irradio luz. Mi presencia transforma todo lo que toco. 💜",
            "Me permito brillar. Mi presencia es un regalo. 💜",
            "Soy la protagonista de mi historia. Hoy más que nunca. 💜",
        ],

        "cuerpo": "Cuerpo hoy ☀️\n\nPico de estrógeno y testosterona.\nEres más carismática, comunicativa y presente.\nLa biología te pone en el centro del mundo.\n\nNormal sentir:\n✨ Sentirte vista y deseada\n🔥 Creatividad y deseo en máximos\n💛 Ganas de dar y compartir\n👑 Presencia que ocupa espacio\n\n_Me permito brillar. Mi presencia es un regalo._",

        "trabajo": "Trabajo hoy ☀️\n\nFirma contratos.\nHaz presentaciones.\nGraba videos. Haz lives.\n\nEstás literalmente brillando — la gente lo siente.\nHoy es el día.\n\n⚠️ Puedes dar demasiado de ti misma. Guarda algo para ti.",

        "relaciones": "Relaciones hoy ☀️\n\nEl mejor momento para la intimidad.\nPara pedir algo importante.\nPara conversaciones difíciles — eres más convincente ahora.\n\nTu carisma está en máximos. Úsalo con intención.",

        "ritual": "Noche hoy ☀️\n\nPuedes dormir menos y sentirte bien.\nBaila, muévete, estate con gente.\n\n🌿 Come: salmón, espinacas, frutos rojos, almendras\n💪 Muévete: fuerza, running, baile libre",

        "autoestima": "Autoestima hoy ☀️\n\nEstá en su punto más alto ahora.\n\nEs el mejor momento para hacer cosas que requieren valentía.\nTu voz, tu presencia, tu seguridad — todo está disponible hoy.",

        "warning": "⚠️ Puedes dar demasiado de ti misma — tiempo, energía, atención. Después del verano viene el otoño. Guarda algo para ti.",

        "response_emotional": "Tiene todo el sentido ☀️\n\nEstás en tu verano interior. Día {day}.\n\nEres la versión más magnética de ti misma ahora mismo. Sin esfuerzo.\n\nEres la protagonista. Úsalo 👑",
    },
    {
        "key": "lutea",
        "name": "Lútea",
        "season": "Otoño interior",
        "emoji": "🍂",
        "days": (17, 28),

        "morning_1": [
            "Día {day} 🍂 Tu otoño interior.\nHoy la energía va hacia adentro. Es tiempo de profundidad.",
            "Día {day} 🍂 Otoño interior.\nNo es mal día — es un día diferente. Más lento. Más honesto.",
            "Día {day} 🍂 Tu otoño está aquí.\nTermina, reflexiona, suelta. Eso es todo lo que necesitas hoy.",
        ],
        "morning_3": [
            "Confío en mi proceso. Todo lo que sembré está creciendo, aunque aún no lo vea. 💜",
            "Me permito sentir todo lo que hay. Mis emociones son mi profundidad. 💜",
            "Estoy segura incluso en los momentos más oscuros. El invierno viene después — y luego la primavera. 💜",
        ],

        "cuerpo": "Cuerpo hoy 🍂\n\nLa progesterona domina.\nLa energía va hacia adentro.\nEres más perceptiva, más sensible, más profunda.\n\nNormal sentir:\n🍃 Emociones más profundas y reales\n🙏 Gratitud que se siente con el cuerpo\n💧 Lágrimas que llegan más fácil — y eso sana\n🫀 Corazón más suave y abierto\n🌙 Necesidad de sentido y propósito\n\n_Pongo la mano en el corazón. Me permito sentir todo lo que hay._\n\nEsto no es depresión. Es profundidad.",

        "trabajo": "Trabajo hoy 🍂\n\nIdeal para terminar, editar, mejorar.\nNo empieces cosas nuevas — cierra lo pendiente.\nTu ojo para los detalles está en su punto más alto.\n\n⚠️ Si sientes que no eres suficiente o que todo se derrumba — espera. Es la progesterona. En unos días esto pasa.",

        "relaciones": "Relaciones hoy 🍂\n\nEvita conversaciones difíciles en los días 24-28.\nPuedes percibir todo más intenso de lo que es.\n\nSi algo te molestó — escríbelo.\nHabla de eso después de la menstruación.",

        "ritual": "Noche hoy 🍂\n\nTu cuerpo pide más sueño. Acuéstate más temprano.\nEscribe en un diario — en esta fase sale lo más honesto de ti.\n\n🌿 Come: batata, nueces, manzana con canela, avena\n💪 Muévete: pilates, yoga, caminatas largas en silencio",

        "autoestima": "Autoestima hoy 🍂\n\nPuede fluctuar en estos días.\nEso es normal y hormonal.\n\nLo que sientes sobre ti misma en los días 22-26 no es la verdad completa.\nEspera unos días. La perspectiva regresa.\n\n⚠️ No tomes decisiones sobre ti misma en estos días.",

        "warning": "⚠️ Si en los días 22-26 sientes que no eres suficiente o que todo se derrumba — espera. No es un diagnóstico. Es la progesterona. En unos días esto pasa.",

        "response_emotional": "Te escucho 🍂\n\nEstás en tu otoño interior. Día {day}.\n\nLas emociones profundas, las lágrimas, querer ir más despacio — todo tiene sentido ahora.\n\nEsto no es depresión. Es profundidad.\nEl otoño antes del invierno. Y el invierno antes de la primavera 🌱\n\n⚠️ Si sientes que no eres suficiente ahora — espera unos días. No es la verdad.",
    }
]

# ============================================================
# FUNCIONES
# ============================================================

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
        lines = ["🔮 Tus próximos 5 días\n"]
        labels = ["Mañana", "En 2 días", "En 3 días", "En 4 días", "En 5 días"]
        for i in range(1, 6):
            future = today + timedelta(days=i)
            diff = (future - last_period).days
            cycle_day = (diff % 28) + 1
            for phase in phases:
                if phase["days"][0] <= cycle_day <= phase["days"][1]:
                    lines.append(f"{phase['emoji']} {labels[i-1]} — Día {cycle_day} · {phase['name']}")
                    break
        lines.append("\n_Planifica tu semana según tu ciclo 💜_")
        return "\n".join(lines)
    except:
        return "No pude calcular el pronóstico."

def send_reply(text):
    resp = MessagingResponse()
    resp.message(text)
    return str(resp)

def morning_message(phase, cycle_day):
    """Genera los 3 mensajes de mañana concatenados con separadores"""
    msg1 = random.choice(phase["morning_1"]).format(day=cycle_day)
    msg2 = random.choice(humor[phase["key"]])
    msg3 = random.choice(phase["morning_3"])
    wisdom_msg = random.choice(wisdom)
    return f"{msg1}\n\n😄 {msg2}\n\n{msg3}\n\n_🌙 {wisdom_msg}_"

# ============================================================
# LÓGICA PRINCIPAL
# ============================================================

def handle_message(phone, text):
    text = text.strip()
    text_lower = text.lower()

    user = users.get(phone, {"name": "", "fecha_periodo": "", "state": "new"})

    # ── NUEVO ──────────────────────────────────────────────────
    if user["state"] == "new":
        users[phone] = {"name": "", "fecha_periodo": "", "state": "asking_name"}
        return "Hola, soy *Taina* 🌙\nTu compañera de ciclo consciente.\n\nEstoy aquí para ayudarte a entender tu cuerpo, tus emociones y tu energía — según el momento de tu ciclo.\n\nCómo te llamas 💜\n\n_Taina es una guía de bienestar. No reemplaza la consulta médica._"

    # ── NOMBRE ─────────────────────────────────────────────────
    if user["state"] == "asking_name":
        name = text.capitalize()
        users[phone] = {"name": name, "fecha_periodo": "", "state": "asking_date"}
        return f"Hola {name} 💜\n\nPara acompañarte necesito saber una cosa:\n\nCuándo comenzó tu último período\n\nEscríbeme la fecha así:\n*15/03/2025*"

    # ── FECHA ──────────────────────────────────────────────────
    if user["state"] == "asking_date":
        parsed = parse_date(text)
        if not parsed:
            return "Hmm, no entendí la fecha 😊\n\nEscríbela así: *15/03/2025*\n(día/mes/año)"
        phase, cycle_day = get_phase(parsed)
        if not phase:
            return "No pude calcular tu ciclo. Intenta con el formato: *15/03/2025*"
        users[phone] = {"name": user["name"], "fecha_periodo": parsed, "state": "active"}
        return f"Perfecto {user['name']} 🌙\n\nCalculé tu ciclo ✨\nHoy estás en el *día {cycle_day}* — *{phase['name']}*\n{phase['emoji']} {phase['season']}\n\n{morning_message(phase, cycle_day)}\n\nEscribe *hoy* para tu plan completo o solo cuéntame cómo te sientes 💜"

    # ── ACTIVO ─────────────────────────────────────────────────
    if user["state"] == "active":
        phase, cycle_day = get_phase(user["fecha_periodo"])
        name = user["name"]
        if not phase:
            return "Hubo un error. Escríbeme tu fecha: *15/03/2025*"

        # RESET
        if any(w in text_lower for w in ["me bajó", "empecé", "llegó", "nuevo ciclo", "me llegó", "empezó", "me vino", "bajó"]):
            today_str = date.today().strftime("%d/%m/%Y")
            users[phone] = {"name": name, "fecha_periodo": today_str, "state": "active"}
            return f"Gracias por avisarme {name} 🌑\n\nReinicié tu ciclo desde hoy.\nDía 1 — Menstruación, invierno interior.\n\nDescansa. No te exijas.\nTu cuerpo hace un trabajo sagrado 💜\n\n😄 {random.choice(humor['menstruacion'])}"

        # BUENOS DÍAS — muestra mensaje de mañana
        if any(w in text_lower for w in ["buenos días", "buen día", "buenas", "morning", "mañana"]):
            return morning_message(phase, cycle_day)

        # HOY — plan completo pero corto
        if any(w in text_lower for w in ["hoy", "plan", "todo", "completo", "qué hago"]):
            return f"{phase['emoji']} Día {cycle_day} — {phase['name']}\n_{phase['season']}_\n\nPara ver cada parte escribe:\n\n🫀 *cuerpo*\n🧠 *trabajo*\n💑 *relaciones*\n🕯️ *ritual*\n👑 *autoestima*\n🔮 *proximos*\n\n{random.choice(phase['morning_3'])}"

        # CUERPO
        if any(w in text_lower for w in ["cuerpo", "emocion", "física", "fisico", "siento físicamente"]):
            return phase["cuerpo"]

        # TRABAJO
        if any(w in text_lower for w in ["trabajo", "decisión", "decision", "proyecto", "negocios", "firmar"]):
            return phase["trabajo"]

        # RELACIONES
        if any(w in text_lower for w in ["relacion", "pareja", "sexo", "intimidad", "amor", "pareja"]):
            return phase["relaciones"]

        # RITUAL / NOCHE
        if any(w in text_lower for w in ["ritual", "noche", "dormir", "sueño", "descanso", "comida", "deporte"]):
            return phase["ritual"]

        # AUTOESTIMA
        if any(w in text_lower for w in ["autoestima", "seguridad", "confianza", "fea", "no me gusto", "me odio"]):
            return phase["autoestima"]

        # PRÓXIMOS DÍAS
        if any(w in text_lower for w in ["proximos", "próximos", "semana", "pronóstico", "pronostico"]):
            return get_forecast(user["fecha_periodo"])

        # FASE ACTUAL
        if any(w in text_lower for w in ["fase", "ciclo", "día", "dia", "qué fase", "en qué"]):
            return f"Hoy estás en el día {cycle_day} {name} {phase['emoji']}\n\n*{phase['name']} — {phase['season']}*\n\nEscribe *hoy* para ver qué hacer 💜"

        # AYUDA
        if any(w in text_lower for w in ["ayuda", "help", "hola", "hi", "menu", "menú"]):
            return f"Hola {name} {phase['emoji']}\n\nDía {cycle_day} — {phase['name']}\n\nEscríbeme lo que necesitas:\n\n🫀 *cuerpo* — tu cuerpo hoy\n🧠 *trabajo* — decisiones y proyectos\n💑 *relaciones* — pareja e intimidad\n🕯️ *ritual* — noche y descanso\n👑 *autoestima* — cómo estás contigo\n🔮 *proximos* — próximos 5 días\n📅 *me bajó* — reiniciar ciclo\n\nO simplemente cuéntame cómo te sientes 💜"

        # RESPUESTA EMOCIONAL
        emotional_words = [
            "triste", "lloro", "llorando", "cansada", "agotada", "ansiosa",
            "ansiedad", "mal", "horrible", "irritada", "enojada", "depre",
            "no puedo", "todo mal", "confundida", "rara", "sola",
            "frustrada", "bloqueada", "vacía", "vacia", "plana",
            "feliz", "bien", "contenta", "motivada", "energía", "increíble"
        ]
        if any(w in text_lower for w in emotional_words):
            return phase["response_emotional"].format(day=cycle_day) + f"\n\n{phase['warning']}"

        # DEFAULT — responde como si fuera un mensaje de mañana
        return f"{phase['emoji']} Día {cycle_day} — {phase['name']}\n\n{random.choice(phase['morning_1']).format(day=cycle_day)}\n\n😄 {random.choice(humor[phase['key']])}\n\nEscribe *hoy* para ver tu plan o cuéntame cómo te sientes 💜"

# ============================================================
# WEBHOOK
# ============================================================

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    phone = request.values.get("From", "")
    reply = handle_message(phone, incoming_msg)
    return send_reply(reply)

@app.route("/", methods=["GET"])
def index():
    return "Taina esta activa 🌙"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
