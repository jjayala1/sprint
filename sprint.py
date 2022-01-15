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
        self.ruta = './'
        #self.ruta = '/home/sprintOct21/sprint'
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

    def insert_comments2(self, day, id_post, author, message, action):

        cur = self.conn.cursor()
        print(action)

        if action == False:
            sql_del = f"DELETE FROM comments WHERE id_post='{id_post}' and author='{author}' and message=''"
            print(sql_del)
            cur.execute(sql_del)
            self.conn.commit()

        else:
            sql_ins = 'INSERT OR IGNORE INTO comments(id_post, author, message) VALUES(?,?,?);'
            cur.execute(sql_ins, (id_post, author, message))
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
                        message TEXT NOT NULL,
                        UNIQUE(id_post, author, message));
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
        print(sql_pivot)
        pivot = spr.fetchall()

        return sprinters, pivot

    def new_post(self, day, link, owner):

        x = datetime.datetime.now()
        curtime = x.strftime("%Y-%m-%d %X")

        sql = 'REPLACE INTO posts(day, link, owner, start_date) VALUES(?, ?, ?, ?);'
        print(sql,day, link, owner, curtime)
        cur = self.conn.cursor()
        cur.execute(sql, (day, link, owner, curtime))
        self.conn.commit()
        self.day = day
        self.link = link
        #self.main()
        return cur.lastrowid

    def get_sprinters(self):

        sql_sprinters = f"SELECT S.*,PC.num_posts,PC.num_comments from sprinters S LEFT JOIN (SELECT owner,count(*) num_posts, C.num_comments FROM posts P LEFT JOIN (SELECT id_post,count(*) num_comments FROM comments GROUP BY id_post) C on P.id=C.id_post GROUP BY owner) PC on S.sprinter=PC.owner order by S.sprinter"
        print(sql_sprinters)
        spr = self.conn.cursor()
        spr.execute(sql_sprinters)
        sprinters = spr.fetchall()
        sprinters_name = []

        for s in sprinters:
            sprinters_name.append(s[1])
        return sprinters_name, sprinters

    def get_links(self, day, owner, author, grupo):

        sql_links = f"SELECT P.id,P.day,owner,link,sum(tot_comm), sum(auth_comm) from posts P inner join sprinters S on P.owner=S.sprinter left join (select id_post,author, sum(case when author='{author}' then 1 end) as auth_comm, count(*) as tot_comm from comments where message='' group by id_post) C on P.id=C.id_post WHERE S.grupo='{grupo}' and P.day like '{day}' and P.owner like '{owner}' GROUP BY P.id ORDER BY owner,day"
        print(sql_links)
        lnk = self.conn.cursor()
        lnk.execute(sql_links)
        links = lnk.fetchall()
        return links

    def get_myposts(self, author):

        sql_links = f"SELECT P.id, day, owner, link, start_date, num_views, num_likes, num_comments, count(id_post) from posts P inner join sprinters S on P.owner=S.sprinter left join (select * from comments where message='') C on P.id=C.id_post WHERE P.owner='{author}' group by P.id,owner,link ORDER BY day"
        print(sql_links)
        lnk = self.conn.cursor()
        lnk.execute(sql_links)
        links = lnk.fetchall()
        return links

#######################################################################################################################
##########################################ABC POST#################################################################
#######################################################################################################################
    def get_post(self, id_post):

        sql_post = f"SELECT id, owner, link, num_views, num_likes, num_comments from posts where id={id_post}"
        print(sql_post)
        pst = self.conn.cursor()
        pst.execute(sql_post)
        return pst.fetchone()

    def edit_post(self, id_post, link, num_views, num_likes, num_comments, owner):
        sql_edit=f"UPDATE posts SET owner='{owner}', link='{link}', num_views='{num_views}', num_likes='{num_likes}', num_comments='{num_comments}' where id={id_post}"
        print(sql_edit)
        lnk_edt = self.conn.cursor()
        lnk_edt.execute(sql_edit)
        self.conn.commit()

    def delete_post(self, id_post):
        sql_delete=f"DELETE FROM posts where id={id_post}"
        print(sql_delete)
        lnk_del = self.conn.cursor()
        lnk_del.execute(sql_delete)
        self.conn.commit()

#######################################################################################################################
##########################################ABC SPRINTER#################################################################
#######################################################################################################################
    def get_sprinter(self, id_sprinter):

        sql_spt = f"SELECT * from sprinters where id={id_sprinter}"
        spt = self.conn.cursor()
        spt.execute(sql_spt)
        return spt.fetchone()

    def edit_sprinter(self, id_sprinter, sprinter, profile, sprint_number, group):
        sql_edit=f"UPDATE sprinters SET sprinter='{sprinter}', profile='{profile}', sprint_number='{sprint_number}', grupo='{group}' where id={id_sprinter}"
        lnk_edt = self.conn.cursor()
        lnk_edt.execute(sql_edit)
        self.conn.commit()

    def delete_sprinter(self, id_sprinter):
        sql_delete=f"DELETE FROM sprinters where id={id_sprinter}"
        lnk_del = self.conn.cursor()
        lnk_del.execute(sql_delete)
        self.conn.commit()

    def get_liuser(self, author):
        sql_liusr = f"SELECT liuser from users where username='{author}'"
        print(sql_liusr)
        liu = self.conn.cursor()
        liu.execute(sql_liusr)
        liusr = liu.fetchall()
        return liusr[0][0]

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


