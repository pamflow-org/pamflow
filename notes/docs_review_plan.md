# Plan de corrección de la documentación (rama dev)

Docs en Sphinx (`docs/source/`, toctrees en `index.md` y en los `index.md` de cada sección) y `README.md`.
Los hallazgos vienen de una exploración y **no están verificados línea por línea**: comprobar cada punto antes de editar.
Marcar `[x]` al terminar cada paso. Un commit por fase.

---

## Fase 0 — Verificación previa
- [x] 0.1 (confirmado: falla con `media_work.csv` no encontrado; `__default__`/`pamflow` no incluyen `filter_media`) Ejecutar `kedro run` (y `pamflow run`) sobre los datos del tutorial en un entorno limpio. Confirmar si falla porque `media_work@pamDP` no existe (`pipeline_registry.py:30-46`, `pipelines/filter_media/pipeline.py:14`).
- [x] 0.2 (línea base: 18 warnings; 9 de encabezados H1, 1 documento huérfano, 8 enlaces/anclas rotas; build en scratchpad, fuera del repo) `sphinx-build -W -b html docs/source /tmp/docs_out` para tener la línea base de warnings (documentos huérfanos, anclas rotas).
- [x] 0.3 (186 passed) `pytest src/tests` para confirmar la línea base.
- [ ] 0.4 **No commitear** `conf/local/parameters.yml` (tiene una ruta personal sin commitear).

## Fase 1 — Decisiones de código (confirmar con el equipo antes de tocar)
- [x] 1.1 (hecho: `with_filter_media` envuelve `__default__` y `pamflow` en `pipeline_registry.py`) `filter_media` en `__default__` y `pamflow`: añadirlo, o hacer que los pipelines lean `media@pamDP` cuando no hay filtro. Depende del resultado de 0.1.
- [x] 1.2 Decisión: `data_science` se va a borrar y **no se documenta**. (Pendiente aparte, fuera de este plan de docs: eliminar `src/pamflow/pipelines/data_science/`, su import y las entradas `data_science` y `pamflow + data_science_pipeline` en `pipeline_registry.py`.)
- [x] 1.3 (hecho: borrados `export.yml`, `figures.yml`, `timelapse.yml` y `data_preparation.yml` de parameters; catálogo sin cambios. Pendiente aparte: nodo `CSA_eventos` comentado y `DwC_eventos` sin nodo) Archivos mal ubicados en `conf/base/parameters/`: `export.yml`, `figures.yml` y `timelapse.yml` contienen entradas de catálogo que duplican o contradicen `conf/base/catalog/`. `data_preparation.yml` está vacío. `DwC_eventos@pandas` no tiene nodo.
- [ ] 1.4 (a hecho: bug `America/Bogota` fijo en `field_deployments_sheet_to_deployments`; pendiente (b) fuente única de timezone vía globals y (c) documentar zona única por proyecto; el resto en `notes/timezone_cleanup_plan.md`) `timezone: Etc/GMT+5` fijo en `conf/base/catalog/data_preparation.yml:4,9,26` y `species_detection.yml:4,9`. Hacer que siga el parámetro `timezone` o documentarlo.
- [x] 1.5 (hecho en 3e4995b y edbd24a: versión leída de pyproject, borrados setup.py y requirements.txt, añadidos build-system y requires-python >=3.10,<3.12, badge 3.10/3.11) Versiones: usar `pyproject.toml` (1.1.0) como fuente única. Actualizar o borrar `src/__init__.py` (0.1), `src/setup.py` y `src/requirements.txt` (kedro 0.18). Alinear el badge de Python del README (3.9-3.11) con el texto (3.11).
- [ ] 1.6 Retoques de código: typo `paramteres.yml` en `species_detection/nodes.py:224`; docstring de `compute_ADI` (dice ACI) en `acoustic_indices/utils.py:82`; comentario en español en `pipeline_registry.py:36`.

