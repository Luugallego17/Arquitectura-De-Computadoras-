/*
 * Práctica: transferencia de bloques de memoria con memcpy/memmove
 * Materia:  Arquitectura de Computadoras
 * Alumna:   Luna Saleth Gallego Martinez
 * Tareas:   #10 — Lectura del arreglo desde memoria secundaria
 *           #11 — Transferencia de bloque con memcpy y limpieza con memset
 *           #12 — Salidas por consola y validación
 *           #13 — Compilación, pruebas y entrega
 *
 * El programa:
 *   1. Lee los 1000 enteros de datos.txt (memoria secundaria) y los
 *      carga en un arreglo en memoria principal, controlando errores.
 *   2. Muestra los primeros y últimos cinco elementos antes del traslado.
 *   3. Transfiere los elementos de los índices 500 a 599 a un segundo
 *      arreglo de 100 elementos usando memcpy.
 *   4. Limpia ese rango del arreglo original con memset (queda en cero).
 *   5. Muestra los 100 elementos transferidos.
 *   6. Valida automáticamente que los índices 500 a 599 del arreglo
 *      original contengan cero e informa éxito o fallo por consola.
 *
 * Compilar:  g++ -Wall -Wextra transferencia.cpp -o transferencia
 * Ejecutar:  ./generador && ./transferencia
 */
#include <cstring>   // memcpy, memset
#include <fstream>
#include <iostream>

const int TOTAL  = 1000;  // tamaño del arreglo original
const int INICIO = 500;   // primer índice del bloque a transferir
const int BLOQUE = 100;   // cuántos elementos se transfieren (500..599)

int main()
{
    int original[TOTAL];
    int transferido[BLOQUE];

    // ---- 1. Lectura desde memoria secundaria (tarea #10) -------------
    std::ifstream archivo("datos.txt");
    if (!archivo) {
        std::cerr << "Error: no se pudo abrir datos.txt.\n"
                  << "Genera el archivo primero con ./generador\n";
        return 1;
    }

    int leidos = 0;
    while (leidos < TOTAL && archivo >> original[leidos]) {
        leidos++;
    }
    if (leidos != TOTAL) {
        std::cerr << "Error: se esperaban " << TOTAL
                  << " enteros pero solo se leyeron " << leidos << ".\n";
        return 1;
    }
    std::cout << "Se cargaron " << leidos
              << " enteros en el arreglo en memoria principal.\n\n";

    std::cout << "Primeros cinco elementos: ";
    for (int i = 0; i < 5; i++) std::cout << original[i] << ' ';
    std::cout << "\nUltimos cinco elementos : ";
    for (int i = TOTAL - 5; i < TOTAL; i++) std::cout << original[i] << ' ';
    std::cout << "\n\n";

    // ---- 2. Transferencia del bloque con memcpy (tarea #11) ----------
    // Los arreglos no se traslapan, así que memcpy es suficiente
    // (si se traslaparan habría que usar memmove).
    memcpy(transferido, &original[INICIO], BLOQUE * sizeof(int));

    // Limpieza del rango 500..599 en el arreglo original.
    memset(&original[INICIO], 0, BLOQUE * sizeof(int));

    // ---- 3. Salidas por consola (tarea #12) --------------------------
    std::cout << "Elementos transferidos al segundo arreglo (indices "
              << INICIO << " a " << INICIO + BLOQUE - 1 << "):\n";
    for (int i = 0; i < BLOQUE; i++) {
        std::cout << transferido[i] << ((i + 1) % 10 == 0 ? '\n' : ' ');
    }
    std::cout << '\n';

    // ---- 4. Validación automática (tarea #12) ------------------------
    int errores = 0;
    for (int i = INICIO; i < INICIO + BLOQUE; i++) {
        if (original[i] != 0) {
            std::cout << "Fallo: el indice " << i << " contiene "
                      << original[i] << " en lugar de 0.\n";
            errores++;
        }
    }
    if (errores == 0) {
        std::cout << "Validacion EXITOSA: los indices " << INICIO << " a "
                  << INICIO + BLOQUE - 1
                  << " del arreglo original contienen cero.\n";
    } else {
        std::cout << "Validacion FALLIDA: " << errores
                  << " elementos no quedaron en cero.\n";
        return 1;
    }

    // Verificación extra: el resto del arreglo no se tocó.
    bool resto_ok = true;
    for (int i = 0; i < TOTAL; i++) {
        if (i >= INICIO && i < INICIO + BLOQUE) continue;
        if (original[i] != i) { resto_ok = false; break; }
    }
    std::cout << (resto_ok
                  ? "El resto del arreglo original no fue afectado.\n"
                  : "Cuidado: se modificaron elementos fuera del rango.\n");

    return resto_ok ? 0 : 1;
}
