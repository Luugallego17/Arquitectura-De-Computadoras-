#include <cstring>
#include <fstream>
#include <iostream>

const int TOTAL  = 1000;
const int INICIO = 500;
const int BLOQUE = 100;

int main()
{
    int original[TOTAL];
    int transferido[BLOQUE];

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

    memcpy(transferido, &original[INICIO], BLOQUE * sizeof(int));
    memset(&original[INICIO], 0, BLOQUE * sizeof(int));

    std::cout << "Elementos transferidos al segundo arreglo (indices "
              << INICIO << " a " << INICIO + BLOQUE - 1 << "):\n";
    for (int i = 0; i < BLOQUE; i++) {
        std::cout << transferido[i] << ((i + 1) % 10 == 0 ? '\n' : ' ');
    }
    std::cout << '\n';

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
