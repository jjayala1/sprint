import requests
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
import datetime


class Sprint():

    def __init__(self, user=''):
        self.user = user
        self.conn = self.create_database('/home/sprintOct21/sprint/sprint.db');
        self.create_tables()

        #self.link = 'https://www.linkedin.com/posts/gonzalo-career-strategist_jobs-careers-jobseekers-activity-6854777607670632448-MiOP/'
        #self.link = 'https://www.linkedin.com/posts/ricky-wk-tam_cybersecurity-data-security-activity-6854815806149283840-SpTa'
        #self.link = 'https://www.linkedin.com/posts/anabullard_emotionalintelligence-selfawareness-settingboundaries-activity-6855921741961715712-AqGV'
        self.link = ''
        self.data = ''

    def main(self):

        if self.user != '':
            self.read_file(self.user)
        elif self.link != '':
            self.get_page()

        if self.data != '':
            #print(self.data)
            #exit()
            self.soup = BeautifulSoup(self.data, "html.parser")
            self.get_likes()
            self.get_comments()

    def get_page(self):
        page = requests.get(self.link)
        #with open('/home/sprintOct21/sprint/file.txt', 'bw') as file:
        #    file.write(page.content)
        self.data = page.content

    def read_file(self):
        f = open(f'{self.user}.html');
        self.data = f.read()

    def get_likes(self):
        self.owner = self.soup.find('a', class_ = 'share-update-card__actor-text-link').text.strip()
        self.num_likes = self.soup.find('span', class_ = 'social-counts-reactions__social-counts-numRections').text.strip()
        #num_comments = self.soup.find_all('a', { 'class':'social-action-counts__social-counts-item'})
        self.num_comments = self.soup.select('a[class="social-action-counts__social-counts-item"]')[0].text.strip().split()[0]
        print(self.num_likes, self.num_comments)
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
                        P.day,
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
        print(sql_pivot)
        print(f"where day like '{day}' and owner like '{owner}'")
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


if __name__ == '__main__':
    sprint = Sprint()
    sprint.main()
    print(sprint.pivot_table())


