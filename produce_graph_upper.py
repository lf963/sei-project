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


def list2str(raw_list, limit=10, length=2):
    tmp = ''
    count = 0
    for index in raw_list:
        count += 1
        if count == limit:
            tmp += str(index) + '...'
            break
        elif count % (10 // length * 2) == 0:
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
    dot.graph_attr['bgcolor'] = '#f0f0f0'
    dot.graph_attr['label'] = 'RESULT!!!'
    dot.graph_attr['labelloc'] = 't'
    dot.graph_attr['fontsize'] = '40'
    dot.graph_attr['labeljust'] = 'l'
    dot.graph_attr['fontcolor'] = 'red'
    dot.node_attr['shape'] = 'note'
    # dot.node_attr['shape'] = 'record'
    len_of_query_list = len(query_list)
    count = 0
    dot.node('0', raw_query, shape='folder')
    for i in range(len_of_query_list):
        count += 1
        if raw_index[i]:
            sql_query = create_sql_query(raw_index[i])
            title_list = []
            for title in do_query(sql_query):
                title_list.append(list(title)[0])
            
            dot.node('first' + str(count), query_list[i], shape='tab')
            dot.node('second' + str(count), list2str(title_list, 10, len_of_query_list))
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
                dot.node('third' + str(count), list2str(title_list, 10, len_of_query_list))
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
    print(result)
    sql_query = create_sql_query(result, 50)

    title_list = []
    if result:
        for title in do_query(sql_query):
            title_list.append(list(title)[0])
    result_1 = list2str(sorted(title_list), 50)
    dot.node(result_1, result_1 + '\n總計結果: ' + str(len(result)) + '篇。', shape='box3d', fontcolor='red', fontsize='20')
    dot.edge(last_node, result_1, color='turquoise')
    dot.graph_attr['dpi'] = '300'

    dot.view()


if __name__ == '__main__':
    slide = 1

    aaa = '100, (可口+雪碧)&(黑松-七喜)|(OSX+android)&(steve#@20@#jobs+cook)|(臺積電-Systex#@20@#精誠)'
    bbb = '(apple)&(nvidia)&(cuda)|(顯示卡)&(amd)'
