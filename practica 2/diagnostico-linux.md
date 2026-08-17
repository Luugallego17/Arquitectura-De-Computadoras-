# Comandos de Diagnóstico en Linux

**Práctica realizada en:** Ubuntu (máquina virtual VirtualBox)
**Autor:** Luu
**Fecha:** 17/08/2026

---

## Tarea 1 — Procesador: `lscpu`

**Comando ejecutado:**

```bash
lscpu
```

**Salida obtenida (resumida — se omiten los flags y la lista de vulnerabilidades):**

```
Architecture:             x86_64
  CPU op-mode(s):         32-bit, 64-bit
  Address sizes:          39 bits physical, 48 bits virtual
  Byte Order:             Little Endian
CPU(s):                   2
  On-line CPU(s) list:    0,1
Vendor ID:                GenuineIntel
  Model name:             13th Gen Intel(R) Core(TM) i5-13420H
    CPU family:           6
    Model:                186
    Thread(s) per core:   1
    Core(s) per socket:   2
    Socket(s):            1
    Stepping:             2
    BogoMIPS:             5222.39
Virtualization features:
  Hypervisor vendor:      KVM
  Virtualization type:    full
Caches (sum of all):
  L1d:                    96 KiB (2 instances)
  L1i:                    64 KiB (2 instances)
  L2:                     2.5 MiB (2 instances)
  L3:                     24 MiB (2 instances)
NUMA:
  NUMA node(s):           1
  NUMA node0 CPU(s):      0,1
```

**¿Qué es?** Un comando que muestra la información del procesador que el kernel de Linux tiene registrada.

**¿Para qué sirve?** Para conocer las características del CPU sin abrir la máquina: arquitectura, núcleos, hilos, cachés y velocidad.

**¿Por qué bota eso?** Al arrancar, el kernel interroga al procesador (instrucción CPUID) y este responde quién es y qué sabe hacer; `lscpu` muestra esa respuesta ordenada.

**Resultados obtenidos:**

- Arquitectura: **x86_64** (64 bits)
- Modelo: **Intel Core i5-13420H (13ª generación)**
- CPUs: **2 núcleos, 1 hilo por núcleo** (la VM solo tiene asignados 2 de los 8 núcleos reales)
- Cachés: **L1d 96 KiB, L1i 64 KiB, L2 2.5 MiB, L3 24 MiB**
- Virtualización: **KVM / full** → confirma que corre dentro de una máquina virtual

---

## Tarea 2 — Buses y Almacenamiento: `lspci` y `lsblk`

**Comandos ejecutados:**

```bash
lspci
lsblk
```

**Salida obtenida de `lspci`:**

```
00:00.0 Host bridge: Intel Corporation 440FX - 82441FX PMC [Natoma] (rev 02)
00:01.0 ISA bridge: Intel Corporation 82371SB PIIX3 ISA [Natoma/Triton II]
00:01.1 IDE interface: Intel Corporation 82371AB/EB/MB PIIX4 IDE (rev 01)
00:02.0 VGA compatible controller: InnoTek Systemberatung GmbH VirtualBox Graphics Adapter
00:03.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller (rev 02)
00:04.0 System peripheral: InnoTek Systemberatung GmbH VirtualBox Guest Service
00:05.0 Multimedia audio controller: Intel Corporation 82801AA AC'97 Audio Controller (rev 01)
00:06.0 USB controller: Apple Inc. KeyLargo/Intrepid USB
00:07.0 Bridge: Intel Corporation 82371AB/EB/MB PIIX4 ACPI (rev 08)
00:0b.0 USB controller: Intel Corporation 82801FB/FBM/FR/FW/FRW (ICH6 Family) USB2 EHCI Controller
00:0d.0 SATA controller: Intel Corporation 82801HM/HEM (ICH8M/ICH8M-E) SATA Controller [AHCI mode] (rev 02)
```

**Salida obtenida de `lsblk`:**

```
NAME    MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0     7:0    0     4K  1 loop /snap/bare/5
loop1     7:1    0    85M  1 loop /snap/claudeai-desktop/1
loop2     7:2    0 521.1M  1 loop /snap/code/257
loop3     7:3    0  63.8M  1 loop /snap/core20/2866
loop4     7:4    0  74.2M  1 loop /snap/core22/1380
loop5     7:5    0 269.6M  1 loop /snap/firefox/4173
loop6     7:6    0    74M  1 loop /snap/core22/2411
loop7     7:7    0  10.7M  1 loop /snap/firmware-updater/127
loop8     7:8    0 505.1M  1 loop /snap/gnome-42-2204/176
loop9     7:9    0  91.7M  1 loop /snap/gtk-common-themes/1535
loop10    7:10   0  10.3M  1 loop /snap/snap-store/1124
loop11    7:11   0   476K  1 loop /snap/snapd-desktop-integration/157
loop12    7:12   0  38.7M  1 loop /snap/snapd/21465
sda       8:0    0   500G  0 disk
├─sda1    8:1    0     1M  0 part
└─sda2    8:2    0   500G  0 part /var/snap/firefox/common/host-hunspell
                                  /
sr0      11:0    1    51M  0 rom  /media/osboxes/VBox_GAs_7.2.14
```

