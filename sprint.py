import os
import requests
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
import datetime


class Sprint():

    def __init__(self, day=1, file='', link=''):

        self.day = day
        self.file = file
        self.link = link
        self.ruta = '/home/sprintOct21/sprint'
        self.conn = self.create_database(f'{self.ruta}/sprint.db');
        self.create_tables()
        self.data = ''
        self.file_name = 'file.txt'

    def main(self):

        if self.file != '':
            self.read_file()
        elif self.link != '':
            self.get_page()

        if self.data != '':
            self.soup = BeautifulSoup(self.data, "html.parser")
            self.get_likes()
            #self.get_comments()

    def get_page(self):
        l = self.link.strip()
        proxyDict = { "http": "socks5h://localhost:3128", "https": "socks5h://localhost:3128", }
        page = requests.get(l, proxies=proxyDict)
        print(l, self.file_name)

        with open(f'{self.ruta}/posts/{self.file_name}', 'bw') as file:
            #file.write(l)
            file.write(page.content)
        self.data = page.content

    def read_file(self):
        f = open(f'{self.ruta}/posts/{self.file}');
        self.data = f.read()
        self.link = self.data.splitlines()[0]

    def get_likes(self):
        self.link = self.soup.find("meta", property="og:url")["content"]
        self.owner = self.soup.find('a', class_ = 'share-update-card__actor-text-link').text.strip()
        self.num_likes = self.soup.find('span', class_ = 'social-counts-reactions__social-counts-numRections').text.strip()
        #num_comments = self.soup.find_all('a', { 'class':'social-action-counts__social-counts-item'})
        self.num_comments = self.soup.select('a[class="social-action-counts__social-counts-item"]')[0].text.strip().split()[0]
        print(self.link, self.num_likes, self.num_comments)
        self.id_post = self.insert_tarea()

        #likes = [r.text.strip() for r in num_likes]
        #comms = [r.text.strip() for r in num_comments]
        #links = [r.attrs['href'] for r in num_comments]

    def insert_tarea(self):
        x = datetime.datetime.now()
        curtime = x.strftime("%Y-%m-%d %X")

        sql = 'REPLACE INTO posts (day, owner, link, start_date, update_date, num_comments, num_likes) VALUES(?,?,?,?,?,?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, (self.day, self.owner, self.link, curtime, curtime, self.num_comments, self.num_likes))
        self.conn.commit()
        return cur.lastrowid

    def get_comments(self):

        comments = self.soup.find_all('section', class_ = 'comment')
        print(len(comments))

        print('***************************************************************************')
        print('*******************************MESSAGES************************************')
        for c in comments:
            self.author = c.find('a', class_ = 'comment__actor-name').text.strip()
            self.message = c.find('span', class_ = 'comment__message').text.strip()
            print(self.author, ':',  self.message)
            self.insert_comments()

        print('***************************************************************************')

    def insert_comments(self):

        sql = 'INSERT INTO comments(id_post, author, message) VALUES(?,?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, (self.id_post, self.author, self.message))
        self.conn.commit()
        return cur.lastrowid

    def create_database(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        return conn


    def create_tables(self):
        table_posts = """CREATE TABLE IF NOT EXISTS posts(
                        id integer PRIMARY KEY,
                        day integer NOT NULL,
                        owner TEXT NULL,
                        link TEXT NOT NULL UNIQUE,
                        start_date TEXT NOT NULL,
                        update_date TEXT NULL,
                        num_comments INTEGER NULL,
                        num_likes INTEGER NULL);
                      """
        table_comments = """CREATE TABLE IF NOT EXISTS comments(
                        id integer PRIMARY KEY,
                        id_post integer NOT NULL,
                        author TEXT NOT NULL,
                        message TEXT NOT NULL);
                      """

        table_sprinters = """CREATE TABLE IF NOT EXISTS sprinters(
                        id integer PRIMARY KEY,
                        sprinter TEXT NOT NULL,
                        total_posts INTEGER NULL,
                        total_comments INTEGER NULL);
                      """

        self.conn.execute(table_posts)
        self.conn.execute(table_comments)
        self.conn.execute(table_sprinters)

    def pivot_table(self, day='%', owner='%'):

        sql_sprinters = f"SELECT sprinter from sprinters order by sprinter"
        spr = self.conn.cursor()
        spr.execute(sql_sprinters)
        sprinters = []

        sql_pivot = """SELECT
                        P.id,
                        P.owner,
                        P.link,
                        P.num_likes,
                        P.num_comments,
                    """

        for s in spr:
            sql_pivot += f"sum(case when C.author='{s[0]}' then 1 end) '{s[0]}', "
            sprinters.append(s[0])

        sql_pivot += f"""count(C.id) Total from posts P inner join comments C on P.id=C.id_post
                        where day like '{day}' and owner like '{owner}'
                        group by P.id
                        order by P.owner;
                     """
        spr.execute(sql_pivot)
        pivot = spr.fetchall()

        return sprinters, pivot

    def new_post(self, day, link):

        x = datetime.datetime.now()
        curtime = x.strftime("%Y-%m-%d %X")

        sql = 'REPLACE INTO posts(day, link, start_date) VALUES(?, ?, ?);'
        cur = self.conn.cursor()
        cur.execute(sql, (day, link, curtime))
        self.conn.commit()
        self.day = day
        self.link = link
        self.main()
        return cur.lastrowid

    def get_sprinters(self):

        sql_sprinters = f"SELECT sprinter from sprinters order by sprinter"
        spr = self.conn.cursor()
        spr.execute(sql_sprinters)
        sprinters = []

        for s in spr:
            sprinters.append(s[0])
        return sprinters

    def data_likes(self, day='%', owner='%'):

        sql_data = f"SELECT owner, sum(num_likes), sum(num_comments) from posts where day like '{day}' and owner like '{owner}' group by owner order by owner"

        if owner != '%':
            sql_data = f"SELECT day, num_likes, num_comments from posts where day like '{day}' and owner like '{owner}' order by day"

        if day != '%':
            sql_data = f"SELECT owner, num_likes, num_comments from posts where day like '{day}' and owner like '{owner}' order by day"

        data = self.conn.cursor()
        data.execute(sql_data)
        print(sql_data)

        dataset = []
        for d in data:
            s = [d[0], d[1], d[2]]
            dataset.append(s)

        sql_reactions = f"SELECT sum(num_likes), sum(num_comments) from posts where day like '{day}' and owner like '{owner}'"
        data1 = self.conn.cursor()
        data1.execute(sql_reactions)

        for d in data1:
            num_likes = d[0]
            num_comments = d[1]

        return dataset, num_likes, num_comments


if __name__ == '__main__':

    archivo_links = './posts/links_Gonzalo.txt1'
    d = 1

    try:
        links = open(archivo_links)
        for l in links.readlines():
            sprint = Sprint(d,'',l)
            sprint.file_name = archivo_links.split('_')[1][:-4] + '_' + str(d).zfill(2) + '.html'
            #print(sprint.file_name)
            #print(l)
            sprint.main()
            d += 1
        exit()
    except:
        print(f'Archivo {archivo_links} no existe')



    for file_post in os.scandir("./posts"):
        if file_post.name[-4:] == 'proc':
            print(file_post.name)
            origin = file_post.name
            dest = file_post.name[:-5]
            os.rename(f'./posts/{origin}', f'./posts/{dest}')


    for file_post in os.scandir("./posts"):
        if file_post.name[-4:] == 'html':
            print(file_post.name)
            origin = file_post.name
            dest = file_post.name + '.proc'
            num_day = file_post.name[-7:-5]

            sprint = Sprint(num_day, f'{origin}', '')
            sprint.main()
            #print(sprint.pivot_table())
            os.rename(f'./posts/{origin}', f'./posts/{dest}')


