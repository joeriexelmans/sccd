# Tarjan's strongly connected components algorithm
# Taken from https://stackoverflow.com/a/6575693 and adopted to Python3

from itertools import chain
from collections import defaultdict
from typing import *

Edge = Tuple[Any,Any]

class _Graph:
    def __init__(self, edges: List[Edge]):
        edges = list(list(x) for x in edges)
        self.edges = edges
        self.vertices = set(chain(*edges))
        self.tails = defaultdict(list)
        for head, tail in self.edges:
            self.tails[head].append(tail)

def strongly_connected_components(edges: List[Edge]):
    graph = _Graph(edges)
    counter = 0
    count = dict()
    lowlink = dict()
    stack = []
    connected_components = []

    def strong_connect(head):
        nonlocal counter
        lowlink[head] = count[head] = counter = counter + 1
        stack.append(head)

        for tail in graph.tails[head]:
            if tail not in count:
                strong_connect(tail)
                lowlink[head] = min(lowlink[head], lowlink[tail])
            elif count[tail] < count[head]:
                if tail in stack:
                    lowlink[head] = min(lowlink[head], count[tail])

        if lowlink[head] == count[head]:
            component = []
            while stack and count[stack[-1]] >= count[head]:
                component.append(stack.pop())
            connected_components.append(component)

    for v in graph.vertices:
        if v not in count:
            strong_connect(v)

    return connected_components
