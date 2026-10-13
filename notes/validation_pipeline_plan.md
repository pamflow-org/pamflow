# Plan: pipeline `detection_validation`

Pipeline nuevo para estimar, por especie, la relación entre el score del
clasificador (`classificationProbability`) y la probabilidad de que la
detección sea correcta, a partir de las anotaciones manuales de segmentos
generadas por `species_detection`. El producto final es un **umbral de
trabajo recomendado por especie**, acompañado de un diagnóstico explícito de
si el modelo tiene respaldo estadístico suficiente o si hace falta anotar
más muestras.

## Idioma de implementación
Si bien este plan está en inglés, usar docstrings y nombres de variables **simpre en inglés**.

## Limitación metodológica (define todo el diseño)

El workflow solo valida segmentos que el modelo **ya marcó como detección**.
No hay revisión independiente del audio para encontrar llamados que el
modelo no detectó. Por lo tanto:

- **No hay falsos negativos, no hay recall, no hay F1.** Cualquier "recall"
  calculado sobre la muestra anotada sería relativo solo a los positivos
  confirmados dentro de esa muestra, no al recall ecológico real — se
  descarta por engañoso.
- Todo lo que se estima es **P(detección correcta | score)**: dada una
  detección con cierto score, ¿qué tan probable es que sea real?

## Enfoque: regresión logística por especie

En vez de barrer umbrales y calcular precisión sobre subconjuntos anidados,
se ajusta un modelo por especie sobre las anotaciones:

```
positive ~ score        (familia binomial, link logit)
```

Ventajas frente al barrido de umbrales:

- **Usa toda la muestra en todo el rango.** Con ~20 anotaciones por especie,
  el barrido parte la muestra en subconjuntos cada vez más chicos y se queda
  sin datos justo en los umbrales altos, que son los que interesan. La
  regresión estima una sola curva con las 20 observaciones completas.
- **El umbral sale en forma cerrada**, sin búsqueda sobre una grilla ni
  problemas de monotonicidad: la curva ajustada es monótona por
  construcción.
- **La calibración es el modelo mismo.** El panel de "precisión observada
  por bin de score" desaparece porque la curva ajustada, graficada contra
  las anotaciones individuales, ya *es* el diagnóstico de calibración — y sin
  el problema de tener 2 anotaciones por bin.
- **Da un criterio formal de validez**: el test de razón de verosimilitud
  contra el modelo nulo (ver abajo).

### Interpretación del umbral (importante, cambia respecto al plan anterior)

La curva ajustada da la probabilidad **puntual** de que una detección *con
ese score exacto* sea correcta — no la precisión acumulada de todas las
detecciones por encima del umbral. Son cosas distintas: si la curva es
creciente, la precisión acumulada por encima de `t` es **mayor** que el
valor puntual en `t`.

Esto significa que el criterio puntual es **conservador**, lo cual está
bien, y además es más directo de comunicar: *"una detección con score ≥ 0.72
tiene al menos 90% de probabilidad de ser correcta para esta especie"*.

### Validación del modelo: modelo nulo vs. modelo logístico

Para cada especie se comparan:

- **Modelo nulo**: solo intercepto. Equivale a decir que la probabilidad de
  acierto es constante y **el score no aporta información** para esa especie.
- **Modelo completo**: intercepto + score.

Test de razón de verosimilitud: `LR = 2·(loglik_completo − loglik_nulo)`,
distribuido χ² con 1 grado de libertad → **p-value**. En `statsmodels` esto
sale directo del ajuste (`res.llr`, `res.llr_pvalue`, `res.llnull`,
`res.llf`), no hay que implementar nada.

- `p < significance_level` → el score discrimina; la curva es utilizable
  para fijar el umbral.
- `p ≥ significance_level` → **no se puede recomendar umbral**.

**Advertencia que hay que respetar al leer el resultado:** un p-value no
significativo *no distingue* entre "el score no sirve para esta especie" y
"no hay muestra suficiente para detectarlo". No rechazar el nulo no es
evidencia a favor del nulo. Por eso el reporte incluye siempre, junto al
p-value, **el coeficiente `b1` y su intervalo de confianza**, que sí
distingue los dos casos:

| Situación | Lectura |
|---|---|
| IC de `b1` ancho, incluye 0 pero también valores grandes | Falta muestra — anotar más segmentos |
| IC de `b1` angosto alrededor de 0 | El score genuinamente no discrimina para esta especie |
| IC de `b1` enteramente > 0 | El score discrimina; usar la curva |

Sin esa distinción, el p-value solo no responde la pregunta que se le está
haciendo.

### Transformación del score (opcional, un parámetro)

