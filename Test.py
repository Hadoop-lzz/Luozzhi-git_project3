import urllib.request
from bs4 import BeautifulSoup
import pymysql.cursors

start = 0
for i in range(1,11):
    # 连接数据库
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='258073',
                                 database='spider_douban',
                                 cursorclass=pymysql.cursors.DictCursor
                                 )
    # 创建一个Request(等于一个url)，Request需要放hearders
    h = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(f"https://movie.douban.com/top250?start={start}&filter=", headers=h)

    # 参数可以是一个url地址，也可以是一个Request
    r = urllib.request.urlopen(req)
    # print(r.status)
    # print(r.read().decode())
    html_doc = r.read().decode()

    # 使用bs4或是re正则表达式进行数据提取
    soup = BeautifulSoup(html_doc, 'html.parser')
    items = soup.find_all("div", class_='item')  # find_all 寻找所有标签，按css搜索：class_=''
    # print(items)
    with connection:
        for item in items:
            img = item.find("div", class_="pic").a.img  # 寻找img标签
            name = img['alt']     #
            url = img['src']

            hd = item.find("div", class_="hd")
            English = hd.find_all("span")
            Englishname = English[1].text   #英文名称
            Othername = hd.find("span", class_="other").text   #台式名称

            bd = item.find("div", class_="bd")
            director = item.find("div", class_="bd").p.text  #导演，演员简介
            # text = re.split("\n+",director0)
            # director = re.split("\b",text).group(1)


            star = bd.find("div", class_="star")
            level = star.find("span", class_="rating_num").text  #豆瓣评分
            comments = star.find_all("span")
            comment = comments[3].text        #评价人数
            label = bd.find("span", class_="inq")     #标签
            # 处理my_object为None的情况
            if label is not None:
                label = bd.find("span", class_="inq").text
            else:
                label = bd.find("span", class_="inq")

            # print("="*50)  #分隔符
            # 把提取出来的数据存储到MySQL
            with connection.cursor() as cursor:
                    sql = "INSERT IGNORE `movie_info` (`movie_name`,`movie_url`,`englishname`,`othername`,`director`,`level`,`comment`,`label`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.executemany(sql, (name, url, Englishname, Othername, director, level, comment, label))
        connection.commit()

    start = start + 25    #更新


