from enum import Enum
from graphviz import Digraph
import output
import produce_graph_upper


# This is for edges in graph
class OperationColor(Enum):
    OR = 'blue'
    AND = 'red'


# id_list: article's id, ex:[1,3,5,7]
# index: add an index to each IdNode to prevent two same id_list from being considered as one single node
# ex: [1,3,5,7] & [2,3,4] | [1,3,5,7] | [10,20,30]
# two [1,3,5,7] should be considered as two different nodes in graph
# so we use IdNode([1,3,5,7], 1) and IdNode([1,3,5,7],3) to differentiate them
# in which 1 and 3 are the position of [1,3,5,7]
class IdNode():
    def __init__(self, id_list, index):
        self.id_list = id_list
        self.index = index


def and_or_operation(list1, list2, and_or_operator):
    if and_or_operator == '&':
        return list(set(list1).intersection(list2))
    else:
        return list(set(list1).union(list2))


# convert list to string
def list2str(id_list):
    s = ""
    for id in id_list:
        s += str(id)
        if id != id_list[-1]:
            s += ","
    return s


def and_operation(list1, list2):
    return list(set(list1).intersection(list2))


def or_operation(list1, list2):
    return list(set(list1).union(list2))


def and_or(article_id_list, operator_list):
    dot = Digraph('G')

    # set font as 新細明體(PmingLiu)
    # without setting this, windows cannot print Chinese
    dot.node_attr['fontname'] = "PmingLiu"

    article_id_stack = []
    operator_stack = []
    article_id_index = 0
    operator_index = 0

    # If a node is at the top level of a graph, we use its position in article_id_list as its index
    # If a node is not at the top level of a graph, we use negative number, node_index, as its index
    node_index = -1
    node_prefix = 'last'

    with dot.subgraph(name = 'flow_chart1') as s:
        s.attr(rank='same')

        while article_id_index < len(article_id_list):
            cur_article_id_str = produce_graph_upper.list2str(article_id_list[article_id_index], 10,
                                                              len(article_id_list))
            article_id_stack.append(IdNode(article_id_list[article_id_index], article_id_index + 1))

            # Create a node,
            s.node(node_prefix + str(article_id_index + 1), cur_article_id_str)

            if operator_index >= len(operator_list):
                break
            if len(operator_stack) == 0 or operator_stack[-1] == '|':
                operator_stack.append(operator_list[operator_index])
            else:
                cur_article_node1 = article_id_stack.pop()
                cur_article_node2 = article_id_stack.pop()
                cur_operator = operator_stack.pop()

                cur_result = and_or_operation(cur_article_node1.id_list, cur_article_node2.id_list, cur_operator)

                article_id_stack.append(IdNode(cur_result, node_index))

                # Create a node
                dot.node(node_prefix + str(node_index),
                         produce_graph_upper.list2str(sorted(cur_result), 10, len(article_id_list)))

                # Connect node
                dot.edge(node_prefix + str(cur_article_node1.index), node_prefix + str(node_index),
                         color=OperationColor.AND.value)
                dot.edge(node_prefix + str(cur_article_node2.index), node_prefix + str(node_index),
                         color=OperationColor.AND.value)

                # After generating a new node, decrease node_index by one
                node_index -= 1

                operator_stack.append(operator_list[operator_index])
            operator_index += 1
            article_id_index += 1

        while len(operator_stack) > 0:
            cur_article_node1 = article_id_stack.pop()
            cur_article_node2 = article_id_stack.pop()
            cur_operator = operator_stack.pop()

            result = and_or_operation(cur_article_node1.id_list, cur_article_node2.id_list, cur_operator)
            article_id_stack.append(IdNode(result, node_index))
            # Create a node
            dot.node(node_prefix + str(node_index),
                     produce_graph_upper.list2str(sorted(result), 10, len(article_id_list)))
            dot.edge(node_prefix + str(cur_article_node1.index), node_prefix + str(node_index),
                     color=OperationColor.OR.value if cur_operator == '|' else OperationColor.AND.value)
            dot.edge(node_prefix + str(cur_article_node2.index), node_prefix + str(node_index),
                     color=OperationColor.OR.value if cur_operator == '|' else OperationColor.AND.value)

            # After generating a new node, increase node_index by one
            node_index -= 1
    result_id = article_id_stack.pop()

    output.print_result(result_id.id_list)

    with dot.subgraph(name='cluster_legend') as c:
        c.graph_attr['label'] = "Legend"
        c.node_attr['shape'] = "plaintext"
        c.node("dummy_node_1","")
        c.node("dummy_node_2", "")
        c.edge('dummy_node_1', 'AND', color=OperationColor.AND.value)
        c.edge('dummy_node_2', 'OR', color=OperationColor.OR.value)

    with dot.subgraph(name='cluster_dummy') as c:
        c.graph_attr['style'] = 'invis'
        c.node_attr['style'] = 'invis'
        c.node("dummy_node_3", "")
    dot.edge("dummy_node_3", "dummy_node_1",ltail="cluster_dummy", lhead="cluster_legend", style="invis")

    # print(dot)
    # dot.view()

    # dot: the graph
    # node_prefix + str(node_index + 1 if node_index != -1 else 1): the name of the last node
    # if we have only one node, the name of that node is node_prefix + str(1)
    return dot, node_prefix + str(node_index + 1 if node_index != -1 else 1), result_id.id_list


if __name__ == '__main__':
    index_list = [[1, 2, 3],[4,5,6],[1,2,3,4,5,6,7,8],[2,4,6,8,10]]
    operator_list = ['&','|','&']
    and_or(index_list, operator_list)