El score de BirdNET sale de una sigmoide, así que `logit(score)` recupera el
logit subyacente y hace que la regresión logística sea una **recalibración
lineal** (equivalente a Platt scaling) en vez de un ajuste sobre una escala
ya comprimida. Suele ajustar mejor.

Parámetro `score_transform: identity | logit`, por defecto `identity` por
simplicidad. Vale la pena probar `logit` y comparar el AIC. Si se usa,
recortar los scores a `[ε, 1−ε]` para evitar infinitos.

## Registro y estructura

Pipeline independiente en `pipeline_registry.py`, **no** concatenado en
`pamflow_pipeline` ni en `__default__`, porque depende de un paso humano
intermedio (llenar la columna `positive` en los `.xlsx` de
`manual_annotations`) — mismo criterio que ya se aplica a `data_science`.

```
data/output/detection_validation/
├── validated_annotations.csv           # anotaciones compiladas y normalizadas
├── precision_model_fits.csv            # 1 fila por especie: coeficientes, LR test, diagnósticos, estado
├── precision_curves.csv                # tabla larga: scientificName × score → probabilidad ajustada + IC (para graficar)
├── detection_validation_summary.csv    # 1 fila por especie: umbral recomendado + contexto para decidir
├── plots/                              # 1 figura por especie (PartitionedDataset)
│   ├── Amazona_farinosa.pdf
│   ├── Ara_severus.pdf
│   └── ...
└── detection_validation_overview.pdf   # infográfico agregado, estilo observations_summary.pdf
```

- Catálogo nuevo: `conf/base/catalog/detection_validation.yml`
- Parámetros nuevos: `conf/base/parameters/detection_validation.yml`
- El plot por especie usa el mismo patrón de `quality_control.yml`
  (`partitions.PartitionedDataset` + `dataset: matplotlib.MatplotlibWriter`).

## Nodos (`src/pamflow/pipelines/detection_validation/nodes.py`)

### 1. `compile_manual_annotations(manual_annotations, positive_values, negative_values, uncertain_values, uncertain_handling)`

- Entrada: `manual_annotations@PartitionedDataset` (los `.xlsx` por especie
  que produce `species_detection`).
- Concatena todas las hojas.
- Normaliza la columna `positive` a tres categorías —
  `positive` / `negative` / `uncertain` — casteando a `str` y aplicando
  `.strip().lower()` antes de comparar.
- **Falla ruidosamente**: si aparece un valor no vacío que no está en
  ninguna de las tres listas, lanza error listando los valores no
  reconocidos y en qué archivo aparecen. Descartarlos en silencio como "sin
  anotar" es la forma más fácil de perder muestra que no sobra (un `"Si "`
  con espacio, un `"1.0"` que Excel convirtió a float).
- Las celdas vacías sí se descartan como pendientes, loggeando cuántas
  quedan por especie.
- Arrastra columnas útiles aunque no se usen todavía: `detectedSpecies`,
  `deploymentID`, identificador estable del segmento.
- Aplica `uncertain_handling`:
  - `exclude` (por defecto): los `uncertain` se excluyen del ajuste pero se
    cuentan y reportan.
  - `positive` / `negative`: los recodifica, para correr el pipeline dos
    veces y obtener **cotas** del umbral. Si la banda entre ambas corridas
    es ancha, eso mismo es el hallazgo: la anotación no es concluyente y hay
    que revisar el protocolo o el material.
- Salida → `validated_annotations@pandas`.

### 2. `fit_precision_models(validated_annotations, params)`

Por especie, con chequeos previos:

- `n_annotated < min_annotations` → estado `insufficient_sample`, no se
  ajusta.
- menos de `min_per_class` positivos o negativos → estado
  `insufficient_sample`. Con un solo predictor la regla práctica pide del
  orden de 10 casos de la clase minoritaria; por debajo de eso el ajuste es
  inestable aunque converja.
- **Separación perfecta** (todos los positivos por encima de todos los
  negativos): `statsmodels` no converge o devuelve coeficientes enormes con
  errores estándar infinitos. Capturarla explícitamente → estado
  `separation`. El umbral queda entre los dos grupos pero no es estimable
  con precisión; conviene reportarlo como tal en vez de dejar pasar un
  número inventado.

Si pasa los chequeos, ajusta `sm.Logit(y, sm.add_constant(f(score)))` y
guarda por especie:

`b0`, `b1`, `b1_se`, `b1_ci_low`, `b1_ci_high`, `loglik_null`, `loglik_full`,
`lr_stat`, `p_value`, `pseudo_r2` (McFadden), `aic`, `n_annotated`,
`n_positive`, `n_negative`, `n_uncertain`, `status`.

Segunda salida: `precision_curves` — grilla de scores × especie con la
probabilidad ajustada y su intervalo de confianza
(`res.get_prediction(grid).conf_int()`, que ya devuelve el IC en la escala
de probabilidad).

