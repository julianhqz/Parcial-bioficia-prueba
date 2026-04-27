# app.py
# Aplicativo evaluativo de Biofísica para estudiantes de rehabilitación
# Uso sugerido: Streamlit + SQLite local

import streamlit as st
import sqlite3
import random
import json
import time
import hashlib
from datetime import datetime

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Cuestionario seguro de Biofísica",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

APP_TITLE = "Cuestionario aplicado de Biofísica"
COURSE_NAME = "Biofísica para Ciencias de la Rehabilitación"
NUM_QUESTIONS_PER_ATTEMPT = 30
TIME_LIMIT_MINUTES = 45
DATABASE_PATH = "resultados_biofisica.db"
PASSING_GRADE = 3.0

# ============================================================
# MEDIDAS DISUASIVAS: NO SON INFALIBLES, PERO DIFICULTAN COPIA
# ============================================================

SECURITY_CSS_JS = """
<style>
html, body, [class*="css"]  {
    user-select: none !important;
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
}
.watermark {
    position: fixed;
    top: 45%;
    left: 8%;
    transform: rotate(-25deg);
    opacity: 0.08;
    font-size: 44px;
    font-weight: 800;
    z-index: 9999;
    pointer-events: none;
    color: #222;
    white-space: nowrap;
}
.question-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    border: 1px solid #eeeeee;
}
.small-note {
    font-size: 0.88rem;
    color: #666;
}
.blocked-box {
    padding: 14px;
    border-radius: 12px;
    background: #fff7e6;
    border: 1px solid #ffd591;
    color: #5f3b00;
}
</style>
<script>
document.addEventListener('contextmenu', event => event.preventDefault());
document.addEventListener('copy', event => event.preventDefault());
document.addEventListener('cut', event => event.preventDefault());
document.addEventListener('paste', event => event.preventDefault());
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && ['c','v','x','s','p','u','a'].includes(e.key.toLowerCase())) {
        e.preventDefault();
    }
    if (e.key === 'F12') {
        e.preventDefault();
    }
});
</script>
"""

st.markdown(SECURITY_CSS_JS, unsafe_allow_html=True)

# ============================================================
# BANCO DE PREGUNTAS
# ============================================================

