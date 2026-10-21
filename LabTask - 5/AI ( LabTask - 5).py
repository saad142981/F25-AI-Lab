
import math
minimax_counter = 0

def minimax(curDepth, nodeIndex, maxTurn, scores, targetDepth):
 global minimax_counter

 if curDepth == targetDepth:
     minimax_counter += 1
     return scores[nodeIndex]
 
 if maxTurn:
    return max(
            minimax(curDepth + 1, nodeIndex * 2, False, scores, targetDepth),
            minimax(curDepth + 1, nodeIndex * 2 + 1, False, scores, targetDepth)
)
 else:
    return min(
        minimax(curDepth + 1, nodeIndex * 2, True, scores, targetDepth),
        minimax(curDepth + 1, nodeIndex * 2 + 1, True, scores, targetDepth)
)
 







alpha_beta_counter = 0

def alphabeta(depth, index, maxTurn, scores, target, alpha, beta):
    global alpha_beta_counter
   
    if depth == target:
        alpha_beta_counter += 1
        return scores[index]
    
    if maxTurn:
        value = float('-inf')
        for i in range(2):
            value = max(value, alphabeta(depth+1, index*2+i, False, scores, target, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        for i in range(2):
            value = min(value, alphabeta(depth+1, index*2+i, True, scores, target, alpha, beta))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

scores = {
    "original_order": [3, 5, 2, 9, 3, 5, 2, 9],
    "reordered_1": [5, 3, 9, 2, 5, 3, 9, 2],
    "reordered_2": [2, 9, 3, 5, 2, 9, 3, 5]
}

for i in scores:
    alpha_beta_counter = 0  
    minimax_counter = 0

    depth = int(math.log2(len(scores[i])))

    print("The optimal value for alpha-beta pruning", i , end=" = ")
    print(alphabeta(0, 0, True, scores[i], depth, float('-inf'), float('inf')))
    print("Number of evaluated leafs = ", alpha_beta_counter)


    print("The optimal value for minimax", i , end=" = ")
    print(minimax(0, 0, True, scores[i], depth))

    print("Number of evaluated leafs = ",minimax_counter)
    print("  ")
   