### `lspci`

**¿Qué es?** Lista los dispositivos conectados al bus PCI (el "cableado interno" de la placa madre).

**¿Para qué sirve?** Para saber qué tarjetas y controladores tiene la máquina (video, red, audio, USB, SATA) y qué chip exacto usan.

**¿Por qué bota eso?** Cada dispositivo PCI tiene grabado un ID de fabricante y de producto; `lspci` los lee y los traduce a nombres. Aparece hardware "antiguo" (chipset 440FX, audio AC'97) porque VirtualBox emula dispositivos clásicos muy compatibles, no el hardware real.

**Dispositivos principales encontrados:** video VirtualBox Graphics Adapter, red Intel 82540EM Gigabit, audio AC'97, controladores USB y controlador SATA.

### `lsblk`

**¿Qué es?** Lista los dispositivos de bloques: discos, particiones, CD e imágenes montadas.

**¿Para qué sirve?** Para ver qué discos hay, su tamaño, particiones y punto de montaje.

**¿Por qué bota eso?** El kernel registra cada dispositivo de bloques en `/sys/block` y `lsblk` lo presenta como árbol.

**Resultados obtenidos:**

- **sda (500 GB):** disco virtual con 2 particiones — `sda1` (1 MB, arranque) y `sda2` (500 GB, raíz `/`)
- **sr0 (51 MB):** CD virtual con las VirtualBox Guest Additions
- **loop0–loop12:** no son discos reales, son paquetes snap de Ubuntu montados como solo lectura

---

## Tarea 3 — Memoria y Sistema: `lsmem` y `sudo lshw`

**Comandos ejecutados:**

```bash
lsmem
sudo lshw
```

**Salida obtenida de `lsmem`:**

```
RANGE                                  SIZE  STATE REMOVABLE BLOCK
0x0000000000000000-0x00000000dfffffff  3.5G online       yes  0-27
0x0000000100000000-0x000000011fffffff  512M online       yes 32-35

Memory block size:       128M
Total online memory:       4G
Total offline memory:      0B
```

### `lsmem`

**¿Qué es?** Muestra cómo está organizada la RAM en rangos de direcciones y bloques.

**¿Para qué sirve?** Para verificar cuánta memoria ve el sistema y que esté activa ("online").

**¿Por qué bota eso?** El BIOS entrega al kernel un mapa de memoria al arrancar y `lsmem` lo muestra. Salen **dos rangos** (3.5G + 512M) porque la zona bajo los 4 GB de direcciones está reservada para dispositivos, así que esos 512M se reubican por encima de los 4 GB.

**Resultados obtenidos:** **4 GB de RAM total**, toda online, administrada en bloques de 128 MB.

### `sudo lshw` — explicación línea por línea

**Salida completa obtenida (se explica bloque por bloque más abajo):**

```
osboxes
    description: Computer
    product: VirtualBox
    vendor: innotek GmbH
    version: 1.2
    serial: 0
    width: 64 bits
    capabilities: smbios-2.5 dmi-2.5 smp vsyscall32
    configuration: family=Virtual Machine uuid=18f94755-b839-47f4-8879-c288fc752a34
  *-core
       description: Motherboard
       product: VirtualBox
       vendor: Oracle Corporation
       physical id: 0
       version: 1.2
       serial: 0
     *-firmware
          description: BIOS
          vendor: innotek GmbH
          physical id: 0
          version: VirtualBox
          date: 12/01/2006
          size: 128KiB
          capacity: 128KiB
          capabilities: isa pci cdboot bootselect int9keyboard int10video acpi
     *-memory
          description: System memory
          physical id: 1
          size: 4GiB
     *-cpu
          product: 13th Gen Intel(R) Core(TM) i5-13420H
          vendor: Intel Corp.
          physical id: 2
          bus info: cpu@0
          version: 6.186.2
          width: 64 bits
          capabilities: fpu fpu_exception wp vme de pse tsc msr pae mce cx8 apic sep
            mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx rdtscp
            x86-64 constant_tsc rep_good nopl xtopology nonstop_tsc cpuid tsc_known_freq
            pni pclmulqdq ssse3 fma cx16 sse4_1 sse4_2 movbe popcnt aes xsave avx f16c
            rdrand hypervisor lahf_lm abm 3dnowprefetch ibrs_enhanced fsgsbase bmi1 avx2
            bmi2 invpcid rdseed adx clflushopt sha_ni arat md_clear flush_l1d
            arch_capabilities
          configuration: microcode=4294967295
     *-pci
          description: Host bridge
          product: 440FX - 82441FX PMC [Natoma]
          vendor: Intel Corporation
          physical id: 100
          bus info: pci@0000:00:00.0
          version: 02
          width: 32 bits
          clock: 33MHz
        *-isa
             description: ISA bridge
             product: 82371SB PIIX3 ISA [Natoma/Triton II]
             vendor: Intel Corporation
             physical id: 1
             bus info: pci@0000:00:01.0
             version: 00
             width: 32 bits
             clock: 33MHz
             capabilities: isa bus_master
             configuration: latency=0
           *-pnp00:00
                product: PnP device PNP0303
                physical id: 0
                capabilities: pnp
                configuration: driver=i8042 kbd
           *-pnp00:01
                product: PnP device PNP0f03
                physical id: 1
                capabilities: pnp
                configuration: driver=i8042 aux
        *-ide
             description: IDE interface
             product: 82371AB/EB/MB PIIX4 IDE
             vendor: Intel Corporation
             physical id: 1.1
             bus info: pci@0000:00:01.1
             logical name: scsi1
             version: 01
             width: 32 bits
             clock: 33MHz
             capabilities: ide isa_compat_mode pci_native_mode bus_master emulated
             configuration: driver=ata_piix latency=64
             resources: irq:0 ioport:1f0(size=8) ioport:3f6 ioport:170(size=8)
               ioport:376 ioport:d000(size=16)
           *-cdrom
                description: DVD reader
                product: CD-ROM
                vendor: VBOX
                physical id: 0.0.0
                bus info: scsi@1:0.0.0
                logical name: /dev/cdrom
                logical name: /dev/sr0
                logical name: /media/osboxes/VBox_GAs_7.2.14
                version: 1.0
                capabilities: removable audio dvd
                configuration: ansiversion=5 mount.fstype=iso9660
                  mount.options=ro,nosuid,nodev,relatime,nojoliet,check=s,map=n,
                  blocksize=2048,uid=1000,gid=1000,dmode=500,fmode=400,iocharset=utf8
                  state=mounted status=ready
              *-medium
                   physical id: 0
                   logical name: /dev/cdrom
                   logical name: /media/osboxes/VBox_GAs_7.2.14
                   configuration: mount.fstype=iso9660 state=mounted
        *-display
             description: VGA compatible controller
             product: VirtualBox Graphics Adapter
             vendor: InnoTek Systemberatung GmbH
             physical id: 2
             bus info: pci@0000:00:02.0
             logical name: /dev/fb0
             version: 00
             width: 32 bits
             clock: 33MHz
             capabilities: vga_controller rom fb
             configuration: depth=32 driver=vboxvideo latency=0 resolution=1024,768
             resources: irq:18 memory:e0000000-e7ffffff memory:c0000-dffff
        *-network
             description: Ethernet interface
             product: 82540EM Gigabit Ethernet Controller
             vendor: Intel Corporation
             physical id: 3
             bus info: pci@0000:00:03.0
             logical name: enp0s3
             version: 02
             serial: 08:00:27:3c:cb:05
             size: 1Gbit/s
             capacity: 1Gbit/s
             width: 32 bits
             clock: 66MHz
             capabilities: pm pcix bus_master cap_list ethernet physical tp 10bt
               10bt-fd 100bt 100bt-fd 1000bt-fd autonegotiation
             configuration: autonegotiation=on broadcast=yes driver=e1000
               driverversion=6.8.0-31-generic duplex=full ip=10.0.2.15 latency=64
               link=yes mingnt=255 multicast=yes port=twisted pair speed=1Gbit/s
             resources: irq:19 memory:f0000000-f001ffff ioport:d010(size=8)
        *-generic
             description: System peripheral
             product: VirtualBox mouse integration
             vendor: InnoTek Systemberatung GmbH
             physical id: 4
             bus info: pci@0000:00:04.0
             logical name: input7
             logical name: /dev/input/event6
             logical name: /dev/input/js1
             logical name: /dev/input/mouse2
             version: 00
             width: 32 bits
             clock: 33MHz
             capabilities: pci
             configuration: driver=vboxguest latency=0
             resources: irq:20 ioport:d020(size=32) memory:f0400000-f07fffff
               memory:f0800000-f0803fff
        *-multimedia
             description: Multimedia audio controller
             product: 82801AA AC'97 Audio Controller
             vendor: Intel Corporation
             physical id: 5
             bus info: pci@0000:00:05.0
             logical name: card0
             logical name: /dev/snd/controlC0
             logical name: /dev/snd/pcmC0D0c
             logical name: /dev/snd/pcmC0D0p
             logical name: /dev/snd/pcmC0D1c
             version: 01
             width: 32 bits
             clock: 33MHz
             capabilities: bus_master
             configuration: driver=snd_intel8x0 latency=64
             resources: irq:21 ioport:d100(size=256) ioport:d200(size=64)
        *-usb:0
             description: USB controller
             product: KeyLargo/Intrepid USB
             vendor: Apple Inc.
             physical id: 6
             bus info: pci@0000:00:06.0
             version: 00
             width: 32 bits
             clock: 33MHz
             capabilities: ohci bus_master cap_list
             configuration: driver=ohci-pci latency=64
             resources: irq:22 memory:f0804000-f0804fff
           *-usbhost
                product: OHCI PCI host controller
                vendor: Linux 6.8.0-31-generic ohci_hcd
                physical id: 1
                bus info: usb@1
                logical name: usb1
                version: 6.08
                capabilities: usb-1.10
                configuration: driver=hub slots=12 speed=12Mbit/s
              *-usb
                   description: Human interface device
                   product: VirtualBox USB Tablet
                   vendor: VirtualBox
                   physical id: 1
                   bus info: usb@1:1
                   logical name: input6
                   logical name: /dev/input/event5
                   logical name: /dev/input/js0
                   logical name: /dev/input/mouse1
                   version: 1.00
                   capabilities: usb-1.10 usb
                   configuration: driver=usbhid maxpower=100mA speed=12Mbit/s
        *-bridge
             description: Bridge
             product: 82371AB/EB/MB PIIX4 ACPI
             vendor: Intel Corporation
             physical id: 7
             bus info: pci@0000:00:07.0
             version: 08
             width: 32 bits
             clock: 33MHz
             capabilities: bridge
             configuration: driver=piix4_smbus latency=0
             resources: irq:9
        *-usb:1
             description: USB controller
             product: 82801FB/FBM/FR/FW/FRW (ICH6 Family) USB2 EHCI Controller
             vendor: Intel Corporation
             physical id: b
             bus info: pci@0000:00:0b.0
             version: 00
             width: 32 bits
             clock: 33MHz
             capabilities: ehci bus_master cap_list
             configuration: driver=ehci-pci latency=64
             resources: irq:19 memory:f0805000-f0805fff
           *-usbhost
                product: EHCI Host Controller
                vendor: Linux 6.8.0-31-generic ehci_hcd
                physical id: 1
                bus info: usb@2
                logical name: usb2
                version: 6.08
                capabilities: usb-2.00
                configuration: driver=hub slots=12 speed=480Mbit/s
        *-sata
             description: SATA controller
             product: 82801HM/HEM (ICH8M/ICH8M-E) SATA Controller [AHCI mode]
             vendor: Intel Corporation
             physical id: d
             bus info: pci@0000:00:0d.0
             logical name: scsi2
             version: 02
             width: 32 bits
             clock: 33MHz
             capabilities: sata pm ahci_1.0 bus_master cap_list emulated
             configuration: driver=ahci latency=64
             resources: irq:21 ioport:d240(size=8) ioport:d248(size=4)
               ioport:d250(size=8) ioport:d258(size=4) ioport:d260(size=16)
               memory:f0806000-f0807fff
           *-disk
                description: ATA Disk
                product: VBOX HARDDISK
                vendor: VirtualBox
                physical id: 0.0.0
                bus info: scsi@2:0.0.0
                logical name: /dev/sda
                version: 1.0
                serial: VBe7242296-7f57c404
                size: 500GiB (536GB)
                capabilities: gpt-1.00 partitioned partitioned:gpt
                configuration: ansiversion=5 guid=023a741b-f668-4f4e-ac68-f1f6cdfbd7b0
                  logicalsectorsize=512 sectorsize=512
              *-volume:0
                   description: BIOS Boot partition
                   vendor: EFI
                   physical id: 1
                   bus info: scsi@2:0.0.0,1
                   logical name: /dev/sda1
                   serial: 9321c88c-3f8c-44ce-9484-0103c6ae1639
                   capacity: 1023KiB
                   capabilities: nofs
              *-volume:1
                   description: EXT4 volume
                   vendor: Linux
                   physical id: 2
                   bus info: scsi@2:0.0.0,2
                   logical name: /dev/sda2
                   logical name: /
                   logical name: /var/snap/firefox/common/host-hunspell
                   version: 1.0
                   serial: 877292f0-69dd-4735-bca5-47131956fcc0
                   size: 499GiB
                   capabilities: journaled extended_attributes large_files huge_files
                     dir_nlink recover 64bit extents ext4 ext2 initialized
                   configuration: created=2024-06-03 20:04:19 filesystem=ext4
                     lastmountpoint=/ modified=2026-08-17 10:41:22 mount.fstype=ext4
                     mount.options=ro,noexec,noatime mounted=2026-08-17 10:41:32
                     state=mounted
  *-input:0
       product: Power Button
       physical id: 1
       logical name: input0
       logical name: /dev/input/event0
       capabilities: platform
  *-input:1
       product: Sleep Button
       physical id: 2
       logical name: input1
       logical name: /dev/input/event1
       capabilities: platform
  *-input:2
       product: AT Translated Set 2 keyboard
       physical id: 3
       logical name: input2
       logical name: /dev/input/event2
       logical name: input2::capslock
       logical name: input2::numlock
       logical name: input2::scrolllock
       capabilities: i8042
  *-input:3
       product: Video Bus
       physical id: 4
       logical name: input4
       logical name: /dev/input/event3
       capabilities: platform
  *-input:4
       product: ImExPS/2 Generic Explorer Mouse
       physical id: 5
       logical name: input5
       logical name: /dev/input/event4
       logical name: /dev/input/mouse0
       capabilities: i8042
```

**¿Qué es?** Un inventario completo del hardware en forma de árbol: cada `*-algo` es un componente, y la sangría indica qué está dentro de qué.

**¿Por qué lleva `sudo`?** Porque lee zonas privilegiadas (las tablas DMI/SMBIOS del BIOS y la configuración de cada dispositivo); por eso pidió la contraseña (`[sudo] password for osboxes:`). Sin permisos de administrador la salida saldría incompleta.

**Campos que se repiten en todo el árbol** (se explican una sola vez):

| Campo | Significado |
|---|---|
| `description` | Qué tipo de componente es |
| `product` / `vendor` | Modelo y fabricante del dispositivo |
| `physical id` | Número que identifica al componente dentro de su "padre" en el árbol |
| `bus info` | Dirección del dispositivo en su bus (ej. `pci@0000:00:03.0` = bus PCI 0, dispositivo 3, función 0) |
| `logical name` | Nombre con el que Linux lo expone (ej. `/dev/sda`, `enp0s3`) |
| `version` | Revisión del hardware o del componente |
| `width` | Ancho de datos/direcciones en bits |
| `clock` | Frecuencia del bus al que está conectado |
| `capabilities` | Lista de funciones que el dispositivo declara saber hacer |
| `configuration` | Cómo lo configuró Linux: driver cargado, opciones activas |
| `resources` | Recursos del sistema que usa: `irq` (línea de interrupción para avisarle al CPU), `ioport` (puertos de entrada/salida) y `memory` (rangos de memoria mapeada) |

#### Encabezado — el equipo completo

```
osboxes
    description: Computer
    product: VirtualBox
    vendor: innotek GmbH
```

- **`osboxes`** — nombre de host de la máquina (viene de la imagen prearmada de OSBoxes).
- **`description: Computer`** — el nodo raíz del árbol: el equipo entero.
- **`product: VirtualBox` / `vendor: innotek GmbH`** — la "computadora" se identifica como VirtualBox. innotek GmbH es la empresa alemana que creó VirtualBox (luego comprada por Sun, y Sun por Oracle). Primera prueba de que es una máquina virtual.
- **`version: 1.2` / `serial: 0`** — versión del "hardware virtual" que VirtualBox presenta y número de serie ficticio (un equipo real traería el serial del fabricante).
- **`width: 64 bits`** — el sistema corre en modo 64 bits.
- **`capabilities: smbios-2.5 dmi-2.5 smp vsyscall32`** — el firmware ofrece tablas SMBIOS/DMI v2.5 (el formato estándar donde el BIOS describe el hardware, y de donde `lshw` saca esta parte); `smp` = soporta multiprocesamiento simétrico (más de un CPU); `vsyscall32` = puede ejecutar llamadas al sistema de programas de 32 bits.
- **`configuration: family=Virtual Machine uuid=18f94755-...`** — el propio firmware declara la familia "Virtual Machine", y el UUID es el identificador único que VirtualBox le asignó a esta VM (el mismo que usa VirtualBox para administrarla).

#### `*-core` — la placa madre

- **`description: Motherboard` / `product: VirtualBox`** — placa madre virtual.
- **`vendor: Oracle Corporation`** — aquí el fabricante figura como Oracle porque es el dueño actual de VirtualBox. Todo lo que cuelga de este nodo (BIOS, RAM, CPU, PCI) está "conectado" a esta placa.

#### `*-firmware` — el BIOS

- **`description: BIOS` / `vendor: innotek GmbH` / `version: VirtualBox`** — el firmware de arranque es el BIOS propio de VirtualBox, no el de la laptop real.
- **`date: 12/01/2006`** — fecha fija que reporta el BIOS de VirtualBox; no significa que el software sea de 2006, es un valor constante de su firmware virtual.
- **`size: 128KiB` / `capacity: 128KiB`** — tamaño de ese firmware.
- **`capabilities: isa pci cdboot bootselect int9keyboard int10video acpi`** — lo que sabe hacer el BIOS: manejar buses ISA y PCI, **arrancar desde CD** (`cdboot`), menú de selección de arranque (`bootselect`), servicios clásicos de teclado y video por interrupciones (`int9keyboard`, `int10video`) y soporte **ACPI** (el estándar de energía: apagar, suspender, etc.).

#### `*-memory` — la RAM

- **`description: System memory` / `size: 4GiB`** — los 4 GiB de RAM asignados a la VM. Coincide con `lsmem`. En una máquina física aquí se verían además los módulos (bancos) individuales; VirtualBox la presenta como un solo bloque.

#### `*-cpu` — el procesador

- **`product: 13th Gen Intel(R) Core(TM) i5-13420H` / `vendor: Intel Corp.`** — el único dato que se "hereda" del hardware real: el modelo del CPU físico.
- **`bus info: cpu@0`** — es el CPU número 0 (el primero).
- **`version: 6.186.2`** — significa familia 6, modelo 186, stepping 2: exactamente los mismos valores que mostró `lscpu` (CPU family: 6, Model: 186, Stepping: 2).
- **`width: 64 bits`** — procesador de 64 bits.
- **`capabilities: fpu ... sse2 ... aes avx avx2 sha_ni hypervisor ...`** — son los *flags* del CPU (los mismos de `lscpu`): cada palabra es una instrucción o función que el chip soporta. Algunos destacables: `fpu` (unidad de punto flotante), `sse/sse2/sse4/avx/avx2` (instrucciones vectoriales para cálculo rápido), `aes` y `sha_ni` (aceleración de cifrado por hardware), `nx` (protección de memoria no-ejecutable), `x86-64` (modo 64 bits), `ht` (hyper-threading), y **`hypervisor`**, el flag que indica explícitamente "estoy corriendo bajo un hipervisor" — otra confirmación de la VM.
- **`configuration: microcode=4294967295`** — 4294967295 es `0xFFFFFFFF` en hexadecimal, el valor "todo unos": VirtualBox no expone la versión real del microcódigo del CPU al invitado, así que aparece este valor de relleno.

#### `*-pci` — el puente principal (Host bridge)

- **`description: Host bridge` / `product: 440FX - 82441FX PMC [Natoma]`** — el "puente anfitrión" es el chip que conecta el CPU y la RAM con el bus PCI. El Intel 440FX (nombre clave *Natoma*) es un chipset real de 1996, de la época del Pentium Pro/Pentium II: VirtualBox lo emula porque es sencillo y todos los sistemas operativos lo soportan.
- **`width: 32 bits` / `clock: 33MHz`** — el bus PCI clásico funciona a 32 bits y 33 MHz. Todos los dispositivos que cuelgan de aquí muestran ese mismo reloj.

#### `*-isa` — puente ISA (y teclado/mouse PS/2)

- **`product: 82371SB PIIX3 ISA`** — el PIIX3 es el "southbridge" compañero del 440FX: conecta el bus PCI con el bus ISA antiguo, donde viven los dispositivos "legacy" como el teclado y mouse PS/2.
- **`capabilities: isa bus_master`** — maneja bus ISA y puede acceder a memoria por sí mismo (`bus_master`).
- **`*-pnp00:00 — PnP device PNP0303 ... driver=i8042 kbd`** — dispositivo Plug-and-Play `PNP0303`, que es el código estándar del **teclado de PC (101/102 teclas)**; lo maneja el driver `i8042` (el controlador PS/2 clásico) en su puerto de teclado (`kbd`).
- **`*-pnp00:01 — PnP device PNP0f03 ... driver=i8042 aux`** — `PNP0F03` es el código estándar del **mouse PS/2**; mismo controlador `i8042`, puerto auxiliar (`aux`).

#### `*-ide` — controlador IDE (y el CD-ROM)

- **`product: 82371AB/EB/MB PIIX4 IDE` / `driver=ata_piix`** — controlador de discos IDE clásico (parte del chip PIIX4); Linux lo maneja con el driver `ata_piix`. En esta VM solo se usa para la unidad de CD.
- **`logical name: scsi1`** — Linux le asigna el adaptador de almacenamiento número 1.
- **`capabilities: ... emulated`** — el propio kernel marca que es un dispositivo **emulado**.
- **`resources: ioport:1f0(size=8) ioport:3f6 ioport:170(size=8) ioport:376 ...`** — son los puertos de E/S **estándar históricos del IDE**: 0x1F0–0x1F7 y 0x3F6 para el canal primario, 0x170–0x177 y 0x376 para el secundario. Los mismos desde los años 80, otra señal del hardware "clásico" emulado.
- **`*-cdrom — DVD reader, product: CD-ROM, vendor: VBOX`** — la unidad óptica virtual. Sus tres `logical name` son el mismo dispositivo visto de tres formas: `/dev/cdrom` (alias), `/dev/sr0` (nombre real del dispositivo) y `/media/osboxes/VBox_GAs_7.2.14` (dónde está montado su contenido).
- **`capabilities: removable audio dvd`** — es extraíble y puede leer CD de audio y DVD.
- **`configuration: mount.fstype=iso9660 mount.options=ro,... state=mounted status=ready`** — tiene un disco insertado (la ISO de las **Guest Additions 7.2.14** de VirtualBox), con sistema de archivos **iso9660** (el estándar de los CD), montado en **solo lectura** (`ro`, como todo CD). Opciones de seguridad típicas: `nosuid`, `nodev` (ignora permisos especiales y archivos de dispositivo dentro del CD).
- **`*-medium`** — nodo que representa el "disco insertado" dentro de la unidad; repite los mismos datos de montaje.

#### `*-display` — la tarjeta de video

- **`product: VirtualBox Graphics Adapter` / `vendor: InnoTek ...`** — GPU virtual de VirtualBox (no la GPU real de la laptop).
- **`logical name: /dev/fb0`** — Linux la expone como *framebuffer* 0 (memoria de video accesible como archivo).
- **`capabilities: vga_controller rom fb`** — es compatible VGA, tiene ROM de video propia y soporta framebuffer.
- **`configuration: depth=32 driver=vboxvideo resolution=1024,768`** — profundidad de color de 32 bits, driver `vboxvideo` (parte de las Guest Additions) y resolución actual 1024×768.
- **`resources: memory:e0000000-e7ffffff memory:c0000-dffff`** — dos rangos de memoria: el primero es el espacio de direcciones reservado para la memoria de video (128 MiB de rango), y `c0000-dffff` es la zona legacy donde tradicionalmente vive la ROM/memoria VGA desde los primeros PC.

#### `*-network` — la tarjeta de red

- **`product: 82540EM Gigabit Ethernet Controller` / `vendor: Intel`** — tarjeta de red Intel emulada por VirtualBox; se elige porque su driver (`e1000`) viene incluido en prácticamente todos los sistemas operativos.
- **`logical name: enp0s3`** — nombre de la interfaz en Linux. El nombre se construye con su ubicación: **en** = ethernet, **p0** = bus PCI 0, **s3** = slot 3 (coincide con `bus info: pci@0000:00:03.0`).
- **`serial: 08:00:27:3c:cb:05`** — la dirección **MAC**. El prefijo `08:00:27` es el bloque de direcciones reservado oficialmente a VirtualBox (otra huella de la VM).
- **`size/capacity: 1Gbit/s`** — velocidad actual y máxima: 1 gigabit.
- **`capabilities: ... ethernet physical tp 10bt 10bt-fd 100bt 100bt-fd 1000bt-fd autonegotiation`** — es ethernet por par trenzado (`tp`) y soporta 10, 100 y 1000 Mbit/s en full-duplex (`-fd`), negociando la velocidad automáticamente.
- **`configuration: driver=e1000 driverversion=6.8.0-31-generic duplex=full ip=10.0.2.15 link=yes speed=1Gbit/s`** — driver `e1000` (la versión mostrada es la del kernel de Ubuntu, 6.8.0-31); enlace activo (`link=yes`), full duplex, y la IP **10.0.2.15**, que es la dirección típica que asigna el modo **NAT** de VirtualBox.

#### `*-generic` — integración de mouse de VirtualBox

- **`product: VirtualBox mouse integration` / `driver=vboxguest`** — dispositivo especial de VirtualBox (manejado por el driver de las Guest Additions) que permite que el puntero entre y salga de la ventana de la VM sin quedar "capturado". Se expone como varios dispositivos de entrada (`/dev/input/...`).

#### `*-multimedia` — el audio

- **`product: 82801AA AC'97 Audio Controller` / `driver=snd_intel8x0`** — tarjeta de sonido emulada según el estándar **AC'97** (1997); driver `snd_intel8x0` de ALSA (el sistema de sonido de Linux).
- **`logical name: card0, /dev/snd/controlC0, pcmC0D0p, pcmC0D0c...`** — es la tarjeta de audio 0; los nodos `pcm...p` son de reproducción (*playback*) y `pcm...c` de captura (grabación).

#### `*-usb:0` — controlador USB 1.1

- **`product: KeyLargo/Intrepid USB` / `vendor: Apple Inc.`** — dato curioso pero correcto: el controlador USB 1.1 (OHCI) que emula VirtualBox se identifica con los IDs de un chip de **Apple**. Por eso aparece "Apple" dentro de una PC virtual.
- **`capabilities: ohci` / `driver=ohci-pci`** — OHCI es el estándar de controladores USB 1.1.
- **`*-usbhost — OHCI PCI host controller ... slots=12 speed=12Mbit/s`** — el "hub raíz" de ese controlador: 12 puertos y velocidad 12 Mbit/s (la máxima de USB 1.1). El `vendor: Linux 6.8.0-31-generic` indica que este nodo lo genera el propio kernel.
- **`*-usb — VirtualBox USB Tablet ... driver=usbhid maxpower=100mA`** — un dispositivo apuntador virtual tipo **tableta USB**: envía coordenadas absolutas (no movimientos relativos como un mouse), lo que hace que el puntero coincida exacto con la posición del mouse real del anfitrión. Driver estándar `usbhid`, consume hasta 100 mA (valor declarado, virtual).

#### `*-bridge` — puente ACPI/energía

- **`product: 82371AB/EB/MB PIIX4 ACPI` / `driver=piix4_smbus`** — la parte del chip PIIX4 encargada de **ACPI** (administración de energía: apagado, suspensión) y del bus **SMBus** (un bus interno de baja velocidad para sensores y configuración). Usa la interrupción 9, la clásica de ACPI.

#### `*-usb:1` — controlador USB 2.0

- **`product: 82801FB ... (ICH6 Family) USB2 EHCI Controller` / `driver=ehci-pci`** — segundo controlador USB, este de tipo **EHCI = USB 2.0**.
- **`*-usbhost ... speed=480Mbit/s`** — su hub raíz funciona a 480 Mbit/s, la velocidad máxima de USB 2.0 (por eso hay dos controladores: uno para dispositivos lentos 1.1 y otro para rápidos 2.0).

#### `*-sata` — controlador SATA (y el disco duro)

- **`product: 82801HM/HEM (ICH8M/ICH8M-E) SATA Controller [AHCI mode]` / `driver=ahci`** — controlador de discos SATA moderno en modo **AHCI** (el estándar actual para discos SATA), manejado por el driver `ahci`. Aquí está conectado el disco principal (a diferencia del CD, que quedó en el IDE).
- **`capabilities: sata pm ahci_1.0 ... emulated`** — SATA con administración de energía (`pm`), AHCI 1.0, y de nuevo marcado como emulado.
- **`*-disk — ATA Disk, product: VBOX HARDDISK`** — el disco duro virtual de VirtualBox, expuesto como `/dev/sda`.
- **`serial: VBe7242296-...`** — serial ficticio generado por VirtualBox (empieza con "VB").
- **`size: 500GiB (536GB)`** — mismo tamaño en dos unidades: 500 **GiB** (base 1024) = 536 **GB** (base 1000, la que usan los fabricantes de discos).
- **`capabilities: gpt-1.00 partitioned partitioned:gpt`** — el disco usa tabla de particiones **GPT** (el esquema moderno, sucesor del MBR).
- **`configuration: guid=... logicalsectorsize=512 sectorsize=512`** — identificador único del disco GPT y sectores de 512 bytes.
- **`*-volume:0 — BIOS Boot partition, capacity: 1023KiB, capabilities: nofs`** — la partición `/dev/sda1` de ~1 MB. Es la **BIOS Boot Partition**: cuando un disco GPT arranca con BIOS clásico (no UEFI), el gestor de arranque GRUB necesita este pequeño espacio para instalarse. `nofs` = no contiene sistema de archivos, solo código de arranque.
- **`*-volume:1 — EXT4 volume, size: 499GiB`** — la partición `/dev/sda2`: casi todo el disco, con sistema de archivos **ext4** (el estándar de Linux, con journaling — `journaled` — que protege contra corrupción si se corta la energía).
- **`logical name: /` y `/var/snap/firefox/common/host-hunspell`** — la misma partición aparece montada dos veces: como raíz del sistema (`/`) y como un *bind mount* (re-montaje de una carpeta en otra ruta) que el snap de Firefox usa para acceder a los diccionarios de ortografía del sistema. Las opciones `ro,noexec,noatime` que se ven corresponden a ese montaje restringido de Firefox (solo lectura, sin ejecutar binarios), no al sistema completo.
- **`configuration: created=2024-06-03 ... state=mounted`** — el sistema de archivos se creó el 3 de junio de 2024 (cuando OSBoxes construyó la imagen) y está montado.

#### `*-input:0` a `*-input:4` — dispositivos de entrada

Estos nodos cuelgan directo del equipo (no del bus PCI) porque son dispositivos de entrada que el kernel registra por separado:

- **`input:0 — Power Button`** y **`input:1 — Sleep Button`** — los "botones" de encendido y suspensión que ACPI expone como dispositivos de entrada (así el sistema detecta cuando se presionan).
- **`input:2 — AT Translated Set 2 keyboard`** — el teclado PS/2 (nombre estándar con que Linux registra el teclado del controlador i8042); las entradas `capslock/numlock/scrolllock` son los LEDs del teclado.
- **`input:3 — Video Bus`** — dispositivo ACPI asociado al video (en laptops reales genera los eventos de brillo de pantalla).
- **`input:4 — ImExPS/2 Generic Explorer Mouse`** — el mouse PS/2 emulado (protocolo IntelliMouse Explorer, de ahí "ImExPS/2"). Convive con la tableta USB de VirtualBox: hay dos apuntadores, el PS/2 clásico y el USB de integración.

---

## Conclusión

En Linux, el kernel detecta el hardware al arrancar y publica esa información en archivos virtuales (`/proc`, `/sys`). Estos comandos no escanean nada nuevo: solo leen esa información y la presentan ordenada, cada uno desde un ángulo distinto — CPU (`lscpu`), buses (`lspci`), discos (`lsblk`), RAM (`lsmem`) y el conjunto completo (`lshw`). Como la práctica se realizó dentro de VirtualBox, todo lo reportado corresponde al hardware **virtual** que el hipervisor presenta a la máquina: chipset Intel 440FX de 1996, BIOS de innotek, disco "VBOX HARDDISK", MAC `08:00:27` e IP NAT 10.0.2.15. El único dato heredado del equipo físico es el modelo del procesador (i5-13420H), aunque limitado a 2 de sus 8 núcleos.