QUESTION_BANK = [
    {
        "id": "B001",
        "system": "Cardiopulmonar",
        "concept": "Gradiente",
        "question": "Durante el intercambio gaseoso alveolocapilar, ¿cuál es la explicación biofísica más adecuada de la entrada de oxígeno desde el alvéolo hacia la sangre?",
        "options": [
            "El oxígeno se mueve principalmente porque el corazón lo empuja hacia la sangre.",
            "El oxígeno se desplaza por un gradiente de presión parcial desde el alvéolo hacia la sangre capilar.",
            "El oxígeno entra a la sangre porque la membrana alveolar genera contracción activa.",
            "El oxígeno se mueve solo cuando aumenta la temperatura corporal."
        ],
        "answer": "El oxígeno se desplaza por un gradiente de presión parcial desde el alvéolo hacia la sangre capilar.",
        "explanation": "El intercambio gaseoso depende de diferencias de presión parcial. El oxígeno difunde desde donde su presión parcial es mayor hacia donde es menor."
    },
    {
        "id": "B002",
        "system": "Cardiopulmonar",
        "concept": "Resistencia",
        "question": "En una vía aérea estrechada por broncoconstricción, ¿qué ocurre con la resistencia al flujo de aire?",
        "options": [
            "Disminuye porque el aire tiene menos espacio para dispersarse.",
            "Aumenta, porque una menor luz del conducto dificulta el paso del aire.",
            "No cambia, porque la resistencia solo depende del volumen pulmonar.",
            "Se vuelve cero durante la espiración."
        ],
        "answer": "Aumenta, porque una menor luz del conducto dificulta el paso del aire.",
        "explanation": "Cuando el radio de una vía disminuye, la resistencia aumenta de manera marcada; por eso pequeños cambios de calibre pueden afectar mucho la ventilación."
    },
    {
        "id": "B003",
        "system": "Cardiopulmonar",
        "concept": "Presión",
        "question": "¿Qué principio explica mejor la entrada de aire durante la inspiración tranquila?",
        "options": [
            "El aire entra cuando la presión alveolar se hace menor que la presión atmosférica.",
            "El aire entra porque la presión atmosférica desaparece.",
            "El aire entra por contracción directa de los bronquios.",
            "El aire entra porque los alvéolos absorben nitrógeno."
        ],
        "answer": "El aire entra cuando la presión alveolar se hace menor que la presión atmosférica.",
        "explanation": "La inspiración ocurre porque la expansión torácica reduce la presión alveolar; el aire fluye desde mayor hacia menor presión."
    },
    {
        "id": "B004",
        "system": "Cardiopulmonar",
        "concept": "Flujo",
        "question": "En términos biofísicos, el flujo sanguíneo sistémico depende principalmente de:",
        "options": [
            "La diferencia de presión entre dos puntos y la resistencia vascular.",
            "La cantidad total de oxígeno inspirado sin relación con la presión.",
            "La longitud de los huesos largos.",
            "La temperatura ambiental exclusivamente."
        ],
        "answer": "La diferencia de presión entre dos puntos y la resistencia vascular.",
        "explanation": "El flujo puede entenderse como proporcional al gradiente de presión e inversamente proporcional a la resistencia."
    },
    {
        "id": "B005",
        "system": "Musculoesquelético",
        "concept": "Energía",
        "question": "Cuando una persona sube escaleras, ¿qué transformación energética es más relevante desde la biofísica del movimiento?",
        "options": [
            "La energía química del ATP se transforma en trabajo mecánico y calor.",
            "La energía eléctrica externa se convierte directamente en fuerza muscular.",
            "La energía térmica del aire se transforma totalmente en masa muscular.",
            "La energía gravitacional desaparece durante la contracción."
        ],
        "answer": "La energía química del ATP se transforma en trabajo mecánico y calor.",
        "explanation": "El músculo convierte energía química en fuerza, desplazamiento y calor; no toda la energía se convierte en trabajo útil."
    },
    {
        "id": "B006",
        "system": "Musculoesquelético",
        "concept": "Palancas",
        "question": "Al realizar flexión de codo con una mancuerna, el antebrazo puede analizarse como un sistema de palanca porque:",
        "options": [
            "Existe un punto de apoyo, una fuerza muscular y una resistencia externa.",
            "El hueso se acorta de manera activa para generar movimiento.",
            "La articulación elimina toda resistencia al movimiento.",
            "La fuerza muscular no produce torque."
        ],
        "answer": "Existe un punto de apoyo, una fuerza muscular y una resistencia externa.",
        "explanation": "Las articulaciones actúan como ejes; los músculos aplican fuerza y las cargas externas generan resistencia y torque."
    },
    {
        "id": "B007",
        "system": "Musculoesquelético",
        "concept": "Torque",
        "question": "Si una carga se aleja del eje articular, ¿qué ocurre con el torque que debe controlar el músculo?",
        "options": [
            "Aumenta porque crece el brazo de momento.",
            "Disminuye porque la carga pesa menos.",
            "No cambia porque el torque no depende de la distancia.",
            "Se convierte automáticamente en presión arterial."
        ],
        "answer": "Aumenta porque crece el brazo de momento.",
        "explanation": "El torque depende de la fuerza y de la distancia perpendicular al eje. Alejar la carga aumenta la exigencia mecánica."
    },
    {
        "id": "B008",
        "system": "Neuromuscular",
        "concept": "Membrana",
        "question": "El potencial de acción neuronal se explica mejor como:",
        "options": [
            "Un cambio rápido del potencial de membrana por movimiento selectivo de iones.",
            "Una contracción de la membrana que empuja la sangre.",
            "Un aumento de temperatura que elimina la necesidad de sodio y potasio.",
            "Una señal química que no involucra cargas eléctricas."
        ],
        "answer": "Un cambio rápido del potencial de membrana por movimiento selectivo de iones.",
        "explanation": "La excitabilidad depende de gradientes electroquímicos y permeabilidad selectiva de la membrana."
    },
    {
        "id": "B009",
        "system": "Neuromuscular",
        "concept": "Gradiente electroquímico",
        "question": "¿Por qué el sodio tiende a entrar a la neurona durante la fase ascendente del potencial de acción?",
        "options": [
            "Porque existe un gradiente electroquímico favorable para su entrada.",
            "Porque el sodio siempre se mueve contra su gradiente sin gasto energético.",
            "Porque la membrana se vuelve impermeable al sodio.",
            "Porque el sodio se transforma en potasio."
        ],
        "answer": "Porque existe un gradiente electroquímico favorable para su entrada.",
        "explanation": "La concentración y la carga eléctrica favorecen la entrada de sodio cuando se abren canales específicos."
    },
    {
        "id": "B010",
        "system": "Neuromuscular",
        "concept": "Retroalimentación",
        "question": "El reflejo miotático contribuye al control postural porque:",
        "options": [
            "Detecta cambios de longitud muscular y genera una respuesta motora compensatoria.",
            "Apaga por completo la actividad del sistema nervioso central.",
            "Impide cualquier contracción muscular voluntaria.",
            "Convierte la presión arterial en energía térmica."
        ],
        "answer": "Detecta cambios de longitud muscular y genera una respuesta motora compensatoria.",
        "explanation": "Los husos musculares informan sobre estiramiento y permiten respuestas reflejas que estabilizan la postura."
    },
    {
        "id": "B011",
        "system": "Vestibulococlear",
        "concept": "Aceleración",
        "question": "El sistema vestibular informa sobre movimiento de la cabeza principalmente porque detecta:",
        "options": [
            "Aceleraciones angulares y lineales mediante desplazamiento de estructuras sensoriales.",
            "Cambios en la glucosa sanguínea exclusivamente.",
            "Presión arterial sistémica en las arterias carótidas.",
            "Contracción directa de los músculos del oído externo."
        ],
        "answer": "Aceleraciones angulares y lineales mediante desplazamiento de estructuras sensoriales.",
        "explanation": "Canales semicirculares y órganos otolíticos responden a aceleraciones que deforman estructuras sensoriales."
    },
    {
        "id": "B012",
        "system": "Vestibulococlear",
        "concept": "Inercia",
        "question": "Cuando una persona gira rápidamente y luego se detiene, la sensación breve de seguir girando se relaciona con:",
        "options": [
            "La inercia de la endolinfa en los canales semicirculares.",
            "La desaparición completa de la gravedad.",
            "El aumento permanente del tamaño de la cóclea.",
            "La pérdida inmediata del potencial de membrana muscular."
        ],
        "answer": "La inercia de la endolinfa en los canales semicirculares.",
        "explanation": "La endolinfa puede seguir moviéndose por inercia aun cuando la cabeza se detiene, generando sensación de movimiento."
    },
    {
        "id": "B013",
        "system": "Endocrino",
        "concept": "Retroalimentación negativa",
        "question": "La regulación de la glucosa por insulina y glucagón es un ejemplo de:",
        "options": [
            "Retroalimentación negativa orientada a conservar la homeostasis.",
            "Movimiento sin gradientes químicos.",
            "Sistema mecánico sin señales químicas.",
            "Flujo sanguíneo independiente del metabolismo."
        ],
        "answer": "Retroalimentación negativa orientada a conservar la homeostasis.",
        "explanation": "Cuando la glucosa cambia, las respuestas hormonales tienden a devolverla hacia rangos funcionales."
    },
    {
        "id": "B014",
        "system": "Endocrino",
        "concept": "Transporte",
        "question": "Una hormona liposoluble atraviesa con mayor facilidad la membrana celular porque:",
        "options": [
            "La bicapa lipídica favorece el paso de moléculas lipofílicas.",
            "Todas las hormonas atraviesan igual cualquier membrana.",
            "La membrana celular no tiene propiedades selectivas.",
            "La hormona empuja mecánicamente la membrana hasta romperla."
        ],
        "answer": "La bicapa lipídica favorece el paso de moléculas lipofílicas.",
        "explanation": "La composición lipídica de la membrana facilita el paso de ciertas moléculas según su solubilidad."
    },
    {
        "id": "B015",
        "system": "Cardiopulmonar",
        "concept": "Elasticidad",
        "question": "La retracción elástica pulmonar durante la espiración tranquila permite que:",
        "options": [
            "El aire salga sin necesidad de contracción muscular intensa en condiciones normales.",
            "Los pulmones se contraigan como músculo esquelético.",
            "La presión atmosférica se anule.",
            "La sangre deje de circular temporalmente."
        ],
        "answer": "El aire salga sin necesidad de contracción muscular intensa en condiciones normales.",
        "explanation": "La elasticidad pulmonar y torácica ayuda a recuperar el volumen previo y favorece la salida de aire."
    },
    {
        "id": "B016",
        "system": "Musculoesquelético",
        "concept": "Centro de masa",
        "question": "Una base de sustentación más amplia mejora la estabilidad porque:",
        "options": [
            "Aumenta el margen para que la proyección del centro de masa permanezca dentro de la base.",
            "Hace que el cuerpo no tenga masa.",
            "Reduce a cero la gravedad.",
            "Elimina toda necesidad de control neuromuscular."
        ],
        "answer": "Aumenta el margen para que la proyección del centro de masa permanezca dentro de la base.",
        "explanation": "La estabilidad depende de la relación entre centro de masa, base de sustentación y control postural."
    },
    {
        "id": "B017",
        "system": "Neuromuscular",
        "concept": "Energía y fatiga",
        "question": "Durante una contracción sostenida, la fatiga puede explicarse parcialmente por:",
        "options": [
            "Alteraciones en disponibilidad energética, metabolitos y excitabilidad neuromuscular.",
            "Ausencia total de consumo de ATP.",
            "Conversión del músculo en tejido óseo.",
            "Desaparición completa de la resistencia externa."
        ],
        "answer": "Alteraciones en disponibilidad energética, metabolitos y excitabilidad neuromuscular.",
        "explanation": "La fatiga es multifactorial e involucra procesos energéticos, iónicos, metabólicos y neurales."
    },
    {
        "id": "B018",
        "system": "Cardiopulmonar",
        "concept": "Difusión",
        "question": "Si aumenta el grosor de la membrana alveolocapilar, la difusión de gases tiende a:",
        "options": [
            "Disminuir, porque aumenta la distancia de difusión.",
            "Aumentar indefinidamente.",
            "No cambiar nunca.",
            "Depender solo del color de la sangre."
        ],
        "answer": "Disminuir, porque aumenta la distancia de difusión.",
        "explanation": "Una mayor distancia de difusión dificulta el paso de gases entre alvéolo y capilar."
    },
    {
        "id": "B019",
        "system": "Vestibulococlear",
        "concept": "Onda mecánica",
        "question": "La audición inicia cuando el sonido se comporta como:",
        "options": [
            "Una onda mecánica que produce vibraciones transmitidas hacia el oído interno.",
            "Una corriente eléctrica que no requiere medio físico.",
            "Un cambio hormonal lento en la sangre.",
            "Una contracción voluntaria del tímpano."
        ],
        "answer": "Una onda mecánica que produce vibraciones transmitidas hacia el oído interno.",
        "explanation": "El sonido requiere propagación mecánica y se transforma en señales nerviosas a través del sistema auditivo."
    },
    {
        "id": "B020",
        "system": "Endocrino",
        "concept": "Señalización",
        "question": "Desde una mirada biofísica, la acción hormonal depende de que la señal:",
        "options": [
            "Sea transportada, alcance células diana y se una a receptores específicos.",
            "Se convierta siempre en sonido audible.",
            "Actúe sin concentración ni afinidad receptor-ligando.",
            "No tenga relación con membranas ni gradientes."
        ],
        "answer": "Sea transportada, alcance células diana y se una a receptores específicos.",
        "explanation": "La señalización hormonal integra transporte, concentración, receptores y respuesta celular."
    },
    {
        "id": "B021",
        "system": "Musculoesquelético",
        "concept": "Presión",
        "question": "Una misma fuerza aplicada sobre una superficie menor produce:",
        "options": ["Mayor presión.", "Menor presión siempre.", "La misma presión sin importar el área.", "Ausencia de deformación tisular."],
        "answer": "Mayor presión.",
        "explanation": "La presión aumenta cuando la fuerza se distribuye sobre menor área. Este principio importa en apoyo, ortesis y riesgo de lesión por presión."
    },
    {
        "id": "B022",
        "system": "Cardiopulmonar",
        "concept": "Viscosidad",
        "question": "Si aumenta mucho la viscosidad sanguínea, ¿qué efecto biofísico esperaría sobre el flujo?",
        "options": [
            "Mayor resistencia y potencial reducción del flujo si el gradiente de presión no compensa.",
            "Aumento automático del flujo sin cambios de presión.",
            "Desaparición de la resistencia vascular.",
            "Conversión de sangre en aire."
        ],
        "answer": "Mayor resistencia y potencial reducción del flujo si el gradiente de presión no compensa.",
        "explanation": "La viscosidad contribuye a la resistencia interna al movimiento del fluido."
    },
    {
        "id": "B023",
        "system": "Neuromuscular",
        "concept": "Umbral",
        "question": "En excitabilidad neuronal, el concepto de umbral indica:",
        "options": [
            "El nivel mínimo de cambio necesario para disparar una respuesta como el potencial de acción.",
            "La temperatura máxima del músculo antes de contraerse.",
            "La distancia entre dos articulaciones.",
            "La presión exacta dentro del alvéolo."
        ],
        "answer": "El nivel mínimo de cambio necesario para disparar una respuesta como el potencial de acción.",
        "explanation": "Muchas respuestas biológicas son no lineales: por debajo del umbral no se dispara la respuesta; al superarlo, aparece una respuesta organizada."
    },
    {
        "id": "B024",
        "system": "Musculoesquelético",
        "concept": "Trabajo mecánico",
        "question": "El trabajo mecánico durante un movimiento se relaciona con:",
        "options": [
            "La fuerza aplicada y el desplazamiento producido en la dirección de esa fuerza.",
            "La frecuencia cardiaca únicamente.",
            "La concentración de hormona tiroidea sin movimiento.",
            "El color de la fibra muscular."
        ],
        "answer": "La fuerza aplicada y el desplazamiento producido en la dirección de esa fuerza.",
        "explanation": "El trabajo mecánico requiere fuerza y desplazamiento. En rehabilitación ayuda a interpretar carga funcional."
    },
    {
        "id": "B025",
        "system": "Endocrino",
        "concept": "Homeostasis",
        "question": "La homeostasis puede entenderse biofísicamente como:",
        "options": [
            "Regulación dinámica de variables internas mediante sensores, señales, efectores y retroalimentación.",
            "Un estado rígido en el que ninguna variable cambia.",
            "Un proceso exclusivo del sistema óseo.",
            "La ausencia de intercambio de energía con el entorno."
        ],
        "answer": "Regulación dinámica de variables internas mediante sensores, señales, efectores y retroalimentación.",
        "explanation": "La homeostasis no significa inmovilidad; implica regulación activa dentro de rangos compatibles con la función."
    },
    {
        "id": "B026",
        "system": "Vestibulococlear",
        "concept": "Transducción",
        "question": "En el oído interno, la transducción ocurre cuando:",
        "options": [
            "Un estímulo mecánico se convierte en señal eléctrica neural.",
            "La sangre se convierte en endolinfa.",
            "La cóclea deja de responder a vibraciones.",
            "La gravedad desaparece durante el movimiento."
        ],
        "answer": "Un estímulo mecánico se convierte en señal eléctrica neural.",
        "explanation": "Las células sensoriales convierten deformaciones mecánicas en señales electroquímicas."
    },
    {
        "id": "B027",
        "system": "Cardiopulmonar",
        "concept": "Relación presión-volumen",
        "question": "La distensibilidad pulmonar se refiere a:",
        "options": [
            "La facilidad con que el pulmón cambia de volumen ante cambios de presión.",
            "La fuerza máxima de los músculos del brazo.",
            "La velocidad de conducción nerviosa auditiva.",
            "La cantidad de glucosa filtrada por el riñón."
        ],
        "answer": "La facilidad con que el pulmón cambia de volumen ante cambios de presión.",
        "explanation": "La compliance o distensibilidad expresa la relación entre cambio de volumen y cambio de presión."
    },
    {
        "id": "B028",
        "system": "Neuromuscular",
        "concept": "Sumación",
        "question": "Una contracción muscular más intensa puede lograrse por:",
        "options": [
            "Reclutamiento de unidades motoras y aumento de frecuencia de descarga.",
            "Eliminación completa de calcio intracelular.",
            "Ausencia de señales nerviosas.",
            "Reducción del número de fibras activas."
        ],
        "answer": "Reclutamiento de unidades motoras y aumento de frecuencia de descarga.",
        "explanation": "La fuerza muscular se regula por cuántas unidades motoras participan y por la frecuencia con que se activan."
    },
    {
        "id": "B029",
        "system": "Musculoesquelético",
        "concept": "Deformación",
        "question": "Un tejido sometido a carga puede deformarse. La magnitud de esa deformación depende, entre otros factores, de:",
        "options": [
            "La carga aplicada, el tiempo de exposición y las propiedades mecánicas del tejido.",
            "Solo del nombre anatómico del tejido.",
            "La voluntad del paciente exclusivamente.",
            "La presión atmosférica sin relación con la carga."
        ],
        "answer": "La carga aplicada, el tiempo de exposición y las propiedades mecánicas del tejido.",
        "explanation": "Los tejidos biológicos tienen comportamiento mecánico dependiente de carga, tiempo y estructura."
    },
    {
        "id": "B030",
        "system": "Endocrino",
        "concept": "Difusión y concentración",
        "question": "Cuando una sustancia se mueve desde una zona de mayor concentración hacia otra de menor concentración, el proceso se asocia con:",
        "options": ["Difusión a favor de gradiente.", "Movimiento contrario al gradiente sin energía.", "Contracción articular.", "Aceleración angular vestibular."],
        "answer": "Difusión a favor de gradiente.",
        "explanation": "La difusión es un proceso esencial para comprender transporte de moléculas y comunicación celular."
    },
    {
        "id": "B031",
        "system": "Cardiopulmonar",
        "concept": "Ventilación-perfusión",
        "question": "Una alteración ventilación/perfusión significa que:",
        "options": [
            "La llegada de aire y la llegada de sangre a zonas pulmonares no están adecuadamente acopladas.",
            "El pulmón deja de tener membranas.",
            "La sangre fluye sin presión.",
            "El oxígeno se mueve sin gradientes."
        ],
        "answer": "La llegada de aire y la llegada de sangre a zonas pulmonares no están adecuadamente acopladas.",
        "explanation": "La eficiencia del intercambio gaseoso requiere relación funcional entre ventilación alveolar y perfusión capilar."
    },
    {
        "id": "B032",
        "system": "Musculoesquelético",
        "concept": "Fricción",
        "question": "En una transferencia de silla a camilla, la fricción entre los pies y el suelo puede ayudar porque:",
        "options": [
            "Permite generar fuerzas de reacción sin que los pies resbalen fácilmente.",
            "Elimina la necesidad de equilibrio.",
            "Reduce la masa corporal a cero.",
            "Bloquea toda señal vestibular."
        ],
        "answer": "Permite generar fuerzas de reacción sin que los pies resbalen fácilmente.",
        "explanation": "La fricción influye en seguridad, estabilidad y capacidad de generar fuerza durante tareas funcionales."
    },
    {
        "id": "B033",
        "system": "Neuromuscular",
        "concept": "Velocidad de conducción",
        "question": "La mielina aumenta la velocidad de conducción nerviosa porque:",
        "options": [
            "Favorece la conducción saltatoria entre nodos de Ranvier.",
            "Convierte el axón en músculo.",
            "Elimina todos los canales iónicos.",
            "Impide cualquier cambio eléctrico."
        ],
        "answer": "Favorece la conducción saltatoria entre nodos de Ranvier.",
        "explanation": "La mielina mejora la eficiencia de propagación de la señal eléctrica."
    },
    {
        "id": "B034",
        "system": "Vestibulococlear",
        "concept": "Frecuencia",
        "question": "En audición, la frecuencia de una onda sonora se relaciona principalmente con:",
        "options": ["La percepción del tono.", "La cantidad de insulina.", "La fuerza del cuádriceps.", "La presión venosa central exclusivamente."],
        "answer": "La percepción del tono.",
        "explanation": "La frecuencia de vibración se relaciona con tonos agudos o graves."
    },
    {
        "id": "B035",
        "system": "Cardiopulmonar",
        "concept": "Retorno venoso",
        "question": "La bomba muscular favorece el retorno venoso porque:",
        "options": [
            "La contracción comprime venas y, junto con válvulas, dirige la sangre hacia el corazón.",
            "La sangre se mueve sin gradientes de presión.",
            "Los músculos convierten la sangre en aire.",
            "Las válvulas venosas invierten el flujo hacia los pies."
        ],
        "answer": "La contracción comprime venas y, junto con válvulas, dirige la sangre hacia el corazón.",
        "explanation": "El movimiento muscular ayuda a vencer efectos gravitacionales y facilita el retorno venoso."
    },
    {
        "id": "B036",
        "system": "Endocrino",
        "concept": "Tiempo de respuesta",
        "question": "Comparadas con señales nerviosas, muchas respuestas endocrinas suelen ser:",
        "options": [
            "Más lentas y sostenidas en el tiempo.",
            "Siempre instantáneas y más rápidas que un reflejo.",
            "Independientes de receptores.",
            "Exclusivas del tejido óseo."
        ],
        "answer": "Más lentas y sostenidas en el tiempo.",
        "explanation": "La señal endocrina depende de liberación, transporte y respuesta en tejidos diana, con cinética generalmente más lenta."
    },
    {
        "id": "B037",
        "system": "Musculoesquelético",
        "concept": "Carga y adaptación",
        "question": "La adaptación del tejido óseo a la carga se entiende mejor como:",
        "options": [
            "Una respuesta biológica a estímulos mecánicos repetidos dentro de rangos tolerables.",
            "Una respuesta inmediata sin relación con fuerzas.",
            "Un proceso que ocurre solo por respiración.",
            "Un fenómeno que no depende de actividad celular."
        ],
        "answer": "Una respuesta biológica a estímulos mecánicos repetidos dentro de rangos tolerables.",
        "explanation": "El hueso responde a cargas mecánicas mediante remodelación, si el estímulo es adecuado y recuperable."
    },
    {
        "id": "B038",
        "system": "Cardiopulmonar",
        "concept": "Temperatura",
        "question": "Durante ejercicio, el aumento de temperatura corporal se relaciona con:",
        "options": [
            "Producción de calor por metabolismo muscular y necesidad de disipación térmica.",
            "Ausencia de metabolismo energético.",
            "Eliminación de toda sudoración.",
            "Detención del flujo sanguíneo cutáneo."
        ],
        "answer": "Producción de calor por metabolismo muscular y necesidad de disipación térmica.",
        "explanation": "La contracción muscular libera calor; el organismo regula temperatura mediante mecanismos como flujo cutáneo y sudoración."
    },
    {
        "id": "B039",
        "system": "Neuromuscular",
        "concept": "Propiocepción",
        "question": "La propiocepción aporta al movimiento funcional porque informa sobre:",
        "options": [
            "Posición y movimiento de segmentos corporales.",
            "Cantidad de oxígeno atmosférico únicamente.",
            "Producción de hormonas tiroideas exclusivamente.",
            "Presión parcial de dióxido de carbono alveolar sin relación motora."
        ],
        "answer": "Posición y movimiento de segmentos corporales.",
        "explanation": "La propiocepción permite ajustar postura, coordinación y control motor."
    },
    {
        "id": "B040",
        "system": "Vestibulococlear",
        "concept": "Integración sensorial",
        "question": "El equilibrio funcional depende de la integración de información:",
        "options": [
            "Vestibular, visual y somatosensorial.",
            "Solo endocrina.",
            "Solo auditiva, sin visión ni propiocepción.",
            "Exclusivamente pulmonar."
        ],
        "answer": "Vestibular, visual y somatosensorial.",
        "explanation": "El control postural integra múltiples entradas sensoriales para orientar el cuerpo en el espacio."
    }
]

