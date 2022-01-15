from flask import Flask, render_template, request, session, redirect, url_for
import json
from datetime import date
import sprint, model

app = Flask(__name__)
app.secret_key = "NzFiZjVjNTQzODAwYThkMWVhNGMwZWI0"

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'GET':
        session.clear()
        return render_template('index.html', mensaje='' )

    if request.method == 'POST':
        modelo = model.Modelo()
        username = request.form['username']
        password = request.form['password']
        codigo, mensaje, liuser, grupo = modelo.valida_acceso(username, password)

        if codigo == 1:
            session['username'] = username
            session['author'] = liuser
            session['grupo'] = grupo
            return redirect(url_for('track'))
        else:
            return render_template('index.html', mensaje=mensaje )

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST' and request.form['accion'] == 'signup':
        username = request.form['username']
        password = request.form['password']
        profile = request.form['profile']
        liuser = request.form['liuser']
        sprint_number = request.form['sprint_number']
        group = request.form['group']
        modelo = model.Modelo()
        codigo, mensaje = modelo.signup(username, password, profile, liuser, sprint_number, group)

        if codigo == 0:
            return render_template('signup.html', mensaje=mensaje )

    return redirect(url_for('home'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    datos = sprint.Sprint()
    if request.method == 'GET':
        sprinters, pivot = datos.pivot_table()
        day = '%'
        owner = '%'

    if request.method == 'POST':
        day = request.form['filter_day']
        owner = request.form['filter_owner']
        print(day,owner)
        sprinters, pivot = datos.pivot_table(day, owner)

    return render_template('dashboard.html', sprinters=sprinters, pivot=pivot, day_sel=day, owner_sel=owner )



@app.route('/templates', methods=['GET'])
def templates():
    if request.method == 'GET':

        templates = [
                    'https://docs.google.com/document/d/19TNXezYAPtQCBHYMhLLWrnybGg7rC8v7oh4LzF2dsRI/edit?usp=sharing',
                    'https://docs.google.com/document/d/1oLJISAjq-FZm0cuUYCidrkUYsjNdgniapmG_6jaVIx4/edit?usp=sharing',
                    'https://docs.google.com/document/d/1RM9U3NXocnLi_a_Ad7UqjXljRroJSSjNNCLOLAnY7vA/edit?usp=sharing',
                    'https://docs.google.com/document/d/1XqSi1kz6Q4VPEmBhj7ILr1gV-pFA8h-VKm7AZIn33uc/edit?usp=sharing',
                    'https://docs.google.com/document/d/1rRbf8mSTaDKpyTsHy2ATLXlHgBYzQYq4Qwoc50b4tWc/edit?usp=sharing',
                    'https://docs.google.com/document/d/1uEHSpBe9_W6NDPLUF8PlxO3EJz6LDLl2rFMoJJTrngY/edit?usp=sharing',
                    'https://docs.google.com/document/d/1IAAK8e1gvDSFNUio4FYImz1bGORVtPvPesxkVclUxAI/edit?usp=sharing',
                    'https://docs.google.com/document/d/1X7a2tcRLAH-JuRsibwuu4SOnr3DHSJVm9PMztGDLA-Y/edit?usp=sharing',
                    'https://docs.google.com/document/d/1yT5I5nNMHYsaijGRhc3LV_z5Ih2xuKWQEYzGSAWp5lM/edit?usp=sharing',
                    'https://docs.google.com/document/d/11yTG4t4BHrpO2m2u9TGzdVKL3u-20_8mGW6ydwwQBEg/edit?usp=sharing',
                    'https://docs.google.com/document/d/130VztGYUjEYxCx670Xa0zaQBqlc_1Fo4mle7vj4PKqk/edit?usp=sharing',
                    'https://docs.google.com/document/d/1qDyU7-yik0KVhmr8yTajzwixo5hw4ZQzB1yth9QGV9M/edit?usp=sharing',
                    'https://docs.google.com/document/d/1hPAKZ-SUJRLW6--_YZkIy_ThpGivWXCIobJuyles3Hs/edit?usp=sharing',
                    'https://docs.google.com/document/d/18P_3qtU36xvOHAKtm3kYr0vvlVXR7suKJuouJ3g2WIU/edit?usp=sharing',
                    'https://docs.google.com/document/d/11EKLlSbYks28hMJdO-KkgDgIwwPny_NaSl7ihB6X9Ys/edit?usp=sharing',
                    ]

        return render_template('templates_sprint.html', templates=enumerate(templates))


@app.route('/new_post', methods=['GET','POST'])
def new_post():
    if request.method == 'GET':
        return render_template('new_post.html' )

    if request.method == 'POST':
        day = request.form['day_number']
        link = request.form['new_link']
        owner = request.form['fauthor']
        datos = sprint.Sprint()
        datos.new_post(day, link, owner)
        return redirect(request.referrer)
        #return render_template('new_post.html' )


@app.route('/track', methods=['GET','POST'])
def track():
    datos = sprint.Sprint()
    username = session['username']
    #author = datos.get_liuser(username)
    author = session['author']
    grupo = session['grupo']

    if request.method == 'GET':
        d1 = date(2022, 1, 9)
        d2 = date.today()
        day = (d2 - d1).days
        owner_sel = '%'

    if request.method == 'POST':

        if 'filter_day' in request.form:
            day = request.form['filter_day']

        if 'owner_sel' in request.form:
            owner_sel = request.form['owner_sel']

        data = request.json

        if data:
            day = data[0]['day']
            id_post = data[1]['id_post']
            action = data[2]['action']
            datos.insert_comments2(day, id_post, author, '', action)

    links = datos.get_links(day, owner_sel, author, grupo)
    sprinters = datos.get_sprinters()[0]

    return render_template('track.html', day_sel=day, links=links, sprinters=sprinters, author=author, owner_sel=owner_sel)


@app.route('/myposts', methods=['GET','POST'])
def myposts():
    datos = sprint.Sprint()
    username = session['username']
    author = session['author']
    grupo = session['grupo']

    if 'owner_sel' in session:
        owner_sel = session['owner_sel']
    else:
        owner_sel =  author

    d1 = date(2022, 1, 9)
    d2 = date.today()
    day = (d2 - d1).days

    if request.method == 'GET':
        pass

    if request.method == 'POST':
        owner_sel = request.form['owner_sel']
        session['owner_sel'] = owner_sel
        print(owner_sel)

    links = datos.get_myposts(owner_sel)
    sprinters = datos.get_sprinters()[0]
    return render_template('myposts.html', day_sel=day, links=links, sprinters=sprinters, author=author, owner_sel=owner_sel, username=session['username'])

@app.route('/edit_post', methods=['GET','POST'])
def edit_post():

    if request.method == 'GET':
        datos = sprint.Sprint()
        id_post = request.args['id_post']
        datos_post = datos.get_post(id_post)
        sprinters = datos.get_sprinters()[0]
        print(datos_post)
        return render_template('edit_post.html', datos=datos_post, sprinters=sprinters)

    if request.method == 'POST':
        #and request.form['accion'] == 'edit':
        print(request.form['accion'])
        id_post = request.form['id_post']
        link = request.form['link']
        num_views = request.form['num_views']
        num_likes = request.form['num_likes']
        num_comments = request.form['num_comments']
        owner = request.form['owner_sel']
        datos = sprint.Sprint()
        datos.edit_post(id_post, link, num_views, num_likes, num_comments, owner)
        return redirect(url_for('myposts'))

@app.route('/delete_post', methods=['GET','POST'])
def delete_post():

    if request.method == 'GET':
        id_post = request.args['id_post']
        print(id_post)
        datos = sprint.Sprint()
        datos.delete_post(id_post)
    return redirect(request.referrer)

@app.route('/sprinters', methods=['GET','POST'])
def sprinters():

    datos = sprint.Sprint()
    sprinters = datos.get_sprinters()[1]
    return render_template('sprinters.html', sprinters=sprinters)

@app.route('/edit_sprinter', methods=['GET','POST'])
def edit_sprinter():

    if request.method == 'GET':
        datos = sprint.Sprint()
        id_sprinter = request.args['id_sprinter']
        datos_sprinter = datos.get_sprinter(id_sprinter)
        print(datos_sprinter)
        return render_template('edit_sprinter.html', datos=datos_sprinter)

    if request.method == 'POST':
        id_sprinter = request.form['id_sprinter']
        sprinter = request.form['sprinter']
        profile = request.form['profile']
        sprint_number = request.form['sprint_number']
        group = request.form['group']
        datos = sprint.Sprint()
        datos.edit_sprinter(id_sprinter, sprinter, profile, sprint_number, group)
        return redirect(url_for('sprinters'))

@app.route('/delete_sprinter', methods=['GET','POST'])
def delete_sprinter():

    if request.method == 'GET':
        id_sprinter = request.args['id_sprinter']
        datos = sprint.Sprint()
        datos.delete_sprinter(id_sprinter)
    return redirect(request.referrer)

@app.route("/stats", methods=['GET', 'POST'])
def chart():

    if request.method == 'POST':
        day = request.form['filter_day']
        owner = request.form['filter_owner']
        print(day,owner)

    else:
        day = '%'
        owner = '%'

    datos = sprint.Sprint()
    sprinters = datos.get_sprinters()[0]
    dataset, num_likes, num_comments = datos.data_likes(day, owner)
    print('Datos:', dataset)
    print('Likes:', num_likes)
    print('Comments:', num_comments)


    return render_template('chart.html', dataset=dataset, day_sel=day, owner_sel=owner, sprinters=sprinters, num_likes=num_likes, num_comments=num_comments)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)





