# Plan de corrección de la documentación (rama dev): pendientes

Las fases 0 a 4 de la revisión están hechas (4.10 descartado). `sphinx -W` pasa sin warnings, `linkcheck` solo muestra la redirección benigna del DOI de Zenodo y `pytest` da 187 passed. Este archivo conserva únicamente lo que sigue abierto. Marcar `[x]` al terminar cada paso. Un commit por tema.

## Verificación final (en curso)
- [ ] Resultado del run `pamflow run --env=verify` (pipeline por defecto) y de `pamflow run --env=verify --pipeline=export`, con salida en una carpeta temporal. Comprobar que las entradas y salidas coinciden con lo documentado. `detection_validation` no se incluye: requiere anotaciones manuales revisadas.
- [ ] Borrar `conf/verify/` (carpeta temporal de esta verificación, no se commitea).
- [ ] `git status`: `conf/local/parameters.yml` fuera de los commits (punto 0.4, precaución permanente).

## Decisiones abiertas
- [ ] **DOI de Zenodo** (`beginner_tutorial/detection_validation.md:6`, texto `TODO: insert Zenodo DOI`): decidir si el archivo de anotaciones está en el DOI 10.5281/zenodo.16922848, en otro, o si se quita el tip.
- [ ] **Plantilla xlsx**: el error de `FieldDeployments` menciona una "provided template" que no existe. Incluir la plantilla o quitar la frase.
- [ ] **`captureMethod` y `fileMediatype`** (decidido no alinear por ahora): el enum documentado en `data_exchange_format.md` (`recordingSchedule, continuous, activityDetection`) difiere del validado en `media.py:88` (`activityDetection, timeLapse`), y `data_preparation/nodes.py:151` fija `audio/WAV` en vez del valor IANA `audio/wav`.

## Zona horaria (punto 1.4, detalle en `notes/timezone_cleanup_plan.md`)
- [ ] Parte A: quitar el argumento `timezone` sin uso de los datasets pamDP y de 5 entradas de catálogo. Decidir entre la opción completa o la compatible con aviso de deprecación.
- [ ] Parte B: documentar `params:timezone`, la limitación de zona única por proyecto y quitar el ejemplo `Etc/GMT+5` de `overview.md:39`.
- [ ] Parte C: soporte multi-zona (mejora futura, abrir como issue).

## Limpieza de código fuera de este plan
- [ ] Eliminar `src/pamflow/pipelines/data_science/`, su import y sus entradas de registro (decidido en 1.2).
- [ ] Nodo `CSA_eventos` comentado y entrada de catálogo `DwC_eventos` sin nodo (1.3): decidir si se eliminan.
- [ ] Decidir si se conserva el alias de pipeline `pamflow` junto a `__default__`.
- [ ] Carpeta `build/` obsoleta en la raíz del repo (ignorada por git): borrar.
