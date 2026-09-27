# Sistema Experto de Rutas — Transporte Masivo (TransMilenio)

Proyecto para la actividad de **Sistemas Inteligentes Basados en Conocimiento**.
Implementa:

1. Una **base de conocimiento** en reglas lógicas (estaciones, líneas
   troncales y tramos con tiempo de viaje) — ver `src/knowledge_base.py`.
2. Un **motor de reglas** (sistema experto) construido con la librería
   [`experta`](https://github.com/nilp0inter/experta) que deriva el grafo
   de conexiones y detecta las estaciones de transbordo — ver
   `src/rules_engine.py`.
3. Un **algoritmo de búsqueda heurística A\*** que usa ese grafo para
   encontrar la mejor ruta (menor tiempo, considerando penalización por
   transbordo) entre una estación de origen y una de destino — ver
   `src/pathfinding.py`.

> **Nota sobre los datos:** el conjunto de estaciones y tiempos de viaje
> es una versión **simplificada e ilustrativa** de la red troncal de
> TransMilenio, pensada para poder construir y sustentar el sistema
> experto. Los nombres de portales y troncales son reales, pero el
> detalle exacto (orden de estaciones intermedias y minutos entre ellas)
> es aproximado. Si necesitan mayor precisión, pueden reemplazar
> `src/knowledge_base.py` con datos oficiales (por ejemplo del portal de
> datos abiertos de TransMilenio / GTFS) sin tocar el resto del código.

## 1. Requisitos

- Python 3.9, 3.10, 3.11 o 3.12.
- pip

## 2. Instalación

```bash
git clone <URL-DE-SU-REPOSITORIO>
cd <carpeta-del-proyecto>

python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Si `pip install experta` falla

`experta` es una librería algo antigua. Si da error de instalación,
intenten:

```bash
pip install frozendict==1.2
pip install experta --no-deps
```

El código ya incluye un parche de compatibilidad (en
`src/rules_engine.py`) para que `experta` funcione en Python 3.10+.

## 3. Ejecución

Listar todas las estaciones disponibles:

```bash
python src/cli.py --listar
```

Calcular la mejor ruta entre dos estaciones:

```bash
python src/cli.py --origen PortalSuba --destino PortalNorte
```

Modo interactivo (si no se pasan --origen/--destino, el programa
pregunta):

```bash
python src/cli.py
```

Ejemplo de salida:

```
Mejor ruta encontrada: PortalSuba -> PortalNorte
Tiempo total estimado: 33.0 minutos
Transbordos necesarios: 2

  1. PortalSuba -> SubaTV91      [Línea Suba, 3 min]
  2. SubaTV91 -> HumedalCordoba  [Línea Suba, 3 min]
  3. HumedalCordoba -> MinutoDeDios [Línea Suba, 3 min]
  4. MinutoDeDios -> SimonBolivar   [Línea Suba, 2 min]
  5. SimonBolivar -> ElPolo         [Línea Calle80, 2 min]  <-- TRANSBORDO
  ...
```

## 4. Pruebas automatizadas

```bash
pytest -v
```

Los resultados de estas pruebas (capturas de pantalla + tabla de casos)
son la base para el documento PDF de pruebas que pide la actividad. Hay
una plantilla lista en `docs/plan_pruebas.md`.

## 5. Estructura del proyecto

```
transmilenio_router/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── knowledge_base.py   # Base de conocimiento (hechos)
│   ├── rules_engine.py     # Motor de reglas (experta)
│   ├── pathfinding.py      # Búsqueda heurística A*
│   └── cli.py              # Punto de entrada / interfaz de consola
├── tests/
│   ├── test_rules_engine.py
│   └── test_pathfinding.py
└── docs/
    ├── plan_pruebas.md     # Plantilla para el documento PDF de pruebas
    └── arquitectura.md     # Explicación breve para el video/sustentación
```

## 6. Flujo de trabajo en Git para el equipo (obligatorio para la entrega)

El enunciado pide que el **log del repositorio evidencie el trabajo de
cada integrante**. Sugerencia de flujo:

1. Una sola persona crea el repositorio en GitHub/GitLab y sube esta
   base de código con un primer commit.
2. Agreguen al **tutor como colaborador** del repositorio (Settings →
   Collaborators en GitHub, o Members en GitLab).
3. Cada integrante trabaja en su propia rama:

   ```bash
   git checkout -b feature/nombre-integrante
   # hacer cambios...
   git add .
   git commit -m "Descripción clara del cambio"
   git push origin feature/nombre-integrante
   ```

4. Cada quien abre un Pull Request / Merge Request hacia `main` para que
   quede registrado quién hizo qué.
5. Repartan el trabajo por módulo, por ejemplo:
   - Integrante 1: `knowledge_base.py` + datos de la red.
   - Integrante 2: `rules_engine.py` (reglas del sistema experto).
   - Integrante 3: `pathfinding.py` (algoritmo de búsqueda).
   - Integrante 4: pruebas (`tests/`), documento de pruebas y video.

Esto garantiza que el historial de commits (`git log`) muestre el aporte
real de cada persona, que es justo lo que se va a revisar.

## 7. Entregables de la actividad

- [ ] Código fuente en Python (este repositorio) + instrucciones (este README).
- [ ] Documento PDF con las pruebas realizadas (usar `docs/plan_pruebas.md`
      como base y exportarlo a PDF una vez completado con resultados reales).
- [ ] Video (máx. 10 min) explicando el proyecto, comandos y resultados,
      con la participación de todos los integrantes.
- [ ] Repositorio Git con el tutor agregado como colaborador y el log de
      commits evidenciando el trabajo de cada integrante.
