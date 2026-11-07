import heapq
def astar(graph, h, start, goal):
    pq=[(h[start], 0, start, [start])]; best={start:0}
    while pq:
        f, g, node, path=heapq.heappop(pq)
        if node==goal: return g, path
        if g!=best[node]: continue
        for nxt,w in graph.get(node, []):
            ng=g+w
            if ng<best.get(nxt,float("inf")):
                best[nxt]=ng
                heapq.heappush(pq, (ng+h[nxt], ng, nxt, path+[nxt]))

g={"S":[("A",1), ("B", 4)], "A": [("C",2)], "B": [("G",5)], "C":[("G",3)], "G":[]}
h={"S":5,"A": 4, "B": 4, "C": 2, "G":0}
print(astar(g,h, "S", "G"))

# Task 1, 2 & 3 updates
def trace(graph, h, start, goal):
    pq=[(h[start], 0, start, [start])]; best={start:0}; exp=[]
    while pq:
        f, g, node, path=heapq.heappop(pq)
        if node==goal:
            cost=sum(dict(graph[path[i]])[path[i+1]] for i in range(len(path)-1))
            return g, path, cost, exp, len(exp)
        if g!=best[node]: continue
        exp.append((node, g, h[node], f))
        for nxt,w in graph.get(node, []):
            ng=g+w
            if ng<best.get(nxt,float("inf")):
                best[nxt]=ng
                heapq.heappush(pq, (ng+h[nxt], ng, nxt, path+[nxt]))
        if len(exp)<=3: print("Exp", len(exp), (node, g, h[node], f), "Frontier:", list(pq))

print("A*:", trace(g, h, "S", "G"))
print("UCS:", trace(g, {k:0 for k in h}, "S", "G"))
h["C"]=10
print("Overestimate:", astar(g, h, "S", "G"), trace(g, h, "S", "G"))
