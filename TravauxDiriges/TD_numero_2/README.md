## 1 Exercices à rendre
### 1.1 Question du cours
Reprendre l’exercice sur l’interblocage donné dans le cours et décrivez deux scénarios :

```
if (rank==0)
{
    MPI_Recv(rcvbuf, count, MPI_DOUBLE, 1, 101, commGlob, &status);
    MPI_Send(sndbuf, count, MPI_DOUBLE, 1, 102, commGlob);
}
else if (rank==1)
{
    MPI_Recv(rcvbuf, count, MPI_DOUBLE, 0, 102, commGlob, &status);
    MPI_Send(sndbuf, count, MPI_DOUBLE, 0, 101, commGlob);
}
```

1. Un premier scénario où il n’y a pas d’interblocage ;
```
MPI_Request request;
MPI_Status  status;
int request_complete = 0;

// Rank 0 sends, rank 1 receives
if (rank == 0)
{
  MPI_Isend(buffer, buffer_count, MPI_INT, 1, 0, MPI_COMM_WORLD, &request);

  // Do some work while waiting for process 1 to be ready
  while (has_work)
  {
    do_work();

    // Test if the request is not already fulfilled
    if (!request_complete)
    {
       MPI_Test(&request, &request_complete, &status);
    }
  }

  // No more work, wait for the request to be complete if it's not the case
  if (!request_complete)
  {
    MPI_Wait(&request, &status);
  }
}
else
{
  MPI_Irecv(buffer, buffer_count, MPI_INT, 0, 0, MPI_COMM_WORLD, &request);

  // Wait for the message to come
  MPI_Wait(&request, &status);
}
```

2. Un deuxième scénario où il y a interblocage.
```
if (rank == 0)
{
    MPI_Recv(rcvbuf, count, MPI_DOUBLE, 1, 101, commGlob, &status);
    MPI_Send(sndbuf, count, MPI_DOUBLE, 1, 102, commGlob);
}
else if (rank == 1)
{
    MPI_Recv(rcvbuf, count, MPI_DOUBLE, 0, 102, commGlob, &status);
    MPI_Send(sndbuf, count, MPI_DOUBLE, 0, 101, commGlob);
}
```

Quelle est à votre avis la probabilité d’avoir un interblocage ?

À mon avis, la probabilité d'interblocage dépend de la façon dont les messages sont échangés entre les processus et de la taille du système. Dans cet exemple, si les messages sont de taille suffisamment petite et que le réseau MPI est rapide, il est possible que l'interblocage ne se produise pas souvent. Cependant, cela peut varier en fonction de nombreux autres facteurs, y compris la charge du système et les caractéristiques de la communication réseau.

Pour éviter l'interblocage, il est important de concevoir vos algorithmes de communication de manière à minimiser les attentes mutuelles et à utiliser des techniques telles que le partage des ressources et la communication non bloquante lorsque cela est possible.