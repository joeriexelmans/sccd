import functools
import itertools

# A generic depth-first tree-visit function that can let multiple visitor functions do "their thing" in only a single pass.
# It accepts 2 lists of visitor functions:
# 'parent_first' is a list of callbacks that will be called with 1 or 2 parameters (and therefore the 2nd parameter of the callback should have a default value): 1) the current element and 2) the value of the callback returned by the parent element if the current element is not the root element.
# 'child_first' is a list of callbacks that will be called with 2 parameters: 2) the current element and 2) An empty list for all the leaf elements or a list with the responses of the children of that element for the callback.
def visit_tree(node, get_children, parent_first=[], child_first=[], parent_values=None):
    # Most parameters unchanged for recursive calls
    def visit(node, parent_values):
        if parent_values is None:
            parent_values = [f(node) for f in parent_first]
        else:
            parent_values = [f(node, p) for f,p in zip(parent_first, parent_values)]

        # child_responses is a list of len(children)-many lists C, where for every child of node, C is the 'to_parent' value returned by every child
        child_responses = [visit(node=c, parent_values=parent_values) for c in get_children(node)]

        to_parent = [f(node, [cs[i] for cs in child_responses]) for i,f in enumerate(child_first)]
        # 'to_parent' is the mapping from our child_first-functions to those functions called on the responses we got from our children

        return to_parent

    return visit(node, parent_values)
