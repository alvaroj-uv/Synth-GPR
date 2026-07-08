# Especificaciones algorítmicas — Synth-GPR

> **Para Claude Code.** Este documento contiene los tres algoritmos centrales del pipeline sim-real en pseudocódigo, con su contexto físico, el mapeo a módulos existentes del repo, y su relación con las tareas del backlog (`TODO_claude_code.md`). Implementar el pseudocódigo respetando las REGLAS marcadas — codifican decisiones físicas y de validez que no son negociables.
>
> Ubicación sugerida en el repo: `docs/specs/ALGORITHM_SPECS.md`

---

## Contexto físico común (leer antes de implementar cualquiera)

1. **El speckle:** la coda de un A-scan en balasto granular es una realización aleatoria del empaquetado (como el moteado de un láser). Dos trazas con física idéntica y piedras en posiciones distintas tienen correlación de forma de onda ≈ 0. Por eso **ninguna métrica del pipeline usa correlación punto a punto de la coda cruda**. Lo estable y comparable es: envolvente suavizada, timing de reflexiones coherentes, y contenido espectral.
2. **La geometría real:** antena GSSI 400 MHz air-launched a **0.50 m** sobre el balasto. Reflexión de superficie esperada ~3.3 ns tras la onda directa. dt real: leerlo SIEMPRE del header DZT (nunca hardcodear; valores históricos inconsistentes en docs: 0.1/0.098/0.0311 ns).
3. **Anti-circularidad:** la colmatación se parametriza por su causa física (`frac_finos` → ε/σ vía CRIM en `src/physics.py`). Las etiquetas de clase para ML vienen de `frac_finos` (sim) o ground truth de calicata (real) — NUNCA de la ε que el clasificador podría leer.
4. **Simetría sim/real:** toda transformación (remuestreo, ventana, suavizado) se aplica con parámetros IDÉNTICOS a ambos dominios. Las asimetrías silenciosas ya causaron un colapso del clasificador (bug del 1/33).

---

## SPEC-1: Calibración secuencial del forward model

**Implementa:** el corazón de T6 (`src/sim_real_comparison.py`) más el loop de calibración.
**Propósito:** encontrar los parámetros del simulador (wavelet, ε, σ, dispersión) que hacen que la sim se parezca a la real *en los observables físicos estables* — no en la forma de onda.
**Principio de diseño:** un observable por perilla, calibrados en orden de dependencia (aguas arriba → aguas abajo). Cada etapa es una compuerta: no se pasa a la siguiente sin converger la anterior, porque un error aguas arriba contamina todo lo de abajo (ej: σ calibrada con wavelet errónea = σ falsa que compensa el error de wavelet).