## Fase 2 — Correcciones solo de documentación (mayores)
- [ ] 2.1 **Rutas de configuración**: sustituir `conf/base/parameters.yml` y `catalog.yml` por `conf/base/parameters/*.yml` y `conf/base/catalog/*.yml`.
  Archivos: `documentation/overview.md:22,25,29,31`, `advanced_tutorials/multiseason_config.md:10-11`, `advanced_tutorials/custom_pipeline.md:20`, y los comentarios de cabecera de `conf/local/catalog.yml` y `conf/local/parameters.yml`.
- [ ] 2.2 **Hoja de despliegues** (`data_standardization/data_exchange_format.md:29-51`, README 3.x):
  - Reescribir según `datasets/pamDP/field_deployments_sheet.py:56-130`: las 19 columnas deben existir; son obligatorios los valores de `deploymentID`, fechas y horas de inicio/fin, `latitude` y `longitude`.
  - `recorderModel` y `recorderConfiguration` no son obligatorios.
  - Corregir `recorderID` a `deploymentID` (el código usa `data_preparation/nodes.py:121`).
  - El nombre del archivo es configurable.
  - Valorar añadir una plantilla xlsx.
- [ ] 2.3 **Species detection** (`documentation/pipeline_details.md:79-95`, `beginner_tutorial/species_detection.md`, `conf/base/parameters/species_detection.yml:6`):
  - Documentar `segment_length` (3.0), `classifier_model_path` y `classifier_labels_path`.
  - Corregir la semántica de `manual_annotations_file_name`: el código sustituye la palabra `species` por `Genus_species`.
  - Corregir los inputs de los nodos: `params:species_detection_parameters` completo más `params:timezone`, y `segment_length` en `create_segments_node`.
  - Listar todas las salidas: `segments.csv`, `segments/`, `manual_annotations/`, `observations_summary`, `observations_per_species`.
- [ ] 2.4 **Valores y salidas de QC**:
  - `timelapse.sample_length` es 1, no 5 (`pipeline_details.md:62`, `beginner_tutorial/quality_control.md:39`).
  - `deployment_location.png` pasa a `.pdf`.
  - Nombrar `survey_effort.pdf`, `audio_outliers.pdf/csv` y `sensor_performance_data.csv`.
  - Añadir una subsección sobre audio outliers al tutorial de QC y al README.
- [ ] 2.5 **Inputs de nodos** (`pipeline_details.md:79,81,84,113,163`): `media@pamDP` pasa a `media_work@pamDP`. En data_preparation añadir `params:timezone` (líneas 18 y 20) y corregir "requires no parameters" (línea 13).
- [ ] 2.6 **Pipelines sin documentar**:
  - Documentar `export` (`media_gbif.csv`, `deployments_gbif.csv`, `observations_gbif.csv`).
  - Documentar `filter_media` y `deployments_filter`.
  - Añadir la lista completa de nombres válidos de `--pipeline`: `data_preparation`, `quality_control`, `graphical_soundscape`, `acoustic_indices`, `species_detection`, `detection_validation`, `export`.
  - Documentar `pamflow_gui.py`.
  - Añadir `export/` al árbol de salidas del README.
  - Usar `pamflow run` y `kedro run` de forma coherente, y dar el comando de `kedro viz`.
- [ ] 2.7 **Navegación y enlaces**:
  - `getting_involved/index.md` está huérfano y su caption dice "Advanced tutorial". Incluirlo en el toctree y corregir el caption.
  - Enlaces placeholder `https://github.com/` en `advanced_tutorials/custom_acoustic_indices.md:7,9`.
  - Anclas rotas en `beginner_tutorial/species_detection.md:26` (`#4-target-species-list`) y `:28` (`#observations` en minúscula).
  - Unificar la organización de GitHub (`pamflow/` frente a `pamflow-org/`).
  - Completar o quitar el `TODO` del DOI de Zenodo en `detection_validation.md:6`.
  - Enlaces a Kedro `1.0.0` (`overview.md:42`, `running_the_workflow.md:27`) cuando el proyecto usa 0.19.8; también `conf/README.md:25`.

