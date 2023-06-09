import networkx as nx
from collections import defaultdict
import math
import numpy as np
import queue
import random


def print_basic_properties(dataset, display_interm_results = False) -> None:

    """Считает и выводит основные свойства статического простого графа, 
        полученного из исходного темпорального графа путем добавления всех появившихся ребер за время 0<=t<=1 и удаления дубликатов ребер. \n
        Параметр display_interm_results отвечает за показ промежуточных результатов""" 

    ### Пункт 1.1

    def bfs(adjList, unvisited) -> list:
        WCC = set()  # weakly connected component
        queue = list()  # queue<int>
        
        src_node = unvisited.pop()
        queue.append(src_node)
        
        # loop until the queue is empty
        while queue:
            # pop the front node of the queue and add it to WCC
            current_node = queue.pop(0)
            WCC.add(current_node)
            
            # check all the neighbour nodes of the current node
            for neighbour_node in adjList[current_node]:
                to = neighbour_node # neighbour_node - это to_ind
                if to in unvisited:
                    unvisited.remove(to)
                    queue.append(to)

        return WCC

    graph = defaultdict(set)  # исходный граф

    for line in dataset:
        [from_ind, to_ind] = [int(x) for x in line.split()]
        graph[from_ind].add(to_ind)
        graph[to_ind].add(from_ind)


    sum_E = 0
    for i in graph.items():
        sum_E += len(i[1])
    E = sum_E // 2

    # максимальное число ребер в полном графе с количеством вершин V - 1
    max_E = (len(graph))*(len(graph) - 1) // 2

    print("Number of vertexes:", len(graph))
    print("Number of edges:", E)
    print("Maximal number of edges:", max_E)
    print("Density:", E / max_E)

    count = 0
    max_size = 0
    max_WCC = set()
    uniqueVertexes = list(graph.keys())
    while len(uniqueVertexes) > 0:
        WCC = bfs(graph, uniqueVertexes)
        size = len(WCC)
        if size > max_size:
            max_size = size
            max_WCC = WCC
        count += 1
        if display_interm_results:
            print("WCC", count, "size", size, ":", WCC)

    print("Количество компонент слабой связности: ", count)
    if display_interm_results: 
        print("Наибольшая КСС: ", max_WCC)
    print("Мощность наибольшей КСС: ", max_size)
    print("Отношение мощности наибольшей КСС к общему количеству вершин: ", max_size / len(graph))

    
    ### Пункт 1.2.

    ver = defaultdict(set) # подграф с наибольшей КСС 

    for line in dataset:
        [from_ind, to_ind] = [int(x) for x in line.split()]
        if (from_ind and to_ind) in max_WCC:
            ver[from_ind].add(to_ind)
            ver[to_ind].add(from_ind) 
        
    #print("подграф с наибольшей КСС: ", ver) 

    n = len(ver) # кол-во вершин для 2a

    # random_v = random.choices(list(max_WCC), k=n) 
    #random_v =random.sample(list(max_WCC), k=n) # мн-во вершин для 2a
    #print('random_v', random_v)
    V = len(graph) + 1
    def dijkstra_algo(adjList, start) -> list:
      min_queue = queue.PriorityQueue()
      distance = [np.inf] * V

      min_queue.put((0, start))
      distance[start] = 0

      while not min_queue.empty():
        u = min_queue.get()[1]
        for v in adjList[u]:
          weight = 1
          if distance[v] > distance[u] + weight:
            distance[v] = distance[u] + weight
            min_queue.put((distance[v], v))


      pairs_of_vertexes = [] # at distance = 2
      for i in range(start, V):
        if distance[i] == 2:
          pairs_of_vertexes.append((start, i))

                # print(i, ":", distance[i])

            # print(pairs_of_vertexes)
            # print()

      # print('k',distance) 
      distance[0] = 0
      if np.inf in distance: 
        distance[distance.index(np.inf)] = 0 
      # print(distance)     
      return max(distance), distance




    def find_eccentrisity(g, v) -> list: # поиск массива экцентрисететов g - граф, v - мн-во вершин, по которым идёт поиск 
        e = []
        e_1 = []
        for i in v: 
            m = dijkstra_algo(g, i)
            e.append(m[0]) 
            e_1.append(m[1])
        return e, e_1

    #print(ver)
    print("max_WCC", max_WCC)
    eccentricity = find_eccentrisity(ver, max_WCC)
    print('-------')

    print("Диаметр:", max(eccentricity[0]), "Совпадает со встроенной ф-цией?")
    print("Радиус:", min(eccentricity[0]), "Совпадает со встроенной ф-цией?")
    print("90 процентиля расстояния (геодезического) между вершинами графа:", np.percentile(eccentricity[1], 90))


    def bfs_snowball(visited, adjList, unvisited, lenght):
        WCC = set()  # weakly connected component
        queue = list()  # queue<int>
        edges = defaultdict(set)
        queue.append(visited[0])
        queue.append(visited[1])

        # loop until the queue is empty
        while queue and len(WCC) < lenght:
            # pop the front node of the queue and add it to WCC
            current_node = queue.pop(0)
            WCC.add(current_node)
            # check all the neighbour nodes of the current node
            for neighbour_node in adjList[current_node]:
                to = neighbour_node  # neighbour_node - это tuple(to, weight, time)
                if to in unvisited:
                    unvisited.remove(to)
                    queue.append(to)
        # print("snow-ball component 1", WCC)
        max_size = 0
        while len(WCC) > 0:
            new_WCC = bfs(adjList, WCC)
            # print(WCC)
            size = len(new_WCC)
            if size > max_size:
                max_size = size
                new_max_WCC = new_WCC

        #print("snow-ball component", max_WCC)
        for v in new_max_WCC:
            for neighbour_node in adjList[v]:
                if neighbour_node in new_max_WCC:
                    edges[v].add(neighbour_node)
                    edges[neighbour_node].add(v)

        return edges, new_max_WCC




    random_v = random.sample(list(max_WCC), k=2)

    print('max_WCC', max_WCC)

    # max_WCC_1 = max_WCC
    # edges, new_WCC = bfs_snowball(random_v, graph, max_WCC_1, len(max_WCC_1))
    # # #print("Snowball: ", edges)
    # print("Size snowball component: ", len(new_WCC))
    # ###############################################
    # print('max_WCC', max_WCC)
    # matrix_of_shortest_paths = find_eccentrisity(edges, new_WCC)
    #
    # print("Диаметр snowball:", max(matrix_of_shortest_paths[0]))
    # print("Радиус snowball:", min(matrix_of_shortest_paths[0]))
    # print("90 процентиля расстояния (геодезического) между вершинами графа snowball:", np.percentile(matrix_of_shortest_paths[1], 90))



    ### Пункт 1.3. Посчитать средний кластерный коэффициент для наибольшей КСС
    #
    def local_clustering_coefficient(adjList, u) -> float:

        # сет соседей вершины u
        adj2u_set = set()
        for v in adjList[u]:
            adj2u_set.add(v)

        gamma_u = len(adj2u_set)

        if (gamma_u < 2):
            return 0

        L_u = countEdgesInSet(adjList, adj2u_set)

        Cl_u = 2 * L_u / (gamma_u * (gamma_u - 1))

        return Cl_u


    # считает количество ребер между вершинами в сете vertexes_set
    def countEdgesInSet(adjList, vertexes_set):
        sum = 0
        for node in vertexes_set:
            for neighbour_node in adjList[node]:
                if neighbour_node in vertexes_set:
                    sum+=1
        return sum // 2


    sum_Cl = 0
    for vertex in max_WCC:
        sum_Cl+=local_clustering_coefficient(graph, vertex)

    average_Cl = sum_Cl / len(max_WCC)
    print("Средний кластерный коэффициент для наибольшей КСС:", average_Cl)


    ### 1.4. Посчитать коэффициент ассортативности по степени вершин
    ### Использовался алгоритм из данного видео https://www.youtube.com/watch?v=gzWlSPxpHZE&t=191s

    def pearson_correlation_coefficient_by_degree(adjList, edge_list):
        X = []
        Y = []

        for edge in edge_list:
            x = edge[0]
            y = edge[1]
            X.append(len(adjList[x]))
            Y.append(len(adjList[y]))

        avg_x = sum(X) / len(X)
        avg_y = sum(Y) / len(Y)

        XminusAvg_x = [k - avg_x for k in X]
        YminusAvg_y = [k - avg_y for k in Y]

        Z = [x * y for x, y in zip(XminusAvg_x, YminusAvg_y)]

        sq_XminusAvg_x = [x ** 2 for x in XminusAvg_x]
        sq_YminusAvg_y = [y ** 2 for y in YminusAvg_y]

        sum_sq_x = sum(sq_XminusAvg_x)
        sum_sq_y = sum(sq_YminusAvg_y)
        sum_Z = sum(Z)

        if (sum_sq_x == 0 or sum_sq_y == 0):
            print("correlation coef is not defined!")
            return 0

        r = sum_Z / ((sum_sq_x * sum_sq_y) ** 0.5)

        return r

    # считываем из датасета список ребер, игнорируя их направленность и дубликаты (вес и время тоже игнорируем)
    edge_list = set()
    for line in dataset:
        [from_ind, to_ind] = [int(x) for x in line.split()]
        edge_list.add((from_ind, to_ind))
        edge_list.add((to_ind, from_ind))


    # Сравнение результатов с алгоритмом из библиотеки networkx
    my_r = pearson_correlation_coefficient_by_degree(graph, edge_list)
    print("my_pearson_correlation_coefficient_by_degree:", my_r)

    G = nx.Graph(edge_list)
    nx_r = nx.degree_pearson_correlation_coefficient(G)
    print("nx_pearson_correlation_coef: ", nx_r)

    print("error: ", abs(nx_r - my_r))

#1.2b snowball
    max_WCC_1 = max_WCC
    edges, new_WCC = bfs_snowball(random_v, graph, max_WCC_1, len(max_WCC_1))
    # #print("Snowball: ", edges)
    print("Size snowball component: ", len(new_WCC))
    matrix_of_shortest_paths = find_eccentrisity(edges, new_WCC)

    print("Диаметр snowball:", max(matrix_of_shortest_paths[0]))
    print("Радиус snowball:", min(matrix_of_shortest_paths[0]))
    print("90 процентиля расстояния (геодезического) между вершинами графа snowball:", np.percentile(matrix_of_shortest_paths[1], 90))
