# -*- coding: utf-8 -*-
import sqlite3
from graphviz import Digraph


def create_sql_query(query_term):
    query_term = sorted(query_term)[:10]
    sql_query = ''
    for i in query_term:
        if i == query_term[-1]:
            sql_query += 'id = ' + str(i)
        else:
            sql_query += 'id = ' + str(i) + ' OR '
    return sql_query


def list2str(raw_list):
    tmp = ''
    count = 0
    for index in raw_list:
        count += 1
        if count == 10:
            tmp += str(index) + '...'
            break
        elif index == raw_list[-1]:
            tmp += str(index)
        else:
            tmp += str(index) + ', '

    return tmp


def do_query(sql_query):
    conn = sqlite3.connect('News.sqlite')
    cur = conn.cursor()
    return cur.execute("SELECT title FROM wiki WHERE " + sql_query)


def draw(slide_window, raw_query, query_list, raw_index, slide_index, rrr):

    dot = Digraph('G')
    # dot.attr(compound='true')
    # dot.graph_attr['rankdir'] = 'LR'
    dot.node_attr['shape'] = 'box3d'
    len_of_query_list = len(query_list)
    count = 0
    dot.node('0', raw_query)

    for i in range(len_of_query_list):
        count += 1
        if raw_index[i]:
            sql_query = create_sql_query(raw_index[i])
            title_list = []
            for title in do_query(sql_query):
                title_list.append(list(title)[0])

            dot.node('first' + str(count), query_list[i])
            dot.node('second' + str(count), list2str(title_list))
            dot.edge('0', 'first' + str(count))
            dot.edge('first' + str(count), 'second' + str(count))
        else:
            dot.node('first' + str(count), query_list[i])
            dot.node('second' + str(count), 'None')
            dot.edge('0', 'first' + str(count))
            dot.edge('first' + str(count), 'second' + str(count))

    if slide_window != -1:
        count = 0
        for i in range(len_of_query_list):
            count += 1
            if slide_index[i]:
                sql_query = create_sql_query(slide_index[i])
                title_list = []
                for title in do_query(sql_query):
                    title_list.append(list(title)[0])
                dot.node('third' + str(count), list2str(title_list))
                dot.edge('second' + str(count), 'third' + str(count))
            else:
                dot.node('third' + str(count), 'None')
                dot.edge('second' + str(count), 'third' + str(count))

    if slide_window != -1:
        last = 'third'
    else:
        last = 'second'
    print(dot)
    dot.view()


if __name__ == '__main__':
    slide = 1
    a = '100, (周杰倫#@30@#女友)|(男友#@30@#周杰倫)'
    b = ['周杰倫#@30@#女友', '男友#@30@#周杰倫', 'a', 'b', 'c', 'd']
    # c = [[1098743, 5076512], []]
    # d = [[1098743, 5076512], []]
    d = [[13]] * 6
    c = [[13], [18, 13, 21], [22, 25, 13, 39, 30], [1098743, 45, 13, 62], [13, 21, 22, 25, 39, 1098743, 70], [20, 62, 21, 13, 18, 1098743], [70, 1098743, 45]]
    e = [[1098743, 70, '&', [13]], [45, [13], '&', [13]], [62, [13], '&', [13]], [13, 18, '&', [1098743, 13, 21]], [21, [1098743, 13, 21], '&', [1098743]], [[1098743], [13], '|', [1098743, 13]], [1098743, 13]]
    draw(slide,a,b,c,d,e)