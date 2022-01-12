import sqlite3
#import sys
#import traceback

class Modelo:

    def abre_conexion(self):
        self.connection =  sqlite3.connect('sprint.db', check_same_thread = False)
        self.cursor = self.connection.cursor()

    def cierra_conexion(self):
        self.cursor.close()
        self.connection.close()

    def query(self, query):
        self.abre_conexion()

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            #print("Exception class is: ", er.__class__)
            #print('SQLite traceback: ')
            #exc_type, exc_value, exc_tb = sys.exc_info()
            #print(traceback.format_exception(exc_type, exc_value, exc_tb))

    def signup(self, username, password):

        self.query(f"SELECT pk from users where username='{username}' order by pk DESC")
        exist = self.cursor.fetchone()

        if exist == None:
            self.query(f"INSERT INTO USERS(username, password) VALUES('{username}', '{password}')")
            mensaje = [1, f'Usuario {username} Registrado Exitosamente']

        else:
            mensaje = [0, f'Usuario {username} ya existe, elige otro.']

        self.cierra_conexion()
        return mensaje

    def get_users(self):
        self.query(f"SELECT username from users order by pk DESC")
        db_users = self.cursor.fetchall()
        users = []

        for i in range(len(db_users)):
            person = db_users[i][0]
            users.append(person)

        self.cierra_conexion()
        return users

    def valida_acceso(self, username, password):
        query = f"SELECT username, password from users where username='{username}' and password='{password}' order by pk DESC"
        self.query(query)

        existe = self.cursor.fetchone()
        mensaje = [0, 'User/password incorrect'] if existe is None else [1, 'Usuario Válido']

        self.cierra_conexion()
        return mensaje

    def get_id_user(self, usuario):
        self.query(f"SELECT pk from users where username='{usuario}'")
        return self.cursor.fetchone()[0]


if __name__=='__main__':

    modelo = Modelo()
    signup = modelo.signup('jjayala3', '12345')
    print(signup)

    #usuarios = modelo.get_users()
    #print(usuarios)

    #acceso = modelo.valida_acceso('jjayala', '12345')
    #print(acceso)

