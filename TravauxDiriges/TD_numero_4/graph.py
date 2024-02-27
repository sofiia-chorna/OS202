import matplotlib.pyplot as plt

num_processes = [1, 2, 3, 4]
execution_times = [6.32e-02, 1.91e-02, 8.52e-03, 7.66e-03]
display_times = [1.71e-02, 5.62e-03, 4.56e-03, 2.13e-03]

# Créer un graph
plt.figure(figsize=(10, 6))
plt.bar(num_processes, execution_times, color='blue', label='Temps d\'exécution')
plt.bar(num_processes, display_times, color='red', label='Temps d\'affichage')
plt.xlabel('Nombre de processus')
plt.ylabel('Temps (secondes)')
plt.title('Temps d\'exécution et d\'affichage par rapport au nombre de processus')
plt.xticks(num_processes)
plt.legend()

# Affichage du graphique
plt.show()
