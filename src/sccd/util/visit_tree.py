import functools
import itertools

# A generic depth-first tree-visit function that can let multiple visitor functions do their thing in only a single pass.
# It accepts 2 lists of visitor functions:
# 'before_children' is a list of callbacks that will be called with 1 or 2 parameters (and therefore the 2nd parameter of the callback should have a default value): 1) the current element and 2) the value of the callback returned by the parent element if the current element is not the root element.
# 'after_children' is a list of callbacks that will be called with 2 parameters: 2) the current element and 2) An empty list for all the leaf elements or a list with the responses of the children of that element for the callback.
def visit_tree(node, get_children, before_children=[], after_children=[], parent_values=None):
    # Most parameters unchanged for recursive calls
    visit = functools.partial(visit_tree, get_children=get_children, before_children=before_children, after_children=after_children)

    if parent_values is None:
        parent_values = [f(node) for f in before_children]
    else:
        parent_values = [f(node, p) for f,p in zip(before_children, parent_values)]


    child_responses = (visit(node=c, parent_values=parent_values) for c in get_children(node))
    # child_responses is a list of len(children)-many lists C, where for every child of node, C is the 'to_parent' value returned by every child

    to_parent = [f(node, [cs[i] for cs in child_responses]) for i,f in enumerate(after_children)]
    # 'to_parent' is the mapping from our after_children-functions to those functions called on the responses we got from our children

    return to_parent


# def visit_tree2(node, get_children, before_child=[], after_child=[], parent_values=None):
#     # Most parameters unchanged for recursive calls
#     visit = functools.partial(visit_tree2, get_children=get_children, before_child=before_child, after_child=after_child)

#     if parent_values is None:
#         parent_values = [before_f(node) for before_f in before_child]
#     else:
#         parent_values = [before_f(node, p) for before_f,p in zip(before_child, parent_values)]

#     children_responses = [visit(node=c, parent_values=parent_values) for c in get_children(node)]
#     children_responses2 = [list(itertools.chain.from_iterable(cr[i] for cr in children_responses)) for i,after_f in enumerate(after_child)]

#     to_parent = []
#     for after_f, res in zip(after_child, children_responses2):
#         ls = []
#         after_f(node, res, ls)
#         to_parent.append(ls)

#     print("visit_tree2, node=",node,"children_responses:",children_responses2)
#     print("to parent:", to_parent)

#     return to_parent