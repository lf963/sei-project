# please refer to https://github.com/yichen0831/opencc-python
import csv
from opencc import OpenCC
import os
import re
import sqlite3


openCC = OpenCC()
openCC.set_conversion('s2twp') # Simplified Chinese to Traditional Chinese (Taiwan standard, with phrases)

article_start_pattern = "<doc id="
article_id_pattern = re.compile("<doc id=\"(.+)\" url")
article_url_pattern = re.compile("url=\"(.+)\" title")
article_title_pattern = re.compile("title=\"(.+)\">")
article_text_pattern = re.compile("<doc id=\"(.+)\" url")

db_path = os.path.join(os.getcwd(), 'articles', 'wiki.db')
csv_path = os.path.join(os.getcwd(), 'articles', '_wiki.csv')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

sql = "DELETE FROM Source"
cur.execute(sql)
conn.commit()

for item in range(0, 2):
    if item == 0:
        file_path = os.path.join(os.getcwd(), 'articles', 'wiki_00')
    else:
        file_path = os.path.join(os.getcwd(), 'articles', 'wiki_01')
    i = 0
    article_id = ""
    article_url = ""
    article_title = ""
    article_text = ""

    with open(file_path, 'r', encoding='utf-8') as infile:
        with open(csv_path,  'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for line in infile:
                # if i > 100:
                #     break
                if line == '\n':
                    continue
                elif line == "</doc>\n":
                    print(int(article_id), article_url, article_title)
                    # cur.execute("INSERT INTO source VALUES(?,?,?,?)",
                    #            (int(article_id), article_url, article_title, article_text))
                    # conn.commit()
                    #print(article_text)
                    #writer.writerow([int(article_id), article_url, article_title, article_text])
                    article_text = ""
                    continue
                tw_line = re.sub("\n", '', openCC.convert(line))
                if re.match(article_start_pattern, line):

                    article_id = article_id_pattern.findall(tw_line)[0]
                    article_url = article_url_pattern.findall(tw_line)[0]
                    article_title = article_title_pattern.findall(tw_line)[0]
                else:
                    article_text += tw_line
                    #article_text += re.sub(chinese_pattern, "", tw_line)

                i += 1

