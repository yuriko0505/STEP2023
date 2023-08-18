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

    def get_key_from_value(self, d, val):
        keys = [k for k, v in d.items() if v == val]
        if keys:
            return keys[0]
        return None
    
    # Find the shortest path.
    # |start|: The title of the start page.
    # |goal|: The title of the goal page.
    def find_shortest_path(self, start, goal):
        start_key = self.get_key_from_value(self.titles, start)
        if start_key is None:
            print("non-existent page: \"%s\"" %(start))
            return
        goal_key = self.get_key_from_value(self.titles, goal)
        if goal_key is None:
            print("non-existent page: \"%s\"" %(goal))
            return
        
        queue = collections.deque()
        visited = {}
        visited[start_key] = True
        prev_node = {}
        queue.append(start_key)
        shortest_path_exist = False
        while len(queue):
            node = queue.popleft()  # dequeue
            if node == goal_key:
                shortest_path_exist = True
                break
            for child in self.links[node]:  # add child nodes
                if not child in visited:
                    visited[child] = True
                    queue.append(child)
                    prev_node[child] = node
        
        if shortest_path_exist:
            node = goal_key
            path = [self.titles[node]]
            while node != start_key:
                node = prev_node[node]
                path.append(self.titles[node])
            path.reverse()
            for i in range(len(path)-1):
                print(path[i], end=" -> ")
            print(path[len(path)-1])
            return
        else:
            print("Not found")
            return

    # Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        num_of_pages = len(self.titles.keys())  # Actual number of links

        pagerank = [{}, {}]  # Two arrays, before update and after update
        prev = 0  # pagerank[prev] stores page ranks before update
        now  = 1  # pagerank[now] stores page ranks after update
        for id in self.links.keys():
            pagerank[prev][id] = 1

        while True:
            for id in self.links.keys():
                pagerank[now][id] = 0

            dist_random = 0  # Total page rank distributed randomly
            for id in self.links.keys():
                if self.links[id] == []:
                    dist_random += pagerank[prev][id] / num_of_pages
                    continue
                else:
                    dist_random += 0.15 * pagerank[prev][id] / num_of_pages

                dist_link = 0.85 * pagerank[prev][id] / len(self.links[id])  # Page rank distributed to linked nodes
                for link in self.links[id]:
                    pagerank[now][link] += dist_link
            
            variation = 0  # Difference between before and after update
            for id in self.links.keys():
                pagerank[now][id] += dist_random
                variation += abs(pagerank[now][id] - pagerank[prev][id])
            
            if variation < 1e-2:  # Convergence judgment
                break

            prev, now = now, prev  # Swap indexes
        
        sorted_pagerank = sorted(pagerank[prev].items(), key=lambda x: x[1], reverse=True)
        print("Page rank ranking")
        for rank in range(10):
            print("%d: %s" % (rank+1, self.titles[sorted_pagerank[rank][0]]))


    # Do something more interesting!!
    def find_something_more_interesting(self):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        pass


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # wikipedia.find_longest_titles()
    # wikipedia.find_most_linked_pages()
    # wikipedia.find_shortest_path("渋谷", "小野妹子")
    # wikipedia.find_shortest_path("ラ・カンパネラ", "VVVF")
    # wikipedia.find_shortest_path("B", "E")
    wikipedia.find_most_popular_pages()
