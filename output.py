import os
import sqlite3


def print_result(search_result):
    result = []

    # Because sqlite3 can accept only 1000 parameters, we fetch our result batch by batch
    # If batch_size is 900 and we have 4123 items, we have to run (4123 / 900) + 1 times
    batch_size = 900
    batch_num = int(len(search_result) / batch_size) + 1

    if len(search_result) != 0:
        conn = sqlite3.connect(os.path.join(os.getcwd(), 'News.sqlite'))
        for i in range(0, batch_num):
            cur = conn.cursor()
            sql = "SELECT id, url, title FROM wiki WHERE "
            for j in range(i * batch_size, i * batch_size + batch_size):
                if j >= len(search_result):
                    break
                if j == i * batch_size + batch_size - 1 or j == len(search_result) - 1:
                    sql += "id = " + str(search_result[j])
                else:
                    sql += "id = " + str(search_result[j]) + " OR "
            cur.execute(sql)
            data = cur.fetchall()
            for row in data:
                result.append([row[0], row[1], row[2]])
    for x in result:
        print(x)
    print("Found %d results" % len(search_result))