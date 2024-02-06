import matplotlib.pyplot as plt

sequential_time = 3.028447389602661
parallel_time = 2.4278180599212646

versions = ['Séquentielle', 'Parallèle']
execution_times = [sequential_time, parallel_time]

# Créer le graph
plt.figure(figsize=(8, 6))
plt.bar(versions, execution_times, color=['blue', 'orange'])
plt.xlabel('Version')
plt.ylabel('Temps d\'exécution (s)')
plt.title('Comparaison des temps d\'exécution (Séquentielle vs Parallèle)')
plt.show()
