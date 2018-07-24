# -*- coding: utf-8 -*-
import re
import sqlite3
import datetime
import urllib.request
from bs4 import BeautifulSoup
import ssl
from langconv import *



def simple2tradition(line):
    line = Converter('zh-hant').convert(line)
    return line


#crawling text from web
def getArticles(url):
    resp = urllib.request.urlopen(url, context=ssl._create_unverified_context(), timeout=5).read().decode("utf-8")
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


#split the raw query text into positive and negative terms
def split_pos_neg(query_term):
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
    return positive, negative


#realizing the wildcard's, [start word, last word, tolerable word number]
#extension: 1(returning an additional item<query_term_2>
def get_wildcard(raw_query, extension=0):
    query_term = []
    query_term_2 = []
    wildcard = []
    for i in raw_query:
        if '#@' in i:
            start = i.index('#@')
            end = i.index('@#')
            query_term.append(i[:start])
            query_term.append(i[end + 2:])
            wildcard.append([i[:start], i[end + 2:], int(i[start + 2:end])])
        else:
            query_term_2.append(i)
            query_term.append(i)

    if extension:
        return query_term, query_term_2, wildcard
    else:
        return query_term, wildcard


def create_sql_query(query_term):
    sql_query = ""
    for i in query_term:
        if i == query_term[-1]:
            sql_query += "text LIKE '%" + i.replace("'", "''").lower() + "%'"
        else:
            sql_query += "text LIKE '%" + i.replace("'", "''").lower() + "%' AND "
    return sql_query


#get the result which is/are the index(es) that those articles who satisfies the query condition
def get_result(sql_query, cursor, wildcard):
    result = []
    if sql_query != '':
        raw_result = cursor.execute('SELECT * FROM wiki WHERE ' + sql_query)

        if len(wildcard) == 0:
            for i in raw_result:
                result.append(i)
        else:
            for i in raw_result:
                check = True
                for j in wildcard:
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
                    result.append(i)
    return result


