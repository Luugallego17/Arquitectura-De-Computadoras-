#include <fstream>
#include <iostream>

const int TOTAL = 1000;

int main()
{
    std::ofstream archivo("datos.txt");
    if (!archivo) {
        std::cerr << "Error: no se pudo crear datos.txt\n";
        return 1;
    }

    for (int i = 0; i < TOTAL; i++) {
        archivo << i << '\n';
    }

    std::cout << "Archivo datos.txt generado con " << TOTAL
              << " enteros (0 a " << TOTAL - 1 << ").\n";
    return 0;
}