```
ALGORITMO calibración_secuencial_forward
ENTRADA:
    traza_real                      # A-scan medido
    dt_real                         # leído del header DZT (¡exacto!)
    h_aire = 0.50                   # gap de aire conocido (m)
    espesor_balasto                 # de calicata si existe; si no, incógnita acoplada
    porosidad                       # input geotécnico conocido (~0.4)
SALIDA:
    {wavelet, eps_eff, sigma_eff, perfil_dispersión}

# ---------- PRE: tratamiento idéntico en ambos lados ----------
FUNCIÓN preparar(traza, dt):
    corregir_tiempo_cero(traza)              # alinear a la onda directa
    aplicar_dewow(traza)
    # NO aplicar ganancia (AGC/TVG): la amplitud es información de sigma
    SI dt ≠ dt_real:
        traza = remuestrear(traza, dt → dt_real)
    RETORNAR traza
    # REGLA: sim y real pasan por ESTA MISMA función, mismos parámetros.

real = preparar(traza_real, dt_real)

# ==================================================================
# ETAPA 1 — WAVELET  (aísla la fuente; todo lo demás depende de ella)
# ==================================================================
# Observable: la onda directa (primeros ~4 ns), separada en el tiempo,
# dependiente casi solo de fuente+antena. El observable más limpio.

ventana_directa = recortar(real, t=0 .. ~4ns)
SI usar_modelo_antena:                       # nivel de alta fidelidad
    wavelet = extraer_de(antenna_like_GSSI_400)
SINO:                                        # nivel barato
    wavelet = deconvolucionar(ventana_directa, reflexión_placa_metálica)
        # deconvolución contra reflector conocido (R=-1) → pulso efectivo

corregir_polaridad(wavelet)                  # Ez * -1 si hace falta (convención de signo, no física)

sim_directa = simular_solo_directa(wavelet, h_aire)
ASSERT correlación(envolvente(sim_directa), envolvente(ventana_directa)) > umbral_1
    # criterio sobre la DIRECTA (evento coherente aislado), no sobre la coda

# ==================================================================
# ETAPA 2 — VELOCIDAD / TIMING  (fija eps·espesor; alinea eventos)
# ==================================================================
# Observable: tiempos de las reflexiones COHERENTES (superficie, base balasto).
# Restringe el PRODUCTO velocidad×espesor, no eps y espesor por separado.

t_superficie = pick_reflexión(real, esperado ≈ 2*h_aire/c)   # ≈ 3.3 ns
ASSERT |t_superficie - 3.3ns| < tol        # confirma geometría 50cm y tiempo cero

t_base = pick_reflexión(real, después de t_superficie)
Δt_balasto = t_base - t_superficie

SI espesor_balasto conocido:
    v_balasto = 2 * espesor_balasto / Δt_balasto
    eps_eff = (c / v_balasto)^2
SINO:
    registrar_restricción(eps_eff·espesor² ligados)   # se separan con offsets/calicata

# ==================================================================
# ETAPA 3 — ENVOLVENTE / SIGMA  (fija la atenuación)
# ==================================================================
# Observable: tasa de decaimiento α de la envolvente suavizada de la coda.
# α es MONÓTONA en sigma → converge en pocas iteraciones (interpolación, no grid).

FUNCIÓN alpha_de(traza):
    env = |hilbert(traza)|
    coda = recortar(env, t=t_superficie .. t_nivel_ruido)   # excluir la directa
    coda_suave = suavizar(coda, ventana=K)     # matar el speckle (K igual sim/real)
    (pendiente, nivel) = ajuste_recta_mínimos_cuadrados(t, log(coda_suave))
    RETORNAR -pendiente                        # α ; sigma ∝ α

α_real = alpha_de(real)
sigma = sigma_inicial_literatura
REPETIR:
    sim = preparar(simular(wavelet, eps_eff, sigma, espesor), dt_sim)
    α_sim = alpha_de(sim)
    SI |α_sim - α_real| < tol_α: SALIR
    sigma = actualizar(sigma, α_sim, α_real)   # interpolar: α crece con sigma
HASTA convergencia
sigma_eff = sigma
    # NOTA: sigma_eff ABSORBE spreading geométrico y pérdida por scattering.
    # Es sigma EFECTIVA de calibración, no conductividad pura del material.

# ==================================================================
# ETAPA 4 — DISPERSIÓN / COLMATACIÓN  (lo más fino; solo si 1-3 coinciden)
# ==================================================================
# Observable: desplazamiento del centroide espectral hacia abajo CON el tiempo
# (la pérdida de altas frecuencias se acumula con la profundidad).
# ADVERTENCIA (hueco #2 identificado): materiales gprMax con eps/sigma constantes
# NO producen downshift espectral apreciable. Las fuentes del downshift en sim son:
# (a) el balasto granular (scattering ~f^4), (b) materiales Debye para matriz húmeda
# (#add_dispersion_debye). Si la Etapa 4 no converge con medio homogéneo, NO es un
# bug de calibración — es física ausente del simulador.

FUNCIÓN evolución_espectral(traza):
    PARA cada ventana temporal w en la coda:
        centroide[w] = frecuencia_media(|FFT(traza en w)|)
        ancho[w]     = ancho_banda(...)
    RETORNAR (centroide vs w, ancho vs w)

REPETIR:
    frac_finos = actualizar(frac_finos, pendiente(cen_sim), pendiente(cen_real))
    (eps_c, sigma_c) = CRIM(frac_finos, porosidad, humedad)   # src/physics.py
    sim = preparar(simular(wavelet, eps_c, sigma_c, espesor), dt_sim)
HASTA |pendiente(cen_sim) - pendiente(cen_real)| < tol_disp

# ==================================================================
# MÉTRICAS DE PARECIDO (para reportar; NUNCA correlación de coda cruda)
# ==================================================================
similitud = {
    directa:    correlación(env(sim_directa), env(ventana_directa)),
    timing:     |Δt_sim - Δt_real|,
    envolvente: correlación(log(suavizar(env_coda_sim)), log(suavizar(env_coda_real))),
    espectro:   wasserstein_1D(espectro_coda_sim, espectro_coda_real),
}
RETORNAR {wavelet, eps_eff, sigma_eff, perfil_dispersión, similitud}
```

