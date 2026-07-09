# TODO Synth-GPR — Backlog para Claude Code

> Referenciado por `.claude/CLAUDE.md`. Orden de trabajo: P0 → P1 → P2.
> Este fichero se creó 2026-07-07 a partir del backlog de la sesión 2026-07-04
> (que vivía solo en chat), con el estado real de ejecución.

## Estado del backlog original (T1–T14) — COMPLETO

| Tarea | Descripción | Estado | Commit |
|---|---|---|---|
| T1 | `dt` obligatorio en `extract_features` (ValueError, sin default silencioso) | ✅ DONE | `daf15c3` |
| T2 | `preprocess_physical` / `normalize_for_features` (separar físico de normalización; guarda del 1/33) | ✅ DONE | `3a3a86d` |
| T3 | Golden test de la cadena de features (`tests/test_golden_features.py`) | ✅ DONE | `8a92a4e` |
| T4 | `resolve_gprmax_python()` — sin rutas de máquina hardcodeadas | ✅ DONE | `a6bc46c` |
| T5 | `scripts/pipeline/assemble_dataset.py` (features+meta, anti-circularidad) | ✅ DONE | `8e98440` |
| T6 | `src/sim_real_comparison.py` + CLI (métricas canónicas: envolvente/α/espectro) | ✅ DONE | `2d0ec71` |
| T7 | Lectura/reversión de ganancia DZT (hallazgo: no decodificable en Puerto-Limache) | ✅ DONE | `76e09e7` |
| T8 | Escenario 50 cm granular + wavelet GSSI (`examples/ballast_50cm_granular.toml`) | ✅ DONE | `9a214b1` |
| T9 | Verificador de empaquetado (3 controles; validado con run gprMax real: ε 6.10 vs 6.0) | ✅ DONE | `8ed6c40` |
| T10 | Archivar scripts sueltos de la raíz (ya lo había hecho el refactor) | ✅ DONE | `e310a25` |
| T11 | Consolidar packers (conservados los 2 externos: pymunk + RCPGenerator; rip/rcp → attic) | ✅ DONE | `bd93a4d` |
| T12 | Sincerar README (claims → `docs/reports/HISTORICAL_BASELINE.md`) | ✅ DONE | `624a8f2` |
| T13 | `tests/verify/` → invariante rescatado + attic | ✅ DONE | `e178ef7` |
| T14 | CI mínimo (GitHub Actions: pytest + ruff suave) | ✅ DONE | `2a468e8` |

## Pendientes activos (post-backlog)

- **Sampler HYDRO-CLAMP-style** (fix de `src/sampling.py`): muestrear la ETIQUETA
  y luego invertir con `inverse_convert_fi_to_pvc(FI, porosity=real)`; hoy la
  etiqueta no casa con la geometría empaquetada, la FI-masa satura ~38.7 (HF
  inalcanzable), top/bottom y humedad se muestrean independientes. Ver memoria
  `project_hydro_clamp_sampling`.
- **Wavelet definitiva** (SPEC-1 Etapa 1): deconvolución contra placa metálica o
  modelo de antena gprMax (`antenna_like_GSSI_400`) — el grid search de 2026-06-16
  quedó INVALIDATED (ver abajo).
- **Primer run de CI en GitHub Actions**: vigilar la tolerancia float del golden
  test en Linux.

## Descubierto durante sesiones

- **2026-07-07 — `CALIBRATION_VALIDATION_CHECKLIST.md` ya no existía** (503
  líneas; borrado en el squash del refactor `d919858`). Sus claims inválidos
  sobrevivían propagados; las correcciones de honestidad se aplicaron a los docs
  vivos: `FINAL_CALIBRATION_SUMMARY.md`, `WAVEFORM_CALIBRATION_RESULTS.md`,
  `DEFAULT_CONFIGURATION_GUIDE.md`, `GPRMAX_SAMPLING_CONTROL.md`, `INDEX.md`,
  `BALLAST_LAYER_CODA_VALIDATION.md` + 5 TOMLs de `examples/`.
- **2026-07-07 — §1.2 (frecuencia) y §1.3 (spacing) usaban la misma métrica de
  suelo de ruido que §1.1 (waveform)**: correlación de forma de onda sobre
  coda-speckle, todas −0.028…+0.011. Corregidas junto a 1.1 (mismo fundamento).
- **2026-07-07 — `experiments/2026-06-30/README.md` contiene un eco del 88.76%**:
  dejado congelado (registro fechado de experimento; no se reescriben).
- 2026-07-04 — la cadena de features emite **824** columnas numéricas, no las 572
  documentadas (CLAUDE.md/README desactualizados en ese número).
- 2026-07-04 — `experiments/2026-06-30/*` runners aún contienen rutas de máquina
  hardcodeadas: dejados como registros congelados (T4 solo barrió scripts vivos).
- 2026-07-04 — DZT Puerto-Limache: bloque de ganancia del header no decodificable
  (`rh_rgain=8192, rh_nrgain=5`) → estado de ganancia de la amplitud real
  DESCONOCIDO para calibración de σ (memoria `reference_dzt_gain`).