Salidas → `precision_model_fits@pandas`, `precision_curves@pandas`.

### 3. `recommend_thresholds(precision_model_fits, target_precision)`

Invierte la curva ajustada en forma cerrada:

```
f(t*) = (logit(target_precision) − b0) / b1
t*    = f⁻¹( … )        # identidad o sigmoide, según score_transform
```

Estados posibles por especie:

| `status` | Significado |
|---|---|
| `ok` | Modelo significativo, `b1 > 0`, `t*` dentro del rango de scores observado |
| `insufficient_sample` | Muestra insuficiente para intentar el ajuste |
| `score_not_informative` | `p ≥ significance_level` — revisar el IC de `b1` para saber si falta muestra o si el score no sirve |
| `negative_slope` | `b1 < 0` — el score se comporta al revés; casi siempre indica un problema en los datos o en la anotación, hay que mirarlo |
| `target_unreachable` | `t* > max(score)` — ni el score más alto observado alcanza `target_precision` |
| `target_always_met` | `t* < min(score)` — todas las detecciones ya superan el objetivo |
| `separation` | Separación perfecta; umbral no estimable con precisión |

Agrega `n_annotated`, `n_positive`, `n_negative`, `n_uncertain`, `p_value`,
`b1_ci_low`, `b1_ci_high` y la probabilidad ajustada en `t*`.

Salida → `detection_validation_summary@pandas`.

### 4. `plot_precision_models(validated_annotations, precision_curves, detection_validation_summary)`

Una figura por especie, un solo panel:

- Anotaciones individuales como puntos en `y ∈ {0, 1}` con jitter vertical,
  posicionados por su score.
- Curva logística ajustada con banda de IC.
- Línea horizontal en `target_precision`, línea vertical en `t*`.
- Anotación de texto en la esquina: `n`, `n_positive`/`n_negative`, p-value,
  pseudo-R², `status`. Los números tienen que estar visibles en la figura;
  una curva bonita ajustada sobre 12 puntos no debería poder mirarse sin ver
  que son 12 puntos.
- Para especies con `status != ok`, graficar igual pero sin línea de umbral
  y con el estado marcado en el título.

Generador tipo `create_segments_folder` (yield `{especie: fig}`).

Salida → `detection_validation_plots@PartitionedDataset`.

### 5. `plot_validation_overview(detection_validation_summary)`

Infográfico agregado estilo `plot_observations_summary` (tarjetas): nº
especies con umbral recomendado, nº total de segmentos anotados, nº de
`uncertain`, distribución de umbrales recomendados, y conteo de especies por
`status` — para ver de un vistazo cuántas quedaron sin umbral y por qué.

Salida → `detection_validation_overview@matplotlib`.

## Parámetros (`detection_validation_parameters`)

```yaml
detection_validation_parameters:
  target_precision: 0.9          # probabilidad mínima de acierto deseada en el umbral
  significance_level: 0.05       # umbral del LR test (modelo nulo vs. logístico)
  confidence_level: 0.95         # IC del coeficiente y de la banda del gráfico
  min_annotations: 15            # mínimo de anotaciones para intentar el ajuste
  min_per_class: 3               # mínimo de positivos y de negativos
  score_transform: identity      # identity | logit
  uncertain_handling: exclude    # exclude | positive | negative
  positive_values: ["1", "x", "y", "yes", "si", "sí", "true", "verdadero", "p"]
  negative_values: ["0", "n", "no", "false", "falso"]
  uncertain_values: ["?", "d", "dudoso", "uncertain"]
```

## Plan de construcción incremental

Cada paso deja el pipeline corriendo de punta a punta antes de pasar al
siguiente, contra datos reales
(`data/output/species_detection/manual_annotations/*.xlsx`).

### Paso 1 — Plomería: compilar anotaciones

- Nodo 1. Registrar el pipeline en `pipeline_registry.py` aunque sea de un
  solo nodo; crear catálogo y parámetros.
- **Validación**: abrir `validated_annotations.csv` y confirmar contra 2-3
  `.xlsx` reales que el mapeo a `positive`/`negative`/`uncertain` quedó
  bien, que los valores no reconocidos efectivamente hacen fallar el nodo, y
  que el log reporta pendientes por especie.
- **Chequeo de tamaño de muestra, aquí y no después**: con
  `validated_annotations` ya se sabe el `n` real y el balance de clases por
  especie. Revisar cuántas especies pasarían `min_annotations` y
  `min_per_class` *antes* de escribir los nodos que dependen de eso. Si son
  pocas, la decisión es subir `segment_size` en `species_detection` y anotar
  más, no seguir construyendo aguas abajo.

### Paso 2 — Modelo y umbral

