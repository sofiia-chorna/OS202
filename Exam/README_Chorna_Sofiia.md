```
lscpu
```
Resultat d'éxecution :
```
Architecture:            x86_64
  CPU op-mode(s):        32-bit, 64-bit
  Address sizes:         39 bits physical, 48 bits virtual
  Byte Order:            Little Endian
CPU(s):                  8
  On-line CPU(s) list:   0-7
Vendor ID:               GenuineIntel
  Model name:            11th Gen Intel(R) Core(TM) i7-1165G7 @ 2.80GHz
    CPU family:          6
    Model:               140
    Thread(s) per core:  2
    Core(s) per socket:  4
    Socket(s):           1
    Stepping:            1
    CPU max MHz:         4700,0000
    CPU min MHz:         400,0000
    BogoMIPS:            5606.40
Virtualization features: 
  Virtualization:        VT-x
Caches (sum of all):     
  L1d:                   192 KiB (4 instances)
  L1i:                   128 KiB (4 instances)
  L2:                    5 MiB (4 instances)
  L3:                    12 MiB (1 instance)
```

Cela indique que je dispose d'un processeur Intel Core i7 de 11e génération avec 8 cœurs, 4 cœurs par socket et 2 threads par cœur. La mémoire cache comprend 192 KiB pour L1d, 128 KiB pour L1i, 5 MiB pour L2 et 12 MiB pour L3.

## Exécution
```
mpiexec -n <number of processus> python3 colorize1.py
```
Par example, pour exécuter avec 4 processus :
```
mpiexec -n 4 python3 colorize1.py
```

Pour le programme sans MPI, exécutez :
```
python3 colorize.py
```

## Résultats
```markdown
| N processes            | MPI Execution Time | Speedup               |
|------------------------|--------------------|-----------------------|
|           1            |     2.8145454      |        100%           |
|           2            |     1.8266667      |        154%           |
|           3            |     2.5645         |        109%           |
|           4            |     2,83333334     |        99%            |

Pour Q1, nous avons partagés l'image en tranches (N = numéro de processeurs) ou chaque a coloré sa partie, puis le processus racine a rassemblé toutes les fragmenets sur l'image finale.
Pour Q2, nous avons utilisé la strategie maître-esclave, maître est responsable pour le calcul et la construction de l'image finale.