**Mapeo al repo:** `preparar` → `preprocess_physical` (T2, `src/signal_processing.py`); `alpha_de`, `evolución_espectral` y las métricas → T6 (`src/sim_real_comparison.py`); lectura DZT SOLO vía `src/dzt_io.py` (incluida la reversión de ganancia de T7); CRIM ya existe en `src/physics.py`.

**Tests requeridos:** α recuperado de una exponencial pura con error <1%; el pick de superficie sobre una sim de control cae en 2·h_aire/c ± tol; wasserstein_1D = 0 para espectros idénticos.

---

## SPEC-2: Generador de archivos `.in`

**Implementa:** T8 (escenario corregido) — extiende `generate_in_files.py` / `src/layer_scene_builder.py` / `src/gpr_commands.py`.
**Propósito:** emitir escenas gprMax con la geometría real (50 cm air-launched), balasto granular, y la fuente correcta según nivel de fidelidad. La estructura son seis bloques en orden de dependencia: materiales → dominio → ventana → posiciones → geometría → fuente → metadatos.

```
FUNCIÓN generar_in_file(config):
ENTRADA config:
    fidelidad          # "barato_2D" | "caro_3D"
    h_aire = 0.50      # gap de aire (m); randomizable con clearance_jitter
    dx = 0.002         # resolución (m)
    capas[]            # lista top→bottom: {nombre, espesor, packed?, material}
    frac_finos         # colmatación como CAUSA física (input de CRIM)
    porosidad = 0.40
    humedad
    wavelet_file       # wavelet calibrada de placa (nivel barato)
    dt_real            # para anotar el remuestreo posterior
    seed               # semilla RNG del empaquetado → SERÁ el group_id
SALIDA: texto del archivo .in

    # ============================================================
    # BLOQUE 0 — Materiales ANTES de geometría
    # ============================================================
    PARA cada capa EN capas:
        SI capa.packed:                        # balasto granular
            (eps_piedra, sig_piedra) = material("granito")     # ε≈5-7
            SI frac_finos > 0:                 # colmatado: huecos con finos+agua
                (eps_matriz, sig_matriz) = CRIM(frac_finos, porosidad, humedad)
            SINO:                              # limpio: huecos con aire
                (eps_matriz, sig_matriz) = (1.0, 0.0)
        SINO:
            (eps, sigma) = material(capa.material)
    # REGLA anti-circularidad: frac_finos es INPUT; la etiqueta ML sale de
    # frac_finos/calicata, NUNCA de estos eps.

    # ============================================================
    # BLOQUE 1 — DOMINIO (derivado del stack)
    # ============================================================
    altura = pml + buffer_inf + Σ(espesores) + h_aire + altura_antena(si 3D) + buffer_sup + pml
    ancho = 0.60                               # huella Fresnel + margen a PML
    profundidad = 0.40 SI caro_3D SINO dx      # 2D = una celda
    EMITIR "#domain", "#dx_dy_dz"

    # ============================================================
    # BLOQUE 2 — VENTANA TEMPORAL
    # ============================================================
    EMITIR "#time_window: 50e-9"               # iguala al dato real
    EMITIR "## RESAMPLE_TO_DT: {dt_real}"      # nota para el post-proceso
    # dt lo fija gprMax por Courant (~4.7ps a 2mm) → la salida SIEMPRE se remuestrea

    # ============================================================
    # BLOQUE 3 — POSICIONES Z (gprMax apila desde z=0 → invertir top→bottom)
    # ============================================================
    z = pml + buffer_inf
    PARA capa EN invertir(capas):              # bottom→top
        capa.z0 = z ; capa.z1 = z + capa.espesor ; z = capa.z1
    z_superficie = z
    z_antena = z_superficie + h_aire

    # ============================================================
    # BLOQUE 4 — GEOMETRÍA
    # ============================================================
    PARA capa EN invertir(capas):
        SI capa.packed:
            # REGLA painter's algorithm: matriz PRIMERO (box que llena la capa),
            # piedras DESPUÉS (lo último escrito gana). Invertir el orden borra las piedras.
            EMITIR "#box ... {matriz}"
            semilla_RNG(seed)                  # reproducibilidad del empaquetado
            PARA piedra EN empaquetar(capa, dx):   # pymunk/rock_packing
                EMITIR "#cylinder/#sphere ... {piedra}"
        SINO:
            EMITIR "#box ... {material}"       # subgrade: extender hasta PML
                                               # (sin reflexión de fondo espuria)

    # ============================================================
    # BLOQUE 5 — FUENTE Y RECEPTOR (ramifica por fidelidad)
    # ============================================================
    SI fidelidad == "barato_2D":
        EMITIR "#waveform: user {wavelet_file}"        # calibrada, NO ricker/gaussian
        EMITIR "#hertzian_dipole: z {x_tx} {y} {z_antena}"
        EMITIR "#rx: {x_tx + offset_txrx} {y} {z_antena}"   # offset GSSI400 ~0.16m
    SINO_SI fidelidad == "caro_3D":
        # NO declarar waveform/dipole/rx: la antena los trae internamente
        EMITIR "#python: antenna_like_GSSI_400(x, y, z_antena, resolution=dx)"
        # resolution DEBE ser 0.0005 | 0.001 | 0.002 (restricción del modelo)

    # ============================================================
    # BLOQUE 6 — METADATOS (contrato con el ensamblador T5)
    # ============================================================
    EMITIR "## CONFIG_frac_finos: {frac_finos}"
    EMITIR "## CONFIG_porosidad / humedad / fidelidad / h_aire"
    EMITIR "## CONFIG_group_seed: {seed}"      # ← se convierte en la columna `group`
                                               #   (guarda anti-fuga espacial)
    RETORNAR unir(líneas)
```

