# -*- coding: utf-8 -*-
import sqlite3
from graphviz import Digraph


def create_sql_query(query_term, limit=10):
    query_term = sorted(query_term)[:limit]
    sql_query = ''
    for i in query_term:
        if i == query_term[-1]:
            sql_query += 'id = ' + str(i)
        else:
            sql_query += 'id = ' + str(i) + ' OR '
    return sql_query


def list2str(raw_list, limit=10):
    tmp = ''
    count = 0
    for index in raw_list:
        count += 1
        if count == limit:
            tmp += str(index) + '...'
            break
        elif count % 10 == 0:
            tmp += str(index) + '\n'
        elif index == raw_list[-1]:
            tmp += str(index)
        else:
            tmp += str(index) + ', '
    if not tmp:
        tmp += 'None'
    return tmp


def do_query(sql_query):
    conn = sqlite3.connect('News.sqlite')
    cur = conn.cursor()
    return cur.execute("SELECT title FROM wiki WHERE " + sql_query)


def draw(slide_window, raw_query, query_list, raw_index, slide_index, dot, last_node, result):
    # dot = Digraph('G')
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

    for i in range(len_of_query_list):
        dot.edge(last + str(i + 1), 'last' + str(i + 1), color='green')

    sql_query = create_sql_query(result, 50)
    if result:
        title_list = []
        for title in do_query(sql_query):
            title_list.append(list(title)[0])
    result = list2str(sorted(title_list), 50)
    dot.node(result, shape='house')
    dot.edge(last_node, result, color='turquoise')

    dot.view()


if __name__ == '__main__':
    slide = 1

    aaa = '100, (可口+雪碧)&(黑松-七喜)|(OSX+android)&(steve#@20@#jobs+cook)|(臺積電-Systex#@20@#精誠)'
    bbb = '(apple)&(nvidia)&(cuda)|(顯示卡)&(amd)'