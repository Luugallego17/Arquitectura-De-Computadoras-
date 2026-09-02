# Práctica: Diagnóstico de hardware con la terminal de Ubuntu

**Materia:** Arquitectura de Computadoras
**Alumna:** Luna Saleth Gallego Martinez
**Fecha:** 17/08/2026

---

## 1. Diagnóstico del procesador — `lscpu`

```bash
lscpu
```

`lscpu` lee la información que el kernel expone sobre el CPU y la
presenta resumida. Lo importante que se identificó:

- **Architecture:** `x86_64` → procesador de 64 bits.
- **CPU(s):** número total de procesadores lógicos (núcleos × hilos).
- **Thread(s) per core:** si vale 2, el procesador tiene *hyper-threading*.
- **Core(s) per socket:** núcleos físicos reales.
- **CPU max/min MHz:** rango de frecuencias al que puede trabajar.
- **Caché L1d / L1i / L2 / L3:** la jerarquía de memoria caché. L1 es la
  más pequeña y rápida (y está dividida en datos `L1d` e instrucciones
  `L1i`), L3 es la más grande y compartida entre núcleos.

Esto conecta directo con el tema de jerarquía de memoria: entre más
cerca del núcleo está la caché, más rápida y más chica es.

---

## 2. Diagnóstico de buses — `lspci`

```bash
lspci
```

`lspci` lista todos los dispositivos conectados al **bus PCI**. Cada
línea muestra la dirección del dispositivo (`bus:dispositivo.función`)
y su tipo. Los principales que se identificaron:

- **Host bridge** — el puente entre el CPU y el resto del sistema.
- **VGA compatible controller** — la tarjeta de video.
- **Ethernet controller / Network controller** — la tarjeta de red.
- **Audio device** — el controlador de sonido.
- **USB controller** — los controladores del bus USB.
- **SATA controller** — el controlador de los discos.

El bus PCI es el "camino" por el que estos dispositivos se comunican
con el procesador y la memoria.

---

## 3. Diagnóstico de almacenamiento — `lsblk`

```bash
lsblk
```

`lsblk` muestra los **dispositivos de bloques** en forma de árbol: el
disco principal (por ejemplo `sda`), sus particiones (`sda1`, `sda2`,
...) y dónde está montada cada una:

- `NAME` — nombre del dispositivo o partición.
- `SIZE` — tamaño.
- `TYPE` — `disk` (disco físico), `part` (partición) o `rom` (unidad óptica).
- `MOUNTPOINTS` — punto de montaje; la partición montada en `/` es la
  raíz del sistema, y puede haber otra para `/boot/efi` o swap.

---

## 4. Diagnóstico de memoria — `lsmem`

```bash
lsmem
```

`lsmem` muestra los **rangos de direcciones** de la memoria RAM y su
estado. Se verificó que:

- Todos los bloques de memoria aparecen en estado **online** (es decir,
  disponibles para el sistema).
- La línea `Total online memory` coincide con la RAM instalada en el
  equipo.

---

## 5. Inventario completo — `sudo lshw`

```bash
sudo lshw
```

`lshw` recorre todo el hardware y genera un inventario jerárquico
(necesita `sudo` para leer la información completa). Se documentaron
las secciones principales:

- **system** — fabricante y modelo del equipo.
- **memory** — RAM instalada y, dentro de `cache`, las cachés L1/L2/L3
  (coincide con lo reportado por `lscpu`).
- **cpu** — modelo exacto del procesador, sus capacidades (*flags*) y
  frecuencias.
- **storage / disk** — el disco y sus volúmenes (coincide con `lsblk`).
- **network** — la tarjeta de red (coincide con `lspci`).
- **display** — la tarjeta de video.

---

## Conclusión

Con solo cinco comandos de terminal se puede levantar el mapa completo
de la arquitectura de la máquina: el procesador y su jerarquía de
cachés (`lscpu`), los dispositivos colgados del bus PCI (`lspci`), el
almacenamiento secundario y sus particiones (`lsblk`), la memoria
principal (`lsmem`) y el inventario general (`lshw`). Cada comando
corresponde a uno de los bloques que estudiamos en la materia: CPU,
buses, memoria y E/S.

> 🖼️ Las capturas de las salidas reales del equipo están como evidencia
> en los comentarios de los issues
> [#3](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/3),
> [#4](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/4) y
> [#5](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/5).