**Decisiones no obvias (documentar en el código):**
- Orden de cálculo inverso al físico: el stack se piensa top→bottom (como ve el radar) pero se coloca bottom→top (como apila gprMax).
- La matriz antes que las piedras (painter's algorithm).
- `seed` = futuro `group_id`: sin registrarla, no hay splits válidos después.
- `h_aire` randomizable (±3-5 cm): la altura real oscila en vehículo; un corpus a 0.500 exactos enseña al clasificador una constancia artificial.

**Tests requeridos:** el `.in` generado contiene el gap de 0.50 m verificable en coordenadas; `CONFIG_group_seed` presente; mismo seed → escena idéntica (bit a bit); en modo caro_3D no aparece ningún `#waveform`.

---

## SPEC-3: Verificador de empaquetado (lazo de 3 controles)

**Implementa:** T9 (`src/packing_verifier.py`).
**Propósito:** convertir "generé una escena" en "generé una escena válida". Tres controles en orden de costo creciente — cada uno filtra antes de pagar el siguiente. Incluye la resolución del problema 2D↔3D de la fracción (la porosidad 2D ≠ 3D; la fracción de área correcta se ENCUENTRA iterando, no se calcula analíticamente).

```
ALGORITMO verificar_y_calibrar_empaquetado
ENTRADA:
    escena              # grilla de materiales del .in discretizado
    objetivo: {granulometría_normada, porosidad_3D≈0.40, frac_finos, humedad}
    traza_real          # para el control 3
    tolerancias: {tol_granulo, tol_eps, tol_alpha, tol_espectral}
SALIDA: veredicto {PASA | AJUSTAR(perilla) | RECHAZAR} + métricas de fidelidad

# ============================================================
# CONTROL 1 — GEOMÉTRICO (barato: sin simular)
# ¿El empaquetador logró lo que se le pidió?
# ============================================================
frac_piedra_lograda = celdas_piedra / celdas_capa_balasto
    # el empaquetador puede NO converger a la fracción pedida — nunca asumir
piedras = componentes_conexos(escena, material_piedra)
D_lograda = distribución_acumulada(diámetros_equivalentes(piedras))
distancia_granulo = max|D_lograda - D_objetivo|            # tipo KS
gradiente_espurio = max-min de frac_piedra_por_franja_horizontal
    # (un gradiente PUEDE ser deseado si modela segregación; si no, artefacto)

SI distancia_granulo > tol O gradiente_espurio > tol:
    RETORNAR RECHAZAR      # problema del empaquetador: re-empaquetar, no calibrar

# ============================================================
# CONTROL 2 — COHERENTE (una sim 2D barata)
# ¿El medio efectivo EMERGENTE coincide con lo que CRIM predice?
# ============================================================
v_piedra = 1 - porosidad_3D
(v_finos, v_agua, v_aire) = repartir_huecos(porosidad_3D, frac_finos, humedad)
eps_esperada = CRIM(v_piedra, v_finos, v_agua, v_aire)     # src/physics.py

traza_sim = simular(escena)                                 # nivel barato
Δt = pick(base) - pick(superficie)
eps_emergente = (c · Δt / (2·espesor_balasto))^2

SI |eps_emergente - eps_esperada| > tol_eps:
    # --- lazo de calibración 2D↔3D ---
    # eps emergente es MONÓTONA en frac_piedra_2D → búsqueda por interpolación
    frac_2D = actualizar(frac_2D, eps_emergente, eps_esperada)
    RETORNAR AJUSTAR(frac_2D)
    # Este mapa frac_3D→frac_2D se calibra UNA VEZ por (granulometría, nivel finos)
    # y se CACHEA en JSON — no es un costo por escena del corpus.

# ============================================================
# CONTROL 3 — INCOHERENTE (contra el dato real; usa SPEC-1/T6)
# ¿El scattering colectivo tiene la estadística correcta?
# ============================================================
sim = preparar(traza_sim) ; real = preparar(traza_real)    # MISMO tratamiento
Δα = |alpha_de(sim) - alpha_de(real)|                       # atenuación colectiva
d_espectral = wasserstein_1D(espectro_coda(sim), espectro_coda(real))
# NUNCA correlación de forma de onda cruda — no existe en este algoritmo

SI Δα > tol_alpha:        RETORNAR AJUSTAR(sigma_matriz)
SI d_espectral > tol_esp: RETORNAR AJUSTAR(reparto_de_huecos vía CRIM)

RETORNAR PASA, métricas = {control1, control2, control3}
    # las métricas SON el informe de fidelidad del Objetivo 1 y se embeben
    # como "## CONFIG_fidelity_*" en el .in (trazabilidad, checklist Obj. 3)
```

**Decisiones no obvias:**
- Cada control tiene SU perilla y no se pisan: granulometría mal → re-empaquetar; ε emergente mal → frac_2D; α mal → σ matriz; espectro mal → reparto de huecos. Nunca grid search multiparámetro donde todo compensa a todo.
- El cacheo del mapa frac_3D→frac_2D es lo que hace viable el corpus masivo.
- La justificación física del granular (para defender ante revisores): las piedras a 400 MHz no se RESUELVEN (d≈5cm ≪ λ/4≈9cm) pero sí se SIENTEN — régimen Rayleigh débil, d/λ≈0.12: scattering colectivo que produce la atenuación aparente y la coda. Solo importa la ESTADÍSTICA del empaquetado (granulometría, fracción, contraste), no las posiciones ni formas individuales — por eso cilindros/discos con la distribución correcta bastan.

**Tests requeridos:** control 1 corre sin simulación sobre una escena de fixture; control 2 con medio homogéneo de ε conocida la recupera del timing con error <5%; el cacheo devuelve la frac_2D calibrada sin re-iterar.

---

## Dependencias entre specs y con el backlog

```
T1 (dt obligatorio) ─┐
T2 (preproc simétrico) ─┼─→ SPEC-1 (T6: comparación/calibración) ─┐
T7 (ganancia DZT) ───┘                                            ├─→ SPEC-3 (T9: verificador)
                                                                   │
SPEC-2 (T8: generador .in) ───────────────────────────────────────┘
        │
        └─→ T5 (ensamblador) lee los CONFIG_* que SPEC-2 emite
```

Implementar en orden: T1/T2/T7 → SPEC-1 → SPEC-2 → SPEC-3 → T5.

## Reglas de validez globales (repetidas aquí a propósito)

1. Nunca splits aleatorios por traza — siempre por `group` (= `CONFIG_group_seed` / tramo).
2. Nunca eps/sigma/pvc como features de ML (metadatos con prefijo `meta_`).
3. Nunca ganancia/normalización sobre datos de análisis de amplitud; normalización solo simétrica y explícita.
4. Nunca correlación de forma de onda cruda sobre la coda — envolvente suavizada, timing y espectro son las métricas.
5. Todo parámetro de tolerancia (`tol_*`) va en config, no hardcodeado, y su valor elegido se documenta.
