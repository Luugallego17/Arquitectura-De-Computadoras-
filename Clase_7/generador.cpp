/*
 * Práctica: transferencia de bloques de memoria — programa auxiliar
 * Materia:  Arquitectura de Computadoras
 * Alumna:   Luna Saleth Gallego Martinez
 * Tarea:    #9 — Generar el archivo de datos en memoria secundaria
 *
 * Genera el archivo "datos.txt" con 1000 números enteros secuenciales
 * (0 a 999), uno por línea. Se usan valores secuenciales a propósito:
 * así el valor de cada elemento coincide con su índice y es fácil
 * verificar después qué elementos se transfirieron (los índices 500 a
 * 599 deben contener los valores 500 a 599).
 *
 * Compilar:  g++ generador.cpp -o generador
 * Ejecutar:  ./generador
 */
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
