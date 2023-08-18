import csv
import sys
import math
import random
from common import read_input
from typing import List


# 2つの都市の座標から距離を計算する関数
def distance(city1: List[float], city2: List[float]) -> float:
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


# 初期巡回路を生成する関数
def generate_initial_tour(cities: List[List[float]]) -> List[int]:
    N = len(cities)
    visited = [False] * N
    tour = []
    current_city = random.randint(0, N-1)  # ランダムに始点の都市を選択
    tour.append(current_city)  # 始点の都市を巡回路に追加
    visited[current_city] = True  # 始点の都市を訪問済みにする

    for _ in range(N - 1):  # 残りの都市を訪問するためのループ
        min_distance = sys.float_info.max  # 最小距離を表す変数を最大の値で初期化
        next_city = -1  # 次に訪れる都市のindexを初期化

        for i in range(N):  # 未訪問の都市を探す
            if not visited[i] and distance(cities[current_city], cities[i]) < min_distance: # 未訪問の都市かつ現在の都市との距離が最小の場合
                min_distance = distance(cities[current_city], cities[i])  # 最小距離を更新
                next_city = i  # 次に訪れる都市のindexを更新

        tour.append(next_city)  # 次に訪れる都市を巡回路に追加
        visited[next_city] = True  # 次に訪れる都市を訪問済みにする
        current_city = next_city  # 現在の都市を更新

    return tour  # 生成された初期巡回路を返す


# 2-optを行う関数
def improve_tour(cities: List[List[float]], tour: List[int]) -> List[int]:
    N = len(cities)  # 都市の数を取得
    improved = True  # 改善フラグを初期化
    
    while improved:  # 改善がある限り繰り返す
        improved = False  # 改善フラグをリセット
        for i in range(1, N - 2):  # 巡回路のインデックスを順に取得
            for j in range(i + 1, N):  # i以降のインデックスを順に取得
                # 現在の巡回路の距離を計算
                dist_current = (distance(cities[tour[i-1]], cities[tour[i]]) + distance(cities[tour[j]], cities[tour[(j + 1) % N]]))
                # 辺を入れ替えた場合の距離を計算
                dist_new = (distance(cities[tour[i-1]], cities[tour[j]]) + distance(cities[tour[i]], cities[tour[(j + 1) % N]]))
                if dist_new < dist_current:  # 新しい巡回路の方が短い場合
                    tour[i:j+1] = reversed(tour[i:j+1])  # 辺を入れ替える
                    improved = True  # 改善フラグを立てる
    return tour  # 改善された巡回路を返す



# indexをcsvファイルに書き込む関数
def print_tour_indices(tour: List[int], output_filename: str):
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['index'])
        for city_index in tour:
            writer.writerow([city_index])


if __name__ == '__main__':
    for i in range(8):
        input_filename = f'input_{i}.csv'
        output_filename = f'output_{i}.csv'

        cities = read_input(input_filename)  # 入力ファイルから都市の座標を読み込む
        tour = generate_initial_tour(cities)  # 初期巡回路を生成
        improved_tour = improve_tour(cities, tour)  # 巡回路を改善

        print_tour_indices(improved_tour, output_filename)

        print(f'Output written to {output_filename}')