#!/usr/bin/env python3

import itertools
import sys
import math
import re

from common import print_tour, read_input, format_tour

def distance(city1, city2):
	return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

def make_dist_matrix(cities):
	N = len(cities)
	dist_matrix = [[0] * N for i in range(N)]
	for i in range(N):
		for j in range(i, N):
			dist_matrix[i][j] = dist_matrix[j][i] = distance(cities[i], cities[j])
	return dist_matrix

def solve_greedy(cities, dist_matrix):
	N = len(cities)

	current_city = 0
	unvisited_cities = set(range(1, N))
	tour = [current_city]

	#1番近いところに行く
	while unvisited_cities:
		next_city = min(unvisited_cities,
						key=lambda city: dist_matrix[current_city][city])
		unvisited_cities.remove(next_city)
		tour.append(next_city)
		current_city = next_city
	return tour


def brute_force(cities):
	cities_permutations = list(itertools.permutations(cities))
	shortest_distance = float('inf') #最短距離を無限大にしておく
	total_distance = 0

	for cities_permutation in cities_permutations:
		total_distance = 0
		# current_city = (0, 0)
		current_city = cities_permutation[0]  #0->-1

		for next_city in cities_permutation[1:]:  # 1->0
			total_distance += distance(current_city, next_city)
			current_city = next_city
		# print("total: ", total_distance)

		if total_distance < shortest_distance:
			shortest_distance = total_distance
			print("shortest: ", shortest_distance)
			shortest_tour = [cities.index(city) for city in cities_permutation]
	return shortest_tour


def two_opt(cities):
	#距離行列を作る
	dist_matrix = make_dist_matrix(cities)
	#貪欲法で経路を求める
	tour = solve_greedy(cities, dist_matrix)
	#最適化
	N = len(cities)
	improved = True
	while improved:
		improved = False
		for i in range(0, N - 2):
			for j in range(i + 2, N):
				AD = dist_matrix[tour[i]][tour[i + 1]]
				BC = dist_matrix[tour[j]][tour[(j + 1) % N]]
				AB = dist_matrix[tour[i]][tour[j]]
				CD = dist_matrix[tour[i + 1]][tour[(j + 1) % N]]
				if AD + BC > AB + CD:
					#入れ替える
					tour_to_change = tour[i + 1 : j + 1]
					tour[i + 1 : j + 1] = tour_to_change[:: -1]
					improved = True
	return tour

if __name__ == '__main__':
	assert len(sys.argv) > 1

	cities = read_input(sys.argv[1])
	if len(cities) < 10:
		tour = brute_force(cities)
	else:
		tour = two_opt(cities)
	print_tour(tour)