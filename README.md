# Cuestionario seguro de Biofísica

Aplicativo web en Streamlit para aplicar un cuestionario de Biofísica a estudiantes de ciencias de la rehabilitación.

## Funciones principales

- Banco inicial de 40 preguntas.
- Selección aleatoria de 30 preguntas por intento.
- Opciones de respuesta aleatorizadas.
- Una pregunta por pantalla.
- Tiempo límite configurable.
- Nota automática de 0 a 5.
- Base de datos local SQLite.
- Panel docente con descarga de resultados en CSV.
- Marca de agua dinámica con nombre y correo del estudiante.
- Bloqueos disuasivos de copiar, pegar, clic derecho, impresión y selección de texto.

## Advertencia académica importante

Las medidas contra copiar, pegar y pantallazos son disuasivas. Una aplicación web no puede impedir de forma absoluta que alguien tome una foto externa de la pantalla con otro dispositivo. Para mejorar la seguridad evaluativa se recomienda usar banco amplio de preguntas, versiones aleatorias, tiempo limitado, aplicación supervisada y preguntas aplicadas de razonamiento.

## Instalación local

1. Instalar Python.
2. Abrir la terminal en esta carpeta.
3. Ejecutar:

```bash
pip install -r requirements.txt
```

4. Ejecutar la app:

```bash
streamlit run app.py
```

## Base de datos

La app crea automáticamente el archivo:

```text
resultados_biofisica.db
```

Ese archivo contiene los intentos de los estudiantes. No se recomienda subirlo a GitHub con datos reales.

## Clave docente

La clave inicial del panel docente es:

```text
biofisica2026
```

Se recomienda cambiarla en `app.py` antes de usar la aplicación con estudiantes.

## Subir a GitHub

Sube estos archivos al repositorio:

- `app.py`
- `requirements.txt`
- `README.md`
- `.gitignore`

No subas archivos `.db` con información real de estudiantes.

## Despliegue sugerido

Puede ejecutarse localmente o publicarse en Streamlit Community Cloud conectando el repositorio de GitHub.
