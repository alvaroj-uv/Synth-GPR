# Solución al Problema de los Scripts

## Problema Identificado

Los scripts fallan porque el entorno conda `gprMax` no está activado cuando se ejecutan.

Cuando ejecutas manualmente:
```bash
python -m gprMax s_0000.in
```
Funciona porque tu terminal tiene el entorno `gprMax` activado.

Pero cuando el script ejecuta `python`, usa `/opt/miniconda3/bin/python` (entorno base) que NO tiene gprMax instalado.

## Soluciones

### Opción 1: Activar el entorno antes de ejecutar (RECOMENDADO)

```bash
conda activate gprMax
cd /Users/alvarojeria/Codigo/Synth-GPR/output/pipeline_run/20251210_142323
./run_gprmax.sh -p 4
./extract_features.sh
./create_blueprints.sh
```

### Opción 2: Ejecutar todo en una línea

```bash
conda activate gprMax && cd output/pipeline_run/20251210_142323 && ./run_gprmax.sh -p 4 && ./extract_features.sh && ./create_blueprints.sh
```

### Opción 3: Usar el pipeline principal (ya maneja el entorno)

```bash
conda activate gprMax
./pipeline.sh -n 10 -p 4
```

## Verificación

Para verificar que estás en el entorno correcto:

```bash
# Debe mostrar: gprMax
echo $CONDA_DEFAULT_ENV

# Debe mostrar la ruta con gprMax en ella
which python

# Debe funcionar sin error
python -m gprMax --help
```

## Nota Importante

Los scripts generados por `create_run_scripts.sh` asumen que ya estás en el entorno conda correcto. Esto es intencional para mantener los scripts simples y portables.

Si quieres que los scripts activen automáticamente el entorno, puedes agregar esto al inicio de cada script (después del shebang):

```bash
# Activate conda environment if needed
if [ -n "$CONDA_EXE" ] && [ "$CONDA_DEFAULT_ENV" != "gprMax" ]; then
    eval "$(conda shell.bash hook)"
    conda activate gprMax
fi
```

## Flujo de Trabajo Recomendado

1. Activa el entorno una vez:
   ```bash
   conda activate gprMax
   ```

2. Genera datos:
   ```bash
   ./1_generate_inputs.sh -n 20
   ```

3. Crea scripts para ese directorio:
   ```bash
   ./create_run_scripts.sh output/generated/TIMESTAMP
   ```

4. Ejecuta los scripts (el entorno ya está activado):
   ```bash
   cd output/generated/TIMESTAMP
   ./run_gprmax.sh -p 4
   ./extract_features.sh
   ./create_blueprints.sh
   ```
