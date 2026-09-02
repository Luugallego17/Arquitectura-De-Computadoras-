# Clase 3 — Diagnóstico de hardware en Linux

**Fecha:** 17/08/2026
**Tareas:**

- [#4 — Diagnóstico del Procesador (`lscpu`)](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/4)
- [#5 — Diagnóstico de Buses y Almacenamiento (`lspci`, `lsblk`)](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/5)
- [#3 — Diagnóstico de Memoria y Hardware (`lsmem`, `sudo lshw`)](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/3)

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`diagnostico-linux.md`](diagnostico-linux.md) | Documento de la práctica: qué hace cada comando, qué información entrega y qué se identificó en el equipo. |

> 📝 **Nota:** el documento original se entregó como `practica 2/diagnostico-linux.md`
> pero ese archivo no llegó a quedar en el historial del repositorio, así que
> aquí se reconstruye la práctica. Las capturas de evidencia originales están
> en los comentarios de los issues #3, #4 y #5.

## Resumen de comandos

```bash
lscpu        # características del procesador
lspci        # dispositivos conectados al bus PCI
lsblk        # discos, particiones y puntos de montaje
lsmem        # rangos y estado de la memoria RAM
sudo lshw    # inventario completo del hardware
```
