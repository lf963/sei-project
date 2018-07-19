import sqlite3


def print_result(search_result):
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
        print(row[0], row[1], row[2])


def and_or(index_list, operator_list):
    result = set(index_list[0])
    for i in range(1, len(index_list)):
        if operator_list[i-1] == '|':
            result = result.union(index_list[i])
        else:
            result = result.intersection(index_list[i])
    print_result(list(result))


if __name__ == '__main__':
    index_list = [[13,18,20,25,6205710], [27,33,50,6205710], [13,14,15,16,17,18,19,20,6205710]]
    operator_list = ['|', '&']
    and_or(index_list, operator_list)