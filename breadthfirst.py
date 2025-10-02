"""Breadth-first search (BFS) solver.

Emits visualization events (frontier and visit) when visualization is enabled
at the top-level. Calls are no-ops otherwise.
"""
from collections import deque
import visualize

def solve(maze):
    start = maze.start
    end = maze.end

    width = maze.width

    queue = deque([start])
    shape = (maze.height, maze.width)
    prev = [None] * (maze.width * maze.height)
    visited = [False] * (maze.width * maze.height)

    count = 0

    completed = False

    visited[start.Position[0] * width + start.Position[1]] = True
    visualize.frontier(start.Position)

    while queue:
        count += 1
        current = queue.pop()
        visualize.visit(current.Position)

        if current == end:
            completed = True
            break

        for n in current.Neighbours:
            if n != None:
                npos = n.Position[0] * width + n.Position[1]
                if visited[npos] == False:
                    queue.appendleft(n)
                    visited[npos] = True
                    prev[npos] = current
                    visualize.frontier(n.Position)

    path = deque()
    current = end
    while (current != None):
        path.appendleft(current)
        current = prev[current.Position[0] * width + current.Position[1]]

    return [path, [count, len(path), completed]]
