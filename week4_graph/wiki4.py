import sys
from collections import deque
import time


class Wikipedia:
    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):
        # A mapping from a page ID (integer) to the page title.
        # For example, self.titles[1234] returns the title of the page whose
        # ID is 1234.
        self.titles = {}

        # A set of page links.
        # For example, self.links[1234] returns an array of page IDs linked
        # from the page whose ID is 1234.
        self.links = {}

        # Read the pages file into self.titles.
        with open(pages_file) as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()

    # Find the longest titles. This is not related to a graph algorithm at all
    # though :)
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()

    # Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()

    # Return the page title to which the page ID is connected
    def get_ID_from_title(self, title: str) -> int:
        for key, value in self.titles.items():
            if value == title:
                return key

    # 最短経路までに探索したノードたちを辿り、startからgoalまでの最短経路を返す
    # |node_pair|: 最短経路までに探索したノードたちを親子関係を保存しながら順番に格納したもの. {親ノード: 子ノード}
    # |goal|: 目的のページID
    def return_shortest_path(self, node_pair: dict[int : list[int]], goal: int) -> list[int]:
        shortest_path = deque()
        # 辞書型をリスト型に変換
        node_pair_deque = deque(node_pair.items())  # [(node,[child]),...]
        target = goal
        shortest_path.appendleft(target)

        # goalからstartまでを逆順にたどる
        while len(node_pair_deque) > 0:  # 最初の要素(-1, [start])はdummy
            pair = node_pair_deque.pop()
            parent, children = pair[0], pair[1]
            if target in children:
                target = parent
                shortest_path.appendleft(target)
        return shortest_path

    # Find the shortest path.
    # |start|: The title of the start page.
    # |goal|: The title of the goal page.
    def find_shortest_path(self, start: str, goal: str):
        # ------------------------#
        # Write your code here!  #
        # page titleをpage IDに変換
        start_id = self.get_ID_from_title(start)
        goal_id = self.get_ID_from_title(goal)
        is_found = False  # 最短経路が見つかったか否か
        deque_list = deque()
        enqueued_node_pair: dict[int : list[int]] = {}  # enqueueしたノードたちの親子関係. {親ノード:list[子ノード]}
        visited_nodes: dict[int:bool] = {}  # {node: enqueueされたかどうか}
        # visited_nodesの初期化
        for id in self.titles.keys():
            visited_nodes[id] = False

        deque_list.append(start_id)
        visited_nodes[start_id] = True

        while (len(deque_list) > 0) and (is_found is False):
            node = deque_list.popleft()
            # nodeのchildを順番に見ていく
            for child in self.links[node]:
                if visited_nodes[child]:
                    continue
                deque_list.append(child)
                visited_nodes[child] = True
                # 初めてnodeのchildを辿るとき
                if node not in enqueued_node_pair.keys():
                    enqueued_node_pair[node] = []
                enqueued_node_pair[node].append(child)
                if child == goal_id:
                    is_found = True
                    break
        shortest_path_id = self.return_shortest_path(enqueued_node_pair, goal_id)
        shortest_path_title = [self.titles[id] for id in shortest_path_id]

        print(f"shortest_path from {start} to {goal} is {shortest_path_title}")
        # ------------------------#

    # Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        page_rank_child = {}  # 更新後のページランク
        page_rank_parent = {}  # 元のページランク
        threshold = 0.001  # 更新の前後でページランクの差がこれ以下なら収束とする
        number_of_nodes = len(self.titles)
        # ページランクの初期化
        for node in self.titles:
            page_rank_child[node] = 0
            page_rank_parent[node] = 1
        sum_of_page_rank = sum(page_rank_parent.values())

        diff = 100
        while diff > threshold:
            diff = 0
            for node in self.titles:
                page_rank_child[node] += 0.15
                # scoreをparentからchildrenに振り分ける
                # childを持たないノード
                if not self.links[node]:
                    score = (page_rank_parent[node] * 0.85) / number_of_nodes
                    for node in self.titles:
                        page_rank_child[node] += score
                # childを持つノード
                else:
                    score = (page_rank_parent[node] * 0.85) / len(self.links[node])
                    for child in self.links[node]:
                        page_rank_child[child] += score
            assert round(sum(page_rank_child.values())) == sum_of_page_rank

            # 更新の前後でのページランクの差を比較
            for node in self.titles:
                diff += (page_rank_parent[node] - page_rank_child[node]) ** 2
            if diff <= threshold:
                break

            # 次の計算のための準備
            for node in self.titles:
                page_rank_parent[node] = page_rank_child[node]  # ページランクの更新
                page_rank_child[node] = 0  # 初期化

        # 最もページランクが高いページを求める
        max_rank = -1
        most_popular_node = -1
        for node, page_rank in page_rank_child.items():
            if page_rank >= max_rank:
                max_rank = page_rank
                most_popular_node = node

        print(f"most popular page is {most_popular_node}")

    # Calculate the page ranks and print the most popular pages.0
    # スライド通りに実装
    def find_most_popular_pages_original(self):
        # ------------------------#
        # Write your code here!  #
        page_rank_child = {}  # 更新後のページランク
        page_rank_parent = {}  # 元のページランク
        threshold = 0.001  # 大きめに
        number_of_nodes = len(self.titles)
        # ページランクの初期化
        for node in self.titles:
            page_rank_child[node] = 0
            page_rank_parent[node] = 1

        sum_of_page_rank = sum(page_rank_parent.values())
        diff = 100
        while diff > threshold:
            diff = 0
            # scoreをparentからchildrenに振り分ける
            for parent in self.titles:
                # childを持たないノード
                if not self.links[parent]:
                    for node in self.titles:
                        page_rank_child[node] += page_rank_parent[parent] / number_of_nodes
                # childを持つノード
                else:
                    for child in self.links[parent]:
                        score = (page_rank_parent[parent] * 0.85) / len(self.links[parent])
                        page_rank_child[child] += score
                    for node in self.titles:
                        score = (page_rank_parent[parent] * 0.15) / number_of_nodes
                        page_rank_child[node] += score

            assert round(sum(page_rank_child.values())) == sum_of_page_rank

            # 更新の前後でのページランクの差を比較
            for parent in self.titles:
                diff += (page_rank_parent[parent] - page_rank_child[parent]) ** 2
            if diff <= threshold:
                break

            # 次の計算のための準備
            for node in self.titles:
                page_rank_parent[node] = page_rank_child[node]  # ページランクの更新
                page_rank_child[node] = 0  # 初期化

        # 最もページランクが高いページを求める
        max_rank = -1
        most_popular_node = -1
        for node, page_rank in page_rank_child.items():
            if page_rank >= max_rank:
                max_rank = page_rank
                most_popular_node = node

        print(f"most popular page is {most_popular_node}")
        # ------------------------#

    # Do something more interesting!!
    def find_something_more_interesting(self):
        # ------------------------#
        # Write your code here!  #
        # ------------------------#
        pass


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # wikipedia.find_longest_titles()
    # wikipedia.find_most_linked_pages()
    # wikipedia.find_shortest_path("A", "E")  # for small
    # wikipedia.find_shortest_path("渋谷", "小野妹子")  # for large
    # wikipedia.find_shortest_path("著作権の保護期間", "パリ")  # for medium
    # wikipedia.find_shortest_path("著作権の保護期間", "ナデジダ・チジョワ")  # for medium
    # wikipedia.find_shortest_path("著作権の保護期間", "ライフコーポレーション")  # for medium
    wikipedia.find_most_popular_pages()