import sqlite3


def print_result(search_result):
    count = 0
    if len(search_result) != 0:
        conn = sqlite3.connect('News.sqlite')
        cur = conn.cursor()
        sql = "SELECT id, url, title FROM source WHERE "
        for index in search_result:
            if search_result[-1] == index:
                sql += "id = " + str(index)
            else:
                sql += "id = " + str(index) + " OR "
        cur.execute(sql)
        data = cur.fetchall()
        for row in data:
            count += 1
            print(row[0], row[1], row[2])
    print("Found %d results" %count)


def and_operation(list1, list2):
    return list(set(list1).intersection(list2))


def or_operation(list1, list2):
    return list(set(list1).union(list2))


def and_or(article_id_list, operator_list):
    article_id_stack = []
    operator_stack = []
    article_id_index = 0
    operator_index = 0
    while article_id_index < len(article_id_list):
        article_id_stack.append(article_id_list[article_id_index])
        if operator_index >= len(operator_list):
            break
        if len(operator_stack) == 0 or operator_stack[-1] == '|':
            operator_stack.append(operator_list[operator_index])
        else:
            cur_article_id1 = article_id_stack.pop()
            cur_article_id2 = article_id_stack.pop()
            cur_operator = operator_stack.pop()
            cur_result = and_operation(cur_article_id1, cur_article_id2)
            article_id_stack.append(cur_result)
            operator_stack.append(operator_list[operator_index])
        operator_index += 1
        article_id_index += 1


    while len(operator_stack) > 0:
        cur_article_id1 = article_id_stack.pop()
        cur_article_id2 = article_id_stack.pop()
        cur_operator = operator_stack.pop()
        if cur_operator == '|':
            result = or_operation(cur_article_id1, cur_article_id2)
        else:
            result = and_operation(cur_article_id1, cur_article_id2)
        article_id_stack.append(result)
    result_id = article_id_stack.pop()
    print_result(result_id)


if __name__ == '__main__':
    index_list = [[], [4,5,6], [7,8,9,30],[1,2,3],[5,6,7,8,9,1,0],[20,3,6,5,4,1],[0,1,2]]
    operator_list = ['&', '|','&','|','&','&']
    and_or(index_list, operator_list)