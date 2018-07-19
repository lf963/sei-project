import sqlite3
import datetime
import urllib.request
from bs4 import BeautifulSoup
import ssl
from langconv import *


def simple2tradition(line):
    line = Converter('zh-hant').convert(line)
    return line


context = ssl._create_unverified_context()

def getArticles(url):
    resp = urllib.request.urlopen(url, context=context, timeout=5).read().decode("utf-8")
    soup = BeautifulSoup(resp, "html.parser")
    listUrl = soup.findAll("p")
    text = ''
    for link in listUrl:
        text += link.get_text()

    while True:
        try:
            s = text.index('[')
            e = text.index(']')
            text = text[:s] + text[e + 1:]
        except:
            break

    return simple2tradition(text)


con = sqlite3.connect('News.sqlite')

cur = con.cursor()

while True:
    while True:
        try:
            slide_window = int(input('字數: '))
            break
        except:
            print('輸入錯誤，請重新輸入', end='')

    if slide_window == '':
        slide_window = -1
    query = input('請輸入搜查關鍵字: ')
    if query == '':
        print('Terminate.')
        break

    query_term = query.split('+')
    if slide_window == -1:
        positive = []
        negative = []
        for i in range(len(query_term)):
            if '-' in query_term[i]:
                query_term[i] = query_term[i].split('-')

        for i in query_term:
            if type(i) == str and len(i) > 0:
                positive.append(i)
            else:
                for j in range(len(i)):
                    if len(i[j]) == 0:
                        pass
                    elif j == 0:
                        positive.append(i[j])
                    else:
                        negative.append(i[j])

        query_term_pos = []
        query_term_neg = []
        wildcard_pos = []
        wildcard_neg = []
        for i in positive:
            if '#@' in i:
                start = i.index('#@')
                end = i.index('@#')
                query_term_pos.append(i[:start])
                query_term_pos.append(i[end + 2:])
                wildcard_pos.append([i[:start], i[end + 2:], int(i[start + 2:end])])

            else:
                query_term_pos.append(i)
        for i in negative:
            if '#@' in i:
                start = i.index('#@')
                end = i.index('@#')
                query_term_neg.append(i[:start])
                query_term_neg.append(i[end + 2:])
                wildcard_neg.append([i[:start], i[end + 2:], int(i[start + 2:end])])
            else:
                query_term_neg.append(i)

        start_ts = datetime.datetime.now()

        sql_query = ""
        for i in query_term_pos:
            if i == query_term_pos[-1]:
                sql_query += "text LIKE '%" + i + "%'"
            else:
                sql_query += "text LIKE '%" + i + "%' AND "
        result_pos = []
        if sql_query != '':
            raw_result = cur.execute("SELECT * FROM Source WHERE " + sql_query)

            if len(wildcard_pos) == 0:
                for i in raw_result:
                    result_pos.append(i)
            else:
                for i in raw_result:
                    check = True
                    for j in wildcard_pos:
                        tmp_check = False
                        for k in re.finditer(j[0], i[3]):
                            tmp_first_end = int(k.end())
                            for r in re.finditer(j[1], i[3]):
                                tmp_second_start = int(r.start())
                                if 1 <= (tmp_second_start - tmp_first_end) <= j[2]:
                                    tmp_check = True
                                    break
                            if tmp_check:
                                break
                        if not tmp_check:
                            check = False
                            break
                    if check:
                        result_pos.append(i)

        sql_query = ""
        for i in query_term_neg:
            if i == query_term_neg[-1]:
                sql_query += "text LIKE '%" + i + "%'"
            else:
                sql_query += "text LIKE '%" + i + "%' AND "
        result_neg = []
        if sql_query != '':
            raw_result = cur.execute("SELECT * FROM Source WHERE " + sql_query)

            if len(wildcard_neg) == 0:
                for i in raw_result:
                    result_neg.append(i)
            else:
                for i in raw_result:
                    check = False
                    for j in wildcard_neg:
                        for k in re.finditer(j[0], i[3]):
                            tmp_first_end = int(k.end())
                            for r in re.finditer(j[1], i[3]):
                                tmp_second_start = int(r.start())
                                if tmp_second_start - tmp_first_end - 1 <= j[2]:
                                    result_neg.append(i)
                                    check = True
                                    break
                            if check:
                                break

        spend_time = datetime.datetime.now() - start_ts
        index_pos = []
        index_neg = []
        for i in result_pos:
            index_pos.append(i[0])
        for i in result_neg:
            index_neg.append(i[0])

        #輸出
        result = set(index_pos) - set(index_neg)

        # for i in list(result):
        #   for j in cur.execute("SELECT * FROM Source WHERE ﻿id = \'" + str(i) + '\''):
        #       print(j[2], j[3])
        final_result = []
        counter = 0
        for i in result_pos:
            if i[0] in result:
                counter += 1
                print(counter, i[2])
                final_result.append([counter] + list(i))

        print('搜尋結果總共有', len(result), '篇, 搜尋花費時間', str(spend_time)[5:], '秒。')

        if len(final_result) > 0:
            while True:
                ask = input('想看那些原始文章(編號): ')

                if ask == '':
                    break
                else:
                    ask = ask.split()
                    for i in ask:
                        check = 0
                        for j in final_result:
                            if i == str(j[0]):
                                print(j[3] + '\n' + getArticles(j[2]))
                                check = 1
                                break
                        if check != 1:
                            print('沒有關鍵字: ' + i)
        else:
            print('沒有符合條件的結果。')
    else:
        glo_counter = 0
        final_result = []
        positive = []
        negative = []
        for i in range(len(query_term)):
            if '-' in query_term[i]:
                query_term[i] = query_term[i].split('-')

        for i in query_term:
            if type(i) == str and len(i) > 0:
                positive.append(i)
            else:
                for j in range(len(i)):
                    if len(i[j]) == 0:
                        pass
                    elif j == 0:
                        positive.append(i[j])
                    else:
                        negative.append(i[j])

        query_term_pos_2 = []
        query_term_pos = []
        query_term_neg = []
        query_term_neg_2 = []
        wildcard_pos = []
        wildcard_neg = []
        for i in positive:
            if '#@' in i:
                start = i.index('#@')
                end = i.index('@#')
                query_term_pos.append(i[:start])
                query_term_pos.append(i[end + 2:])
                wildcard_pos.append([i[:start], i[end + 2:], int(i[start + 2:end])])
            else:
                query_term_pos_2.append(i)
                query_term_pos.append(i)

        for i in negative:
            if '#@' in i:
                start = i.index('#@')
                end = i.index('@#')
                query_term_neg.append(i[:start])
                query_term_neg.append(i[end + 2:])
                wildcard_neg.append([i[:start], i[end + 2:], int(i[start + 2:end])])
            else:
                query_term_neg.append(i)
                query_term_neg_2.append(i)

        sql_query = ""
        for i in query_term_pos:
            if i == query_term_pos[-1]:
                sql_query += "text LIKE '%" + i + "%'"
            else:
                sql_query += "text LIKE '%" + i + "%' AND "
        result_pos = []
        if sql_query != '':
            raw_result = cur.execute("SELECT * FROM Source WHERE " + sql_query)

            if len(wildcard_pos) == 0:
                for i in raw_result:
                    result_pos.append(i)
            else:
                for i in raw_result:
                    check = True
                    for j in wildcard_pos:
                        tmp_check = False
                        for k in re.finditer(j[0], i[3]):
                            tmp_first_end = int(k.end())
                            for r in re.finditer(j[1], i[3]):
                                tmp_second_start = int(r.start())
                                if 1 <= (tmp_second_start - tmp_first_end) <= j[2]:
                                    tmp_check = True
                                    break
                            if tmp_check:
                                break
                        if not tmp_check:
                            check = False
                            break
                    if check:
                        result_pos.append(i)

        index_pos = []
        for i in result_pos:
            index_pos.append(i[0])
        # 輸出
        # print([slide_window, sorted(list(set(index_pos))), wildcard_pos, wildcard_neg])
        positive_query_pos = []
        for data in result_pos:
            positive_query_pos.append([data[0]])
            url = data[1]
            text = data[3]
            title = data[2]
            for query in query_term_pos_2:
                tmp = []
                positive_query_pos[-1].append([])
                for i in re.finditer(query, text):
                    tmp.append(i.start())
                positive_query_pos[-1][-1] = sorted(list(set(tmp)))
            for w_pos in wildcard_pos:
                tmp = []
                positive_query_pos[-1].append([])
                for i in re.finditer(w_pos[0], text):
                    for j in re.finditer(w_pos[1], text):
                        if 1 <= (int(j.start()) - int(i.end())) <= w_pos[2]:
                            tmp.append(int(i.start()))
                positive_query_pos[-1][-1] = sorted(list(set(tmp)))
            positive_query_pos[-1].append(title)
            positive_query_pos[-1].append(url)
            positive_query_pos[-1].append(text)

        for i in range(len(positive_query_pos)):
            tmp = []
            for j in range(len(positive_query_pos[i]) - 4, 1, -1):
                tmp_r = []
                tmp_k = []
                for r in positive_query_pos[i][j]:
                    check = False
                    for k in positive_query_pos[i][j - 1]:
                        if abs(r - k) <= slide_window:
                            tmp_r.append(r)
                            tmp_k.append(k)
                            check = True
                        elif check:
                            break
                positive_query_pos[i][j] = list(set(tmp_r))
                positive_query_pos[i][j - 1] = list(set(tmp_k))

        final_pos = []
        for i in positive_query_pos:
            check = True
            for j in i[1:]:
                if len(j) == 0:
                    check = False
                    break
            if check:
                final_pos.append(i)

        for i in final_pos:
            text = i[-1]
            neg = []
            if len(query_term_neg_2) > 0:
                for j in query_term_neg_2:
                    for k in re.finditer(j, text):
                        neg.append(int(k.start()))
            if len(wildcard_neg) > 0:
                for w_neg in wildcard_neg:
                    for k in re.finditer(w_neg[0], text):
                        for j in re.finditer(w_neg[1], text):
                            if 1 <= (int(j.start()) - int(k.end())) <= w_neg[2]:
                                neg.append(int(k.start()))

            tmp = []
            for r in range(len(i) - 4, 0, -1):
                tmp.append(i[r])

            restrict = []
            for n in neg:
                if n - 100 < 0:
                    for res in range(0, n + 101):
                        restrict.append(res)
                else:
                    for res in range(n - 100, n + 101):
                        restrict.append(res)

            restrict = list(set(restrict))
            counter = -1
            path = []
            for r in tmp:
                counter += 1
                path.append([])
                for k in r:
                    if k not in restrict:
                        path[counter].append(k)

            check = True
            for j in path:
                if not j:
                    check = False
                    break

            if check:
                final_result.append(i[-2])
                glo_counter += 1
                print(glo_counter, i[-3])
                # print(neg)
                # print(path)

        if len(final_result) > 0:
            while True:
                ask = input('想看那些原始文章(編號): ')

                if ask == '':
                    break
                else:
                    ask = ask.split()
                    for i in ask:
                        if int(i) > len(final_result):
                            print('編號錯誤，請重新輸入。')
                            break
                        print(getArticles(final_result[int(i) - 1]))
        else:
            print('沒有符合條件的結果。')