## Fase 3 — Higiene del build de docs
- [x] 3.1 (hecho: `docs/source/_build/` en `.gitignore` y desindexado; los `.DS_Store` no estaban trackeados) `git rm -r --cached docs/source/_build` y los `.DS_Store`. Añadirlos a `.gitignore` y quitar líneas duplicadas (`pamflow_tutorial_data`).
- [ ] 3.2 `docs/source/conf.py`:
  - Cambiar `author = "Kedro"` (líneas 31, 177, 192, 207).
  - Arreglar `sys.path.insert` (apunta a `docs/src`).
  - Quitar `html_static_path` y `mathjax` duplicados (líneas 115/128 y 52/54).
  - Leer la versión desde `pyproject.toml`.
- [ ] 3.3 `docs_requirements.txt`: añadir `ipykernel` (lo necesita `nbsphinx`).
- [ ] 3.4 `conf/README.md`: rellenar la sección vacía "Instructions" o sustituir el README genérico de Kedro.
- [ ] 3.5 CI: `sphinx-build -W` y `linkcheck`.

## Fase 4 — Correcciones menores
- [ ] 4.1 Erratas: ownload, clonned, paramters, "Trouble Shooting", estandardization, Additonal, "taxa ." y "standardize" por "standardizes" (`index.md:12`). Unificar `graphical_soundscape` (`detection_validation.md:40` dice `graphical_soundscapes`).
- [ ] 4.2 README: sección "3.3" duplicada (líneas 56 y 59), mención a la versión anonimizada (línea 12), y aclarar que `conf/local/*.yml` ya existen.
- [ ] 4.3 `.WAV` frente a `.wav` (el código acepta ambos), `audio/wav` frente al `audio/WAV` fijo, y `captureMethod` fijo en `activityDetection`.
- [ ] 4.4 Duración de grabación: `input_data.md:14` (30 s cada 30 min) frente a `quality_control.md:15,19` (1 min).
- [ ] 4.5 `data_exchange_format.md`: nota de que `deploymentTags` y similares son del estándar pamDP y no los genera el pipeline; ejemplo de modelo `BirdNET v2.3` frente a `Birdnet 2.4`.
- [ ] 4.6 `beginner_tutorial/species_detection.md`: columnas `classifiedBy` y `classificationTimestamp`, valores aceptados en la validación, y el umbral "0.1" (el código no fija umbral).
- [ ] 4.7 `custom_classifier.md`: rutas inconsistentes (`data/custom_classifier/` frente a `data/input/custom_classifier/`), el "support for custom classifiers" inexistente, y la afirmación sin verificar sobre el filtro de localización.
- [ ] 4.8 `custom_pipeline.md`: `[your_project]` pasa a `pamflow`; `"__default__": my_pipeline` reemplaza el default (usar suma de pipelines); frase "command we discussed earlier".
- [ ] 4.9 `multiseason_config.md`: texto residual (línea 47), "### 3." duplicado (46 y 51), mezcla `wet_2023`/`wet_2024` (17, 59, 83, 119) y árbol de `conf/base` incompleto.
- [ ] 4.10 `contributing_guidelines.md`: prefijos de commit (BUILD/DOC/FEAT/FIX/TEST) frente al historial real (FEATURE/DOCS), y flake8 frente a ruff.
- [ ] 4.11 Terminología: sensor/recorder/ARU/deployment, BirdNET/Birdnet, timelapse/time-lapse. Elegir un término y aplicarlo.
- [ ] 4.12 Texto alternativo en imágenes (`quality_control.md:17,27,34,43-44`), líneas en blanco dentro de los toctree (`beginner_tutorial/index.md:29-31`, `advanced_tutorials/index.md:13-17`), y salidas de graphical soundscape (`.csv` y `.png` en la misma carpeta).
- [ ] 4.13 Mencionar en el índice del tutorial que acoustic indices y graphical soundscapes no tienen tutorial, o crearlos.

## Verificación final
- [ ] `sphinx-build -W -b html docs/source /tmp/docs_out` sin warnings, y `-b linkcheck`.
- [ ] `kedro run` y `pamflow run --pipeline <cada uno>` sobre los datos del tutorial: las entradas y salidas coinciden con lo documentado.
- [ ] `pytest src/tests`.
- [ ] `git status`: `conf/local/parameters.yml` fuera del commit.