def step_1(slide_window, query_list):
    slide_window = int(slide_window)
    final_output = []

    con = sqlite3.connect('News.sqlite')

    cur = con.cursor()
    start_ts = datetime.datetime.now()
    for query in query_list:
        query_term = query.split('+')
        if slide_window == -1:
            positive, negative = split_pos_neg(query_term)

            query_term_pos, wildcard_pos = get_wildcard(positive)
            query_term_neg, wildcard_neg = get_wildcard(negative)

            sql_query_pos = create_sql_query(query_term_pos)
            sql_query_neg = create_sql_query(query_term_neg)

            result_pos = get_result(sql_query_pos, cur, wildcard_pos)
            result_neg = get_result(sql_query_neg, cur, wildcard_neg)

            index_pos = []
            index_neg = []
            for index in result_pos:
                index_pos.append(index[0])
            for i in result_neg:
                index_neg.append(index[0])

            result = set(index_pos) - set(index_neg)
            final_output.append(list(result))
            spend_time = datetime.datetime.now() - start_ts

            # for i in list(result):
            #     for j in cur.execute("SELECT * FROM wiki WHERE ﻿id = \'" + str(i) + '\''):
            #         print(j[2], j[3])
            # final_result = []
            # counter = 0
            # for i in result_pos:
            #     if i[0] in result:
            #         counter += 1
            #         print(counter, i[2])
            #         final_result.append([counter] + list(i))
            #
            # print('搜尋結果總共有', len(result), '篇, 搜尋花費時間', str(spend_time)[5:], '秒。')
            #
            # if len(final_result) > 0:
            #     while True:
            #         ask = input('想看那些原始文章(編號): ')
            #
            #         if ask == '':
            #             break
            #         else:
            #             ask = ask.split()
            #             for i in ask:
            #                 check = 0
            #                 for j in final_result:
            #                     if i == str(j[0]):
            #                         print(j[3] + '\n' + getArticles(j[2]))
            #                         check = 1
            #                         break
            #                 if check != 1:
            #                     print('沒有關鍵字: ' + i)
            # else:
            #     print('沒有符合條件的結果。')
        else:
            glo_counter = 0
            final_result = []
            positive, negative = split_pos_neg(query_term)

            query_term_pos, query_term_pos_2, wildcard_pos = get_wildcard(positive, 1)
            query_term_neg, query_term_neg_2, wildcard_neg = get_wildcard(negative, 1)

            sql_query = create_sql_query(query_term_pos)
            result_pos = get_result(sql_query, cur, wildcard_pos)

            index_pos = []
            for index in result_pos:
                index_pos.append(index[0])

            final_output.append([slide_window, sorted(list(set(index_pos))), wildcard_pos+query_term_pos_2, wildcard_neg+query_term_neg_2])
            spend_time = datetime.datetime.now() - start_ts

            # positive_query_pos = []
            # for data in result_pos:
            #     positive_query_pos.append([data[0]])
            #     url = data[1]
            #     text = data[3]
            #     title = data[2]
            #     for query in query_term_pos_2:
            #         tmp = []
            #         positive_query_pos[-1].append([])
            #         for i in re.finditer(query, text):
            #             tmp.append(i.start())
            #         positive_query_pos[-1][-1] = sorted(list(set(tmp)))
            #     for w_pos in wildcard_pos:
            #         tmp = []
            #         positive_query_pos[-1].append([])
            #         for i in re.finditer(w_pos[0], text):
            #             for j in re.finditer(w_pos[1], text):
            #                 if 1 <= (int(j.start()) - int(i.end())) <= w_pos[2]:
            #                     tmp.append(int(i.start()))
            #         positive_query_pos[-1][-1] = sorted(list(set(tmp)))
            #     positive_query_pos[-1].append(title)
            #     positive_query_pos[-1].append(url)
            #     positive_query_pos[-1].append(text)
            #
            # for i in range(len(positive_query_pos)):
            #     for j in range(len(positive_query_pos[i]) - 4, 1, -1):
            #         tmp_r = []
            #         tmp_k = []
            #         for r in positive_query_pos[i][j]:
            #             check = False
            #             for k in positive_query_pos[i][j - 1]:
            #                 if abs(r - k) <= int(slide_window):
            #                     tmp_r.append(r)
            #                     tmp_k.append(k)
            #                     check = True
            #                 elif check:
            #                     break
            #         positive_query_pos[i][j] = list(set(tmp_r))
            #         positive_query_pos[i][j - 1] = list(set(tmp_k))
            #
            # final_pos = []
            # for i in positive_query_pos:
            #     check = True
            #     for j in i[1:]:
            #         if len(j) == 0:
            #             check = False
            #             break
            #     if check:
            #         final_pos.append(i)
            #
            # for i in final_pos:
            #     text = i[-1]
            #     neg = []
            #     if len(query_term_neg_2) > 0:
            #         for j in query_term_neg_2:
            #             for k in re.finditer(j, text):
            #                 neg.append(int(k.start()))
            #     if len(wildcard_neg) > 0:
            #         for w_neg in wildcard_neg:
            #             for k in re.finditer(w_neg[0], text):
            #                 for j in re.finditer(w_neg[1], text):
            #                     if 1 <= (int(j.start()) - int(k.end())) <= w_neg[2]:
            #                         neg.append(int(k.start()))
            #
            #     tmp = []
            #     for r in range(len(i) - 4, 0, -1):
            #         tmp.append(i[r])
            #
            #     restrict = []
            #     for n in neg:
            #         if n - 100 < 0:
            #             for res in range(0, n + slide_window + 1):
            #                 restrict.append(res)
            #         else:
            #             for res in range(n - slide_window, n + slide_window + 1):
            #                 restrict.append(res)
            #
            #     restrict = list(set(restrict))
            #     counter = -1
            #     path = []
            #     for r in tmp:
            #         counter += 1
            #         path.append([])
            #         for k in r:
            #             if k not in restrict:
            #                 path[counter].append(k)
            #
            #     check = True
            #     for j in path:
            #         if not j:
            #             check = False
            #             break
            #
            #     if check:
            #         final_result.append(i[-2][i[-2].index('=') + 1:])
            #         glo_counter += 1
            #         #print(glo_counter, i[-3])
            #         # print(neg)
            #         # print(path)
            # print(final_result)

            # if len(final_result) > 0:
            #     while True:
            #         ask = input('想看那些原始文章(編號): ')
            #
            #         if ask == '':
            #             break
            #         else:
            #             ask = ask.split()
            #             for i in ask:
            #                 if int(i) > len(final_result):
            #                     print('編號錯誤，請重新輸入。')
            #                     break
            #                 print(getArticles(final_result[int(i) - 1]))
            # else:
            #     print('沒有符合條件的結果。')
    print('done')
    print(spend_time)

    return final_output


if __name__ == '__main__':
    slide = 30
    query_input = ['職業+游擊手', '陳#@1@#鋒-富邦#@10@#球隊+棒球-臺北', '銀行+公司#@30@#董事長-元大-新光', '筆記型電腦+顯示卡', '很大的房子-很慢的車子', '臺積電']

    print(step_1(slide, query_input))