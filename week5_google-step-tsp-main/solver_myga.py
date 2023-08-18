#!/usr/bin/env python3

import sys
import random
import math
import copy

from common import print_tour, read_input
import solver_mytsp as mytsp

### References ###
#
# 「遺伝的アルゴリズム（GA）巡回セールスマン問題」（閲覧日: 2023/06/14）
# https://qiita.com/kkttm530/items/d1e8429a7a7f600986c3
#
##################

# 要素数 N のランダム配列を num 個生成
def generate_routes(N, num):
    routes = [random.sample(range(N), N) for _ in range(num)]
    return routes

# solver を使ってルートを num 個生成
def generate_routes_by_solver(cities, num):
    routes = []
    iteration = 30
    for _ in range(num):
        routes.append(mytsp.solve(cities, iteration))
    return routes

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

# 各ルートの評価
def evaluate(routes, dist_table, loop=0):
    evaluate_value = []
    for i in range(len(routes)):
        temp_evaluate_value = total_distance(routes[i], dist_table)
        evaluate_value.append(temp_evaluate_value)
    return evaluate_value

def selection(routes, evaluate_value, tournament_select_size, tournament_size, elite_select_num, ascending=False):
    select_pop = []
    elite_pop = []

    # トーナメント選択
    while True:
        select = random.sample(evaluate_value, tournament_size)
        select.sort(reverse=ascending)
        for i in range(tournament_select_size):
            value = select[i]
            index = evaluate_value.index(value)
            select_pop.append(routes[index])
        
        # 半減するまで選抜
        if len(select_pop) >= len(routes) // 2:
            break
    
    # エリート保存
    sort_evaluate_value = copy.deepcopy(evaluate_value)
    sort_evaluate_value.sort(reverse=ascending)
    for i in range(elite_select_num):
        value = sort_evaluate_value[i]
        index = evaluate_value.index(value)
        elite_pop.append(routes[index])
    
    return select_pop, elite_pop

# 確率的に順序交差を行う
def crossover(select_pop, crossover_prob):
    cross_pop = random.sample(select_pop, 2)
    pop_1 = cross_pop[0]
    pop_2 = cross_pop[1]

    check_prob = random.randint(0, 100)
    if check_prob <= crossover_prob:
        new_pop_1 = []
        cut_index = random.randint(1, len(pop_1)-2)
        new_pop_1.extend(pop_1[:cut_index])
        for i in range(len(pop_1)):
            if pop_2[i] not in new_pop_1:
                new_pop_1.append(pop_2[i])
        
        new_pop_2 = []
        new_pop_2.extend(pop_1[cut_index:])
        for i in range(len(pop_1)):
            if pop_2[i] not in new_pop_2:
                new_pop_2.append(pop_2[i])
        
        return new_pop_1, new_pop_2

    else:
        return pop_1, pop_2

# route の順番をランダムで入れ替える
def mutation(pop, mutation_prob, N):
    check_prob = random.randint(0, 100)

    if check_prob <= mutation_prob:
        select_num = [i for i in range(N)]
        select_index = random.sample(select_num, 2)

        pop[select_index[0]], pop[select_index[1]] = pop[select_index[1]], pop[select_index[0]]
    
    return pop

# 各ルートを 2-opt で改善
def improve_routes(routes, dist_table):
    for route in routes:
        mytsp.improve_route(route, dist_table)

def solve(cities, generation):
    num_of_cities = len(cities)
    dist_table = make_dist_table(cities)
    pop_num = 20

    # 選択のパラメータ
    tournament_size = 10
    tournamnet_selest_num = 2
    elite_select_num = 1

    # 交叉の確率
    crossover_prob = 50

    # 突然変異の確率
    mutation_prob = 10

    # routes = generate_routes(num_of_cities, pop_num)
    routes = generate_routes_by_solver(cities, pop_num)

    evaluate_value = evaluate(routes, dist_table)

    smallest_value = min(evaluate_value)
    index = evaluate_value.index(smallest_value)
    smallest_route = routes[index]
    for loop in range(generation):
        select_pop, elite_pop = selection(
            routes, evaluate_value, tournamnet_selest_num, tournament_size, elite_select_num)
        
        next_pop = []
        while True:
            pop_1, pop_2 = crossover(select_pop, crossover_prob)
            pop_1 = mutation(pop_1, mutation_prob, num_of_cities)
            pop_2 = mutation(pop_2, mutation_prob, num_of_cities)

            next_pop.append(pop_1)
            next_pop.append(pop_2)

            if len(next_pop) >= pop_num - elite_select_num:
                break

        next_pop.extend(elite_pop)
        improve_routes(next_pop, dist_table)
        evaluate_value = evaluate(next_pop, dist_table, loop=loop+1)
        routes = next_pop

        smallest__value_temp = min(evaluate_value)
        if smallest__value_temp < smallest_value:
            index = evaluate_value.index(smallest__value_temp)
            smallest_route = routes[index]

        print(smallest__value_temp)

    return smallest_route


if __name__ == '__main__':
    assert len(sys.argv) > 2
    tour = solve(read_input(sys.argv[1]), int(sys.argv[2]))
    print_tour(tour)