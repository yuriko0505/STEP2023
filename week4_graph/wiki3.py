import sys
import collections

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

    
    # Find the shortest path.
    # |start|: The title of the start page.
    # |goal|: The title of the goal page.
    def find_shortest_path(self, start, goal):
        start_id = [k for k, v in self.titles.items() if v == start][0] #スタートページのID
        goal_id = [k for k, v in self.titles.items() if v == goal][0] #ゴールページのID
        d = collections.deque() #キューを表す変数
        visited = {} #すでにエンキューしたIDを格納する    key : ID    value : True
        visited[start_id] = True
        connection = {} #あるIDと繋がっている一つ前のIDを格納する    key : ID    value : 一つ前のID
        connection[start_id] = None
        d.append(start_id) #エンキュー
        while len(d) != 0:
            temp_node = d.popleft() #デキュー
            if temp_node == goal_id: #ゴールページが見つかったとき
                break
            for id in self.links[temp_node]:
                if not id in visited:
                    d.append(id) #エンキュー
                    visited[id] = True
                    connection[id] = temp_node
        
        if temp_node != goal_id:
            print("Not found")
            return
        
        shortest_path = [] #最短経路となるページを格納する配列
        while temp_node != None:
            shortest_path.append(self.titles[temp_node])
            temp_node = connection[temp_node]
        shortest_path.reverse()
        print("The shortest path is:")
        for page in shortest_path:
            print(page)
    

    # Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        pagerank = {} #IDがkey、ページランクがvalue
        prev_pagerank = {} #一つ前に更新したページランク　IDがkey、ページランクがvalue
        for id in self.titles.keys():
            prev_pagerank[id] = 1.0 #ページランクを初期値1.0にする
        
        while True:
            for id in self.titles.keys():
                pagerank[id] = 0.0 #ページランクの初期化

            added_pagerank = 0.0 #全ノードに共通して分配されるページランク

            for id in self.titles.keys():
                if self.links[id] != []: #隣接ノードがある場合
                    divided_pagerank = prev_pagerank[id] / len(self.links[id]) #隣接ノード一つあたりに振り分けられるページランク
                    for connected_id in self.links[id]:
                        pagerank[connected_id] += 0.85 * divided_pagerank #ページランクの85%を隣接ノードへ振り分け
                    added_pagerank += 0.15 * prev_pagerank[id] / len(self.titles.keys()) #残りの15%を全ノードに分配
                else: #隣接ノードがない場合
                    added_pagerank += 1.0 * prev_pagerank[id] / len(self.titles.keys()) #100%を全ノードに分配
                
            for id in self.titles.keys():
                pagerank[id] += added_pagerank #全ノードに共通して分配されるページランクを振り分け
            
            for id in self.titles.keys():
                if abs(pagerank[id] - prev_pagerank[id]) >= 1.0: #ページランクが収束していないとき
                    break
            
            #print(sum(pagerank.values())) #ページランクの合計値

            if id == max(self.titles): #ページランクが収束したとき
                break
            
            prev_pagerank = pagerank.copy()

        sorted_pagerank = sorted(pagerank.items(), key=lambda x:x[1], reverse=True) #ページランクが大きい順にソート
        print("The most popular pages are:")
        for i in range(10):
            print(self.titles[sorted_pagerank[i][0]])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # wikipedia.find_longest_titles()
    # wikipedia.find_most_linked_pages()
    # wikipedia.find_shortest_path("渋谷", "パレートの法則")
    wikipedia.find_most_popular_pages()