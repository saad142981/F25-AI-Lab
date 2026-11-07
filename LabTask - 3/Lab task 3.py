from collections import deque
import heapq
#task 1 and 2 
graph={"A":["B", "C"], "B": ["D", "E"], "C":["F"],"D":[],"E":["G"],"F":[],"G":[]}

def bfs(start, goal):
    q=deque([(start, [start])]); seen={start}
    while q:
        node, path=q.popleft()
        print("BFS:", node, path, list(q))
        if node==goal: return path
        for n in graph[node]:
            if n not in seen:
                seen.add(n); q.append((n, path+[n]))

def dfs(start, goal):
    stack=[(start, [start])]; seen=set()
    while stack:
        node, path=stack.pop()
        if node in seen: continue
        seen.add(node)
        print("DFS:", node, path, list(stack))
        if node==goal: return path
        for n in reversed(graph[node]):
            stack.append((n, path+[n]))

print(bfs("A", "G")); print(dfs("A", "G"))

#task 3 
def dls(start, goal, limit):
    stack=[(start, [start], 0)]; cutoff=False
    while stack:
        node, path, d=stack.pop()
        if node==goal: return ("FOUND", path)
        if d==limit:
            if graph[node]: cutoff=True
            continue
        for n in reversed(graph[node]):
            if n not in path:
                stack.append((n, path+[n], d+1))
    return ("CUTOFF", None) if cutoff else ("FAILURE", None)

def iddfs(start, goal, max_depth):
    for limit in range(max_depth+1):
        status, path=dls(start, goal, limit)
        if status!="CUTOFF": return (status, path, list(range(limit+1)))
    return ("CUTOFF", None, list(range(max_depth+1)))

for l in [1, 2, 3, 4]: print("DLS", l, dls("A", "G", l))
for m in [1, 2, 3, 4]: print("IDDFS", m, iddfs("A", "G", m))

weighted_graph={"A":[("B", 1), ("C", 2)], "B":[("D", 1), ("E", 1)], "C":[("F", 1), ("G", 10)], "D":[], "E":[("G", 1)], "F":[], "G":[]}

def ucs(start, goal):
    q=[(0, start, [start])]; seen=set(); order=[]
    while q:
        cost, node, path=heapq.heappop(q)
        if node in seen: continue
        seen.add(node); order.append((node, cost))
        if node==goal: return path, cost, order
        for n, w in weighted_graph[node]:
            if n not in seen:
                heapq.heappush(q, (cost+w, n, path+[n]))

graph={k:[n for n, _ in v] for k, v in weighted_graph.items()}
b_path=bfs("A", "G")
b_cost=sum(dict(weighted_graph[b_path[i]])[b_path[i+1]] for i in range(len(b_path)-1))
u_path, u_cost, u_order=ucs("A", "G")
u_ver=sum(dict(weighted_graph[u_path[i]])[u_path[i+1]] for i in range(len(u_path)-1))
print("Weighted BFS:", b_path, "Cost:", b_cost)
print("UCS:", u_path, "Cost:", u_cost, "Verified:", u_ver, "Order:", u_order)