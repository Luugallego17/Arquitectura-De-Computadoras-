# Clase 1 — Instalación de Ubuntu

**Fecha:** 05/08/2026
**Tarea:** [#1 — Instalar Ubuntu](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/1)

## ¿Qué se hizo?

Se instaló el sistema operativo **Ubuntu** para contar con un entorno
Linux de trabajo, necesario para las prácticas y herramientas de la
materia (terminal, `gcc`, `g++`, Python 3, comandos de diagnóstico de
hardware, etc.).

## Pasos generales de la instalación

1. Descargar la imagen ISO de Ubuntu desde [ubuntu.com](https://ubuntu.com/download).
2. Crear la máquina virtual (o USB booteable) y arrancar desde la ISO.
3. Seguir el asistente: idioma, distribución de teclado, particionado y usuario.
4. Al terminar, actualizar el sistema:

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

5. Instalar las herramientas de compilación que se usan en el curso:

   ```bash
   sudo apt install build-essential gcc g++ python3 -y
   ```

## Criterio de terminado

✅ Ubuntu instalado, actualizado y funcionando correctamente, con acceso
a la terminal. Todas las prácticas de las clases siguientes se
ejecutaron sobre esta instalación.
