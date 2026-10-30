# Plan: limpieza y documentación de `timezone`

Seguimiento del punto 1.4 de `notes/docs_review_plan.md`. Marcar `[x]` al terminar cada paso. Un commit por tema.

## Contexto (verificado)
- El argumento `timezone` de los datasets pamDP (`Media`, `Deployments`, `Observations`, `CSVPamDP`) se guarda en `self.timezone` (`CSVPamDP.py:52`) y **nunca se lee**. Las fechas se normalizan con `pd.to_datetime(...).isoformat()` (`CSVPamDP.py:99-101`, `139-141`), que conserva el offset del texto.
- Las 5 entradas de catálogo con `timezone: Etc/GMT+5` (`conf/base/catalog/data_preparation.yml:4,9,26` y `species_detection.yml:4,9`) **no afectan ninguna salida**.
- El offset real lo fijan los nodos con `params:timezone` (`data_preparation/nodes.py:159` para media, `:271`/`:273` para deployments; `species_detection/nodes.py:167` para `classificationTimestamp`).
- Hay **una sola zona horaria por proyecto**. No hay soporte para deployments en zonas distintas.
- Hecho: bug de `'America/Bogota'` fijo en deployments (commit `f28f084`, con test nuevo).

## Parte A — Quitar el argumento muerto (código)
Decidir antes de empezar:
- [x] A.0 Opción **completa** (quitar `timezone` de los constructores y del catálogo; rompe catálogos locales que lo declaren) u opción **compatible** (dejarlo opcional, ignorado y marcado como obsoleto, con aviso de deprecación). Recomendación: compatible primero, completa en una versión posterior.
- [x] A.1 Buscar usos: `grep -rn "timezone" src/ conf/ docs/ README.md` y revisar `conf/local/catalog.yml` de los usuarios conocidos.
- [x] A.2 Editar `CSVPamDP.py`, `media.py`, `deployments.py` y `observations.py` según A.0.
- [x] A.3 Borrar las 5 líneas `timezone:` de `conf/base/catalog/data_preparation.yml` y `species_detection.yml`.
- [x] A.4 Tests: instanciar cada dataset sin `timezone`; si es la opción compatible, comprobar que pasarlo da un aviso y no un error.
- [x] A.5 Verificar con `scratchpad/snap.py` (antes/después) que el catálogo cargado solo pierde esas claves, y ejecutar `pytest src/tests` (187 tests).
- [x] A.6 Commit aparte, p. ej. `FIX: Remove unused timezone argument from pamDP datasets`.

## Parte B — Documentación
- [x] B.1 `docs/source/documentation/overview.md:39`: quitar `timezone: Etc/GMT+5` del ejemplo de catálogo.
- [x] B.2 Documentar que la zona horaria se define solo en `params:timezone` (`conf/local/parameters.yml`), con nombre IANA (`America/Bogota`), en `beginner_tutorial/data_preparation.md` y README (líneas 74-76).
- [x] B.3 Documentar la **limitación de zona única por proyecto** y la solución provisional: separar los deployments por zona y ejecutar un proyecto (o una temporada, ver `multiseason_config.md`) por cada una.
- [x] B.4 Aclarar en `data_exchange_format.md` que los timestamps salen en ISO 8601 con offset (`+01:00`, `-05:00`).
- [ ] B.5 Commit aparte de documentación.

## Parte C — Mejora futura (fuera de este plan)
- [ ] C.1 Soporte multi-zona: columna `timezone` por deployment en la hoja de despliegues, o mapeo `deploymentID → zona` en los parámetros, con el parámetro global como valor por defecto. Afecta a `field_deployments_sheet.py`, `get_media_file`, `field_deployments_sheet_to_deployments`, la documentación del formato y los tests. Abrir como issue.
- [ ] C.2 Valorar que `classificationTimestamp` use la zona del deployment y no la global.

## Al terminar
- [ ] Marcar 1.4 como hecho en `notes/docs_review_plan.md`.
- [ ] `git status`: `conf/local/parameters.yml` fuera de los commits.