# ============================================================
# BASE DE DATOS SQLITE
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_PATH, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_code TEXT UNIQUE,
        student_name TEXT,
        student_email TEXT,
        student_id TEXT,
        started_at TEXT,
        finished_at TEXT,
        score_raw INTEGER,
        score_total INTEGER,
        grade_0_5 REAL,
        passed INTEGER,
        time_seconds INTEGER,
        questions_json TEXT,
        answers_json TEXT
    )
    """)
    conn.commit()
    conn.close()


def save_attempt(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO attempts (
        attempt_code, student_name, student_email, student_id,
        started_at, finished_at, score_raw, score_total, grade_0_5,
        passed, time_seconds, questions_json, answers_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["attempt_code"], data["student_name"], data["student_email"], data["student_id"],
        data["started_at"], data["finished_at"], data["score_raw"], data["score_total"],
        data["grade_0_5"], data["passed"], data["time_seconds"],
        json.dumps(data["questions"], ensure_ascii=False),
        json.dumps(data["answers"], ensure_ascii=False)
    ))
    conn.commit()
    conn.close()


def load_results():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT student_name, student_email, student_id, started_at, finished_at,
           score_raw, score_total, grade_0_5, passed, time_seconds
    FROM attempts
    ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


init_db()

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def make_attempt_code(student_email: str) -> str:
    raw = f"{student_email}-{datetime.now().isoformat()}-{random.random()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def format_seconds(seconds: int) -> str:
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}:{sec:02d}"


def start_attempt(student_name, student_email, student_id):
    selected_questions = random.sample(QUESTION_BANK, NUM_QUESTIONS_PER_ATTEMPT)
    for q in selected_questions:
        random.shuffle(q["options"])

    st.session_state.started = True
    st.session_state.finished = False
    st.session_state.student_name = student_name.strip()
    st.session_state.student_email = student_email.strip().lower()
    st.session_state.student_id = student_id.strip()
    st.session_state.attempt_code = make_attempt_code(student_email)
    st.session_state.started_at = datetime.now().isoformat(timespec="seconds")
    st.session_state.start_time = time.time()
    st.session_state.current_index = 0
    st.session_state.questions = selected_questions
    st.session_state.answers = {}


def calculate_results():
    questions = st.session_state.questions
    answers = st.session_state.answers
    correct = 0
    detail = []

    for q in questions:
        selected = answers.get(q["id"], None)
        is_correct = selected == q["answer"]
        if is_correct:
            correct += 1
        detail.append({
            "id": q["id"],
            "system": q["system"],
            "concept": q["concept"],
            "question": q["question"],
            "selected": selected,
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    total = len(questions)
    grade = round((correct / total) * 5, 2)
    passed = 1 if grade >= PASSING_GRADE else 0
    elapsed = int(time.time() - st.session_state.start_time)

    result_data = {
        "attempt_code": st.session_state.attempt_code,
        "student_name": st.session_state.student_name,
        "student_email": st.session_state.student_email,
        "student_id": st.session_state.student_id,
        "started_at": st.session_state.started_at,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "score_raw": correct,
        "score_total": total,
        "grade_0_5": grade,
        "passed": passed,
        "time_seconds": elapsed,
        "questions": [q["id"] for q in questions],
        "answers": detail
    }
    return result_data

# ============================================================
# INTERFAZ
# ============================================================

st.title("🧬 Cuestionario seguro de Biofísica")
st.caption(COURSE_NAME)

if "started" not in st.session_state:
    st.session_state.started = False
if "finished" not in st.session_state:
    st.session_state.finished = False

if st.session_state.get("started") and not st.session_state.get("finished"):
    watermark_text = f"{st.session_state.student_name} · {st.session_state.student_email}"
    st.markdown(f"<div class='watermark'>{watermark_text}</div>", unsafe_allow_html=True)

if not st.session_state.started:
    st.markdown("""
    Este aplicativo evalúa conceptos biofísicos aplicados a sistemas humanos relevantes para rehabilitación:
    gradiente, flujo, presión, resistencia, energía, temperatura, membrana y retroalimentación.
    """)

    st.markdown("""
    <div class='blocked-box'>
    <b>Condiciones de aplicación:</b><br>
    • El sistema seleccionará 30 preguntas aleatorias del banco disponible.<br>
    • Las opciones se presentarán en orden aleatorio.<br>
    • El cuestionario tiene límite de tiempo.<br>
    • El aplicativo bloquea selección de texto, copiar, pegar, clic derecho e impresión desde atajos comunes.<br>
    • Estas medidas son disuasivas; ningún navegador web impide de forma absoluta fotografías externas de pantalla.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Datos del estudiante")
    with st.form("student_form"):
        student_name = st.text_input("Nombre completo")
        student_email = st.text_input("Correo institucional")
        student_id = st.text_input("Código o documento")
        accept = st.checkbox("Declaro que responderé de forma individual, sin copiar, distribuir o fotografiar el contenido del cuestionario.")
        submitted = st.form_submit_button("Iniciar cuestionario")

    if submitted:
        if not student_name.strip() or not student_email.strip() or not student_id.strip():
            st.error("Debes diligenciar nombre, correo y código/documento.")
        elif "@" not in student_email:
            st.error("Ingresa un correo válido.")
        elif not accept:
            st.warning("Debes aceptar la declaración de honestidad académica para iniciar.")
        else:
            start_attempt(student_name, student_email, student_id)
            st.rerun()

