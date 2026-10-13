# Plan de corrección de la documentación (rama dev): pendientes

Las fases 0 a 4 de la revisión están hechas (4.10 descartado). `sphinx -W` pasa sin warnings, `linkcheck` solo muestra la redirección benigna del DOI de Zenodo y `pytest` da 187 passed. Este archivo conserva únicamente lo que sigue abierto. Marcar `[x]` al terminar cada paso. Un commit por tema.

## Verificación final (en curso)
- [x] (hecho: ambos terminan sin errores y las salidas coinciden con lo documentado) Run del pipeline por defecto y de `export` sobre los datos del tutorial, con salida temporal. `detection_validation` no se incluye: requiere anotaciones manuales revisadas.
- [x] Borrar `conf/verify/` (carpeta temporal de esta verificación, no se commitea).
- [x] `git status`: `conf/local/parameters.yml` fuera de los commits (punto 0.4, precaución permanente).

## Decisiones abiertas
- [ ] **Anotaciones simuladas en Zenodo**: el tutorial (`detection_validation.md`) ya enlaza el DOI 10.5281/zenodo.16922848 y asume que los 7 `.xlsx` simulados (con `filePath` relativos) están incluidos en ese dataset. Subirlos al registro de Zenodo (están en `~/Downloads/pamflow_simulated_annotations/`, junto con `simulate_annotations.py`).
- [ ] **Plantilla xlsx**: el error de `FieldDeployments` menciona una "provided template" que no existe. Incluir la plantilla o quitar la frase.
- [ ] **`captureMethod` y `fileMediatype`** (decidido no alinear por ahora): el enum documentado en `data_exchange_format.md` (`recordingSchedule, continuous, activityDetection`) difiere del validado en `media.py:88` (`activityDetection, timeLapse`), y `data_preparation/nodes.py:151` fija `audio/WAV` en vez del valor IANA `audio/wav`.

## Zona horaria (punto 1.4, detalle en `notes/timezone_cleanup_plan.md`)
- [ ] Parte A: quitar el argumento `timezone` sin uso de los datasets pamDP y de 5 entradas de catálogo. Decidir entre la opción completa o la compatible con aviso de deprecación.
- [ ] Parte B: documentar `params:timezone` y la limitación de zona única por proyecto. El ejemplo `Etc/GMT+5` de `overview.md` ya se sustituyó por la entrada `field_deployments_sheet@pandas`.
- [ ] Parte C: soporte multi-zona (mejora futura, abrir como issue).

## Limpieza de código fuera de este plan
- [ ] Eliminar `src/pamflow/pipelines/data_science/`, su import y sus entradas de registro (decidido en 1.2).
- [ ] Nodo `CSA_eventos` comentado y entrada de catálogo `DwC_eventos` sin nodo (1.3): decidir si se eliminan.
- [ ] Decidir si se conserva el alias de pipeline `pamflow` junto a `__default__`.
- [ ] Carpeta `build/` obsoleta en la raíz del repo (ignorada por git): borrar.
