#!/usr/bin/env python3

import sys
import math
import copy
import random
import itertools

from common import print_tour, read_input


def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

def make_dist_table(cities):
    num_of_cities = len(cities)
    table = [[0 for _ in range(num_of_cities)] for _ in range(num_of_cities)]
    for i in range(num_of_cities):
        for j in range(i+1, num_of_cities):
            table[i][j] = table[j][i] = distance(cities[i], cities[j])
    return table

def total_distance(route, dist_table):
    sum = 0
    for i in range(-1, len(route)-1):
        sum += dist_table[route[i]][route[i+1]]
    return sum

# Return route
# Greedy
def initial_route(cities, dist_table):
    N = len(cities)
    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]

    while unvisited_cities:
        next_city = min(unvisited_cities,
                        key=lambda city: dist_table[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    return tour

# Fisher-Yates shuffle
def random_shuffle(route):
    random.seed()
    for i in range(len(route), 1, -1):
        a = i - 1
        b = random.randrange(1e8) % i
        if b != 0:
            route[a], route[b] = route[b], route[a]


def solve(cities, iter):
    dist_table = make_dist_table(cities)
    route = initial_route(cities, dist_table)

    best_route = copy.deepcopy(route)
    best_dist = total_distance(route, dist_table)

    for i in range(iter):
        if len(cities) <= 512:
            improve_route(route, dist_table)
        else:
            improve_route_for_large(route, dist_table)
        
        dist_temp = total_distance(route, dist_table)
        print("iter: %d  dist:%f" % (i, dist_temp))
        if dist_temp < best_dist:
            best_dist = dist_temp
            best_route = copy.deepcopy(route)    
        if len(cities) <= 512:
            random_shuffle(route)
    
    print(best_dist)
    return best_route

def improve_route(route, dist_table):
    num_of_cities = len(route)
    # 2-opt
    improved = True
    # time = 0
    while improved:
        # print("improved: %d" %(time))
        improved = False
        for i in range(num_of_cities-2):
            for j in range(i+2, num_of_cities):
                before = dist_table[route[i]][route[i+1]] + dist_table[route[j]][route[(j+1)%num_of_cities]]
                after  = dist_table[route[i]][route[j]] + dist_table[route[i+1]][route[(j+1)%num_of_cities]]
                
                if after < before:
                    route[i+1], route[j] = route[j], route[i+1]
                    improved = True
        # time += 1
    # # 3-opt
    # broken = True
    # while broken:
    #     broken = False
    #     for i in range(1, len(route)):
    #         for j in range(i+1, len(route)):
    #             for k in range(j+1, len(route)):
    #                 for _ in range(2):
    #                     route[i], route[j], route[k] = route[j], route[k], route[i]  # Swap nodes
    #                     temp_dist = total_distance(route, dist_table)
                        
    #                     if temp_dist < shortest_distance:
    #                         shortest_distance = temp_dist
    #                         shortest_route = copy.deepcopy(route)
    #                         broken = True
    #                         break
    #                     route[i], route[j], route[k] = route[j], route[k], route[i]

def improve_route_for_large(route, dist_table):
    num_of_cities = len(route)
    # 2-opt
    improved = True

    num_of_swap_points = 1<<9
    swap_points = random.sample(range(num_of_cities), num_of_swap_points)
    swap_points.sort()

    time = 0
    while improved:
        # print("improved: %d" %(time))
        improved = False
        for (i, j) in itertools.combinations(swap_points, 2):
            before = dist_table[route[i]][route[i+1]] + dist_table[route[j]][route[(j+1)%num_of_cities]]
            after  = dist_table[route[i]][route[j]] + dist_table[route[i+1]][route[(j+1)%num_of_cities]]
            if after < before:
                flipped_path = route[i+1 : j+1]
                route[i+1: j+1] = flipped_path[:: -1]
                improved = True
        time += 1
        if (time > 1000):
            break

if __name__ == '__main__':
    assert len(sys.argv) > 2
    tour = solve(read_input(sys.argv[1]), int(sys.argv[2]))
    # print_tour(tour)