elif st.session_state.started and not st.session_state.finished:
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = (TIME_LIMIT_MINUTES * 60) - elapsed

    if remaining <= 0:
        st.warning("El tiempo terminó. Se guardará el intento con las respuestas registradas.")
        result_data = calculate_results()
        save_attempt(result_data)
        st.session_state.result_data = result_data
        st.session_state.finished = True
        st.rerun()

    st.progress((st.session_state.current_index + 1) / NUM_QUESTIONS_PER_ATTEMPT)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Pregunta", f"{st.session_state.current_index + 1}/{NUM_QUESTIONS_PER_ATTEMPT}")
    with col_b:
        st.metric("Tiempo restante", format_seconds(max(0, remaining)))
    with col_c:
        answered_count = len(st.session_state.answers)
        st.metric("Respondidas", f"{answered_count}/{NUM_QUESTIONS_PER_ATTEMPT}")

    q = st.session_state.questions[st.session_state.current_index]

    st.markdown("<div class='question-card'>", unsafe_allow_html=True)
    st.markdown(f"**Sistema:** {q['system']}  ")
    st.markdown(f"**Concepto biofísico:** {q['concept']}")
    st.subheader(q["question"])

    previous_answer = st.session_state.answers.get(q["id"], None)
    selected = st.radio(
        "Selecciona una respuesta:",
        q["options"],
        index=q["options"].index(previous_answer) if previous_answer in q["options"] else None,
        key=f"radio_{q['id']}"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns([1, 1, 1])

    with nav1:
        if st.button("← Anterior", disabled=st.session_state.current_index == 0):
            if selected:
                st.session_state.answers[q["id"]] = selected
            st.session_state.current_index -= 1
            st.rerun()

    with nav2:
        if st.button("Guardar respuesta"):
            if selected:
                st.session_state.answers[q["id"]] = selected
                st.success("Respuesta guardada.")
            else:
                st.warning("Selecciona una opción antes de guardar.")

    with nav3:
        next_label = "Finalizar" if st.session_state.current_index == NUM_QUESTIONS_PER_ATTEMPT - 1 else "Siguiente →"
        if st.button(next_label):
            if selected:
                st.session_state.answers[q["id"]] = selected
                if st.session_state.current_index == NUM_QUESTIONS_PER_ATTEMPT - 1:
                    unanswered = NUM_QUESTIONS_PER_ATTEMPT - len(st.session_state.answers)
                    if unanswered > 0:
                        st.error(f"Aún tienes {unanswered} pregunta(s) sin responder.")
                    else:
                        result_data = calculate_results()
                        save_attempt(result_data)
                        st.session_state.result_data = result_data
                        st.session_state.finished = True
                        st.rerun()
                else:
                    st.session_state.current_index += 1
                    st.rerun()
            else:
                st.warning("Selecciona una opción antes de continuar.")

    st.divider()
    st.markdown("<p class='small-note'>Recomendación docente: aplicar en sesión controlada. La seguridad técnica reduce filtraciones, pero la validez mejora más con banco amplio, preguntas aplicadas y versiones aleatorias.</p>", unsafe_allow_html=True)

elif st.session_state.finished:
    result = st.session_state.result_data
    st.success("Cuestionario finalizado y guardado correctamente.")

    st.subheader("Resultado")
    c1, c2, c3 = st.columns(3)
    c1.metric("Correctas", f"{result['score_raw']}/{result['score_total']}")
    c2.metric("Nota", f"{result['grade_0_5']}/5.0")
    c3.metric("Tiempo", format_seconds(result["time_seconds"]))

    if result["passed"]:
        st.info("Resultado: aprobado según el punto de corte configurado.")
    else:
        st.warning("Resultado: requiere refuerzo conceptual.")

    st.subheader("Retroalimentación formativa")
    with st.expander("Ver detalle de respuestas"):
        for item in result["answers"]:
            icon = "✅" if item["is_correct"] else "❌"
            st.markdown(f"### {icon} {item['id']} · {item['system']} · {item['concept']}")
            st.write(item["question"])
            st.write(f"**Tu respuesta:** {item['selected']}")
            st.write(f"**Respuesta esperada:** {item['correct_answer']}")
            st.write(f"**Explicación:** {item['explanation']}")
            st.divider()

    if st.button("Cerrar intento"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ============================================================
# PANEL DOCENTE
# ============================================================

st.sidebar.title("Panel docente")
st.sidebar.caption("Acceso básico para revisión local de resultados.")
admin_password = st.sidebar.text_input("Clave docente", type="password")

# Cambiar antes de usar con estudiantes reales.
if admin_password == "biofisica2026":
    st.sidebar.success("Acceso docente habilitado")
    rows = load_results()
    st.sidebar.write(f"Intentos registrados: {len(rows)}")

    if rows:
        import pandas as pd
        df = pd.DataFrame(rows, columns=[
            "nombre", "correo", "codigo", "inicio", "fin",
            "correctas", "total", "nota_0_5", "aprobado", "tiempo_segundos"
        ])
        st.sidebar.download_button(
            label="Descargar resultados CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="resultados_biofisica.csv",
            mime="text/csv"
        )

        with st.expander("📊 Ver resultados docentes"):
            st.dataframe(df, use_container_width=True)

elif admin_password:
    st.sidebar.error("Clave incorrecta")