- Nodos 2 y 3. En este punto el pipeline ya es útil de punta a punta: de
  anotaciones manuales a umbral recomendado por especie con su diagnóstico.
- **Validación**: para 1-2 especies, ajustar la logística a mano en un
  notebook y comparar coeficientes, p-value y `t*` contra la tabla.
  Confirmar que una especie con muestra chica cae en el estado esperado y no
  produce un umbral silenciosamente. Revisar con criterio biológico si los
  umbrales de 2-3 especies conocidas son razonables.

### Paso 3 — Visualización

- Nodos 4 y 5.
- **Validación**: inspección visual — la curva, la línea del umbral y los
  números anotados deben coincidir con `detection_validation_summary.csv`
  para las mismas especies revisadas en el Paso 2.

## Pendiente en `species_detection` (no en este pipeline)

- [ ] **Procedencia de las anotaciones.** Las fichas de validación `.xlsx`
      que genera `species_detection` deberían traer registrado quién anotó,
      cuándo, y la versión del modelo que produjo las detecciones
      (`classifiedBy` de pamDP). Sin eso, en seis meses no va a ser posible
      decir si un umbral corresponde a BirdNET 2.4 o a Perch, ni auditar
      diferencias entre anotadores. Es una columna en el generador de fichas,
      no un nodo de este pipeline.
- [ ] **Documentar el diseño de muestreo** de los segmentos (aleatorio
      simple sobre las detecciones, top-N por score, estratificado). Toda la
      interpretación de la curva ajustada como aplicable a la población de
      detecciones depende de que el muestreo sea aleatorio simple; si es
      top-N o estratificado, las estimaciones están sesgadas y hay que
      corregir con pesos.
- [ ] Convención de valores válidos en la columna `positive` (hoy texto
      libre). Idealmente, validación de datos en el `.xlsx` mismo (lista
      desplegable) para que el problema no llegue nunca a este pipeline.

## Notas conceptuales (fuera del alcance actual)

Descartadas por ahora para mantener el pipeline simple; documentadas para no
tener que redescubrirlas.

- **Curva de yield.** Contar detecciones totales en `observations@pamDP` con
  score ≥ t y estimar TP esperados, para ver el trade-off entre precisión y
  volumen retenido. Es el sustituto real de la curva precision-recall. Se
  saca de esta versión; cuando se retome, va sobre `observations@pamDP` (no
  `unfiltered_observations@pamDP`), porque es la población de la que se
  muestrearon los segmentos anotados — y conviene dejar una aserción que
  verifique que todos los segmentos anotados están efectivamente ahí.
- **Precisión acumulada con IC de Wilson.** El enfoque del plan anterior.
  Útil como validación cruzada del modelo logístico (la curva ajustada debe
  ser coherente con los puntos empíricos), pero como método principal
  desperdicia muestra. Nota importante si se retoma: con `n = 20`, el límite
  inferior de Wilson bilateral al 95% con precisión perfecta es
  `20/(20+3.84) = 0.84`, **por debajo de 0.9** — un criterio basado en ese
  límite es inalcanzable por construcción y marcaría todas las especies como
  "sin umbral confiable". Se necesitarían ~35 anotaciones (o ~25 usando el
  intervalo unilateral, que es lo correcto para un criterio unilateral).
- **Umbral conservador desde el IC.** Usar el límite inferior de la banda de
  confianza de la curva en vez del punto estimado. Más honesto con muestra
  chica, pero mueve el umbral bastante hacia arriba; evaluar cuando haya más
  anotaciones.
- **Calibración por bins de score.** Redundante con la curva ajustada, y con
  20 anotaciones y 10 bins daría 2 observaciones por bin — ruido con
  apariencia de diagnóstico.
- **Pooling parcial entre especies.** Un modelo jerárquico (logística con
  interceptos y pendientes aleatorios por especie) permitiría que las
  especies con 8 anotaciones tomen prestada fuerza de las que tienen 40. Es
  lo que la estructura de los datos pide con `n` chico, pero es un salto
  grande de complejidad. Candidato natural para cuando haya más especies
  anotadas.
- **Pseudorreplicación y variación por sitio.** Las detecciones no son
  independientes: varias pueden venir de la misma grabación, la misma noche
  o el mismo individuo, y la regresión asume observaciones independientes.
  Además la precisión del clasificador varía con el paisaje sonoro, así que
  un umbral global por especie puede no transferir entre sitios. Por eso el
  nodo 1 arrastra `deploymentID`: como mínimo permite reportar de cuántos
  despliegues vienen las anotaciones, y eventualmente añadir un efecto
  aleatorio por sitio.
- **Análisis de confusión.** Usar `detectedSpecies` en los negativos para
  ver qué especie se confunde con cuál. El nodo 1 ya arrastra la columna, así
  que se puede hacer después sin reprocesar nada.