from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import json
from datetime import date
import sprint, model
from slack_sdk import WebClient


app = Flask(__name__)
app.secret_key = "NzFiZjVjNTQzODAwYThkMWVhNGMwZWI0"

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'GET':
        session.clear()
        return render_template('index.html', mensaje='' )

    if request.method == 'POST':
        datos = sprint.Sprint()
        #modelo = model.Modelo()
        username = request.form['username']
        password = request.form['password']
        codigo, mensaje, liuser, grupo = datos.valida_acceso(username, password)
        print(codigo, mensaje, liuser, grupo)

        if codigo == 1:
            session['username'] = username
            session['author'] = liuser
            session['grupo'] = grupo

            return redirect(url_for('myposts'))
        else:
            return render_template('index.html', mensaje=mensaje )

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST' and request.form['accion'] == 'signup':
        username = request.form['username']
        password = request.form['password']
        liuser = request.form['liuser']
        profile = request.form['profile']
        slack_username = request.form['slack_username']
        sprint_number = request.form['sprint_number']
        group = request.form['group']
        datos = sprint.Sprint()
        codigo, mensaje = datos.signup(username, password, liuser, profile, slack_username, sprint_number, group)

        if codigo == 0:
            return render_template('signup.html', mensaje=mensaje )

    return redirect(url_for('home'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    username = validate_session()
    if username == 0:
        return redirect(url_for('home'))

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

    sprinters_combo, cur_day, sprinter_sel, author = variables_new_post()
    return render_template('dashboard.html', sprinters=sprinters, pivot=pivot, day_sel=day, owner_sel=owner, username=username, sprinters_combo=sprinters_combo, cur_day=cur_day, sprinter_sel=sprinter_sel, author=author )



@app.route('/templates', methods=['GET'])
def templates():
    username = validate_session()
    if username == 0:
        return redirect(url_for('home'))

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

        sprinters_combo, cur_day, sprinter_sel, author = variables_new_post()
        return render_template('templates_sprint.html', templates=enumerate(templates), username=username, sprinters_combo=sprinters_combo, cur_day=cur_day, sprinter_sel=sprinter_sel, author=author)


@app.route('/new_post', methods=['GET','POST'])
def new_post():
    print(request.method)
    if request.method == 'GET':
        return render_template('new_post.html' )

    if request.method == 'POST':

        data = request.json

        if data:
            #print(data)
            day = data['new_day']
            owner = data['new_sprinter']
            link = data['new_link']
            #print(f"Datos: {day}, {owner}, {link}")
            datos = sprint.Sprint()
            datos.new_post(day, link, owner)
        return jsonify(response='ok'), 201


@app.route('/track', methods=['GET','POST'])
def track():
    username = validate_session()
    if username == 0:
        return redirect(url_for('home'))

    datos = sprint.Sprint()
    #author = datos.get_liuser(username)
    author = session['author']
    grupo = session['grupo']

    day = get_sprint_day()
    owner_sel = '%'

    if request.method == 'POST':

        if 'day_sel' in request.form:
            day = request.form['day_sel']

        if 'sprinter_sel' in request.form:
            sprinter_sel = request.form['sprinter_sel']

        data = request.json

        if data:
            day = data[0]['day']
            id_post = data[1]['id_post']
            action = data[2]['action']
            datos.insert_comments2(day, id_post, author, '', action)

    links = datos.get_links(day, owner_sel, author, grupo)
    sprinters = datos.get_sprinters()[0]

    return render_template('track.html', day_sel=day, links=links, sprinters=sprinters, author=author, owner_sel=owner_sel, username=username)


@app.route('/save_check', methods=['POST'])
def save_check():
    if request.method == 'POST':

        author = session['author']
        data = request.json

        if data:
            day = data[0]['day']
            id_post = data[1]['id_post']
            action = data[2]['action']
            datos = sprint.Sprint()
            datos.insert_comments2(day, id_post, author, '', action)
        return jsonify(response='ok'), 201


@app.route('/myposts', methods=['GET','POST'])
def myposts():

    username = validate_session()
    if username == 0:
        return redirect(url_for('home'))

    datos = sprint.Sprint()

    if 'group_sel' in session:
        group_sel = session['group_sel']
    elif 'grupo' in session:
        group_sel = session['grupo']
    else:
        group_sel = '%'

    if request.method == 'GET':
        sprinters_combo, cur_day, sprinter_sel, author = variables_new_post(group_sel)

    if 'day_sel' in session:
        day_sel = session['day_sel']
    else:
        day_sel = cur_day

    if request.method == 'POST':
        group_sel = request.form['group_sel']
        day_sel = request.form['day_sel']
        sprinter_sel = request.form['sprinter_sel']
        sprinters_combo, cur_day, sprinter_sel1, author = variables_new_post(group_sel)
        session['group_sel'] = group_sel
        session['day_sel'] = day_sel
        session['sprinter_sel'] = sprinter_sel
        print("SESSION: " + session['group_sel'], session['day_sel'], session['sprinter_sel'])

    print("FILTERS: " + group_sel, day_sel, sprinter_sel)
    links = datos.get_myposts(day_sel, sprinter_sel, author, group_sel)
    return render_template('myposts.html', group_sel=group_sel, day_sel=day_sel, sprinter_sel=sprinter_sel, links=links, author=author, username=username, sprinters_combo=sprinters_combo, cur_day=cur_day)


@app.route('/get_posts_curl', methods=['GET'])
def get_posts_curl():

    if request.method == 'GET':
        datos = sprint.Sprint()
        cur_day = get_sprint_day()
        curl_posts = datos.get_posts_curl(cur_day, '%')
        print(curl_posts)
        return curl_posts, 200

    if request.method == 'POST':
        return jsonify(response='ok'), 201

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
    username = validate_session()
    if username == 0:
        return redirect(url_for('home'))

    datos = sprint.Sprint()
    sprinters = datos.get_sprinters()[1]
    sprinters_combo, cur_day, sprinter_sel, author = variables_new_post()
    return render_template('sprinters.html', sprinters=sprinters, username=username, sprinters_combo=sprinters_combo, cur_day=cur_day, sprinter_sel=sprinter_sel, author=author)

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
        username = request.form['username']
        password = request.form['password']
        sprinter = request.form['sprinter']
        #slack_username = request.form['slack_username']
        profile = request.form['profile']
        sprint_number = request.form['sprint_number']
        group = request.form['group']
        datos = sprint.Sprint()
        print(id_sprinter, username, password, sprinter, profile, sprint_number, group)
        datos.edit_sprinter(id_sprinter, username, password, sprinter, profile, sprint_number, group)
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

    username = validate_session()

    datos = sprint.Sprint()

    if 'group_sel' in session:
        group_sel = session['group_sel']
    elif 'grupo' in session:
        group_sel = session['grupo']
    else:
        group_sel = '%'

    if request.method == 'GET':
        sprinters_combo, cur_day, sprinter_sel, author = variables_new_post(group_sel)

    if 'day_sel' in session:
        day_sel = session['day_sel']
    else:
        day_sel = cur_day

    if request.method == 'POST':
        group_sel = request.form['group_sel']
        day_sel = request.form['day_sel']
        sprinter_sel = request.form['sprinter_sel']
        sprinters_combo, cur_day, sprinter_sel1, author = variables_new_post(group_sel)
        session['group_sel'] = group_sel
        session['day_sel'] = day_sel
        session['sprinter_sel'] = sprinter_sel
        print("SESSION: " + session['group_sel'], session['day_sel'], session['sprinter_sel'])

    print("FILTERS: " + group_sel, day_sel, sprinter_sel)
    dataset, num_posts, num_likes, num_comments = datos.data_likes(group_sel, day_sel, sprinter_sel)

    if day_sel == '%':
        days = cur_day
    else:
        days = 1

    completion = f"{int(num_posts.replace(',','')) / (int(days)*len(sprinters_combo)):0.1%}"

    print('Sprinters:', len(sprinters_combo))
    print('Days:', days)
    print('Posts:', num_posts)
    print('Likes:', num_likes)
    print('Comments:', num_comments)

    return render_template('chart.html', dataset=dataset, group_sel=group_sel, day_sel=day_sel, sprinter_sel=sprinter_sel, num_posts=num_posts, completion=completion, num_likes=num_likes, num_comments=num_comments, username=username, sprinters_combo=sprinters_combo, cur_day=cur_day, author=author)


@app.route("/validate", methods=['GET', 'POST'])
def validate_session():
    if 'username' in session:
        print(f"Username: {session['username']}")
        return session['username']
    else:
        return '0'

def get_sprint_day():
    d1 = date(2022, 3, 14)
    d2 = date.today()
    return (d2 - d1).days + 1
    

def variables_new_post(group_sel='%'):

    datos = sprint.Sprint()

    #if 'sprinters_combo' not in session:
    session['sprinters_combo'] = datos.get_sprinters(group_sel)[0]

    if 'cur_day' not in session:
        session['cur_day'] = get_sprint_day()
    
    if 'author' in session:
        author = session['author']
    else: 
        author = '%'

    if 'sprinter_sel' in session:
        sprinter_sel = session['sprinter_sel']
    else:
        sprinter_sel =  author

    print(session['sprinters_combo'])
    return session['sprinters_combo'], session['cur_day'], sprinter_sel, author


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('home'))


########################################################################################################################################
#################################################SLACK FUNCTIONS########################################################################
########################################################################################################################################


@app.route("/slack", methods=['GET', 'POST'])
def slack():

    if request.method == 'GET':
        print("HELLO")
        data = request.values
        return f"HELLO {data}"

    if request.method == 'POST':
        client = WebClient(token=get_slack_token())
        data = request.json
        data1 = request.form

        challenge = "ok"
        if data is not None:

            #with open('data.txt', 'w') as f:
            #    f.write(data)

            if 'challenge' in data:
                challenge = data['challenge'] 

            if 'event' in data:
                if 'reaction' in data['event']:
                    print(data['event']['user'])
                    reaction = data['event']['reaction']
                    response = client.chat_postMessage(channel='U01NNASMGSV', text=reaction)
                elif data['event']['type'] == 'link_shared':
                    link = data['event']['links'][0]['url']
                    print(data['event']['user'])
                    print(link)

        if 'payload' in data1:
            data2 = json.loads(data1['payload'])
            print(type(data1))
            print(type(data2))
            print(len(data2))

            with open('payload.txt', 'w') as f:
                for i in data1['payload']:
                    f.write(i)

            #for k in data2.keys():
            #    print(k)
            #print(data2)

            #Block for new post
            if data2['type'] == 'view_submission' and 'view' in data2:  
                if 'state' in data2['view']:  
                    if 'values' in data2['view']['state']:  
                        if 'combo_day' in data2['view']['state']['values']:  
                            import modal
                            print(data2['view']['state']['values']['combo_day']['static_select-action'])
                            day = data2['view']['state']['values']['combo_day']['static_select-action']['selected_option']['value']
                            link = data2['view']['state']['values']['link']['plain_text_input-action']['value']

                            if link == '':
                                view = modal.get_view_new_post_status('link')

                            owner = data2['user']['username']
                            print(data2['user'])
                            datos = sprint.Sprint()
                            id_np = datos.new_post(day, link, owner)

                            if id_np:
                                view = modal.get_view_new_post_status('ok')
                            else:
                                view = modal.get_view_new_post_status('error')

                            payload = {"response_action": "push",
                                       "view": view
                                      }

                            client = WebClient(token=get_slack_token())
                            #response = client.views_push(**payload)
                            return (payload, 200)

            #Block for track comments
            print(data2['actions'])
            if 'actions' in data2:  
                boton = data2['actions'][0]['value']
                print(data2['actions'])

                if 'action_id' in data2['actions'][0]:
                    slack_checkbox(data2)



            #response = client.chat_postMessage(channel='U01NNASMGSV', text=boton)


        #with open('payload.txt', 'w') as f:
        #    for i in data1['payload']:
        #        f.write(i)


        return f"challenge: {challenge}"

def slack_checkbox(data):
    print('--------------------------------------------------------------------')
    print('--------------------------------------------------------------------')
    print(data['user'])
    print(data['actions'])
    print(data['user']['username'], data['actions'][0]['action_id'])
    datos = sprint.Sprint()

    author = data['user']['username']
    #author = 'José de Jesús Juárez Ayala'
    id_post = data['actions'][0]['action_id'] 
    day = data['actions'][0]['value']
    action = True

    datos.insert_comments2(day, id_post, author, '', action)


@app.route("/slack_track_posts", methods=['GET', 'POST'])
def slack_track_posts():

    if request.method == 'POST':
        import modal
        data = request.form
        trigger_id = data['trigger_id']

        datos = sprint.Sprint()
        day = data['text']

        if day == '':
            day = get_sprint_day()

        owner_sel = '%'
        author = 'José de Jesús Juárez Ayala'
        grupo = '1'
        links = datos.get_links(day, owner_sel, author, grupo)
        
        #print('--------------------------------------------')
        #print(data)
        #print(day, links)

        view = modal.get_view_posts(day, links)
        payload = {"trigger_id": f"{trigger_id}", 
                   "view": view
                  }

        client = WebClient(token=get_slack_token())
        response = client.views_open(**payload)
        return ('', 200)

@app.route("/slack_new_post", methods=['GET', 'POST'])
def slack_new_post():

    if request.method == 'POST':
        import modal

        datos = sprint.Sprint()

        data = request.form
        trigger_id = data['trigger_id']
        link = data['text']

        link = data['text']
        day = get_sprint_day()

        if link == '':
            view = modal.get_view_new_post(day)

        else:
            link = data['text']
            owner = 'delete'
            id_np = datos.new_post(day, link, owner)

            if id_np:
                view = modal.get_view_new_post1('ok')
            else:
                view = modal.get_view_new_post1('error')


        payload = {"trigger_id": f"{trigger_id}", 
                   "view": view
                  }

        client = WebClient(token=get_slack_token())
        response = client.views_open(**payload)
        return ('', 200)

def get_slack_token():
    return 'xoxb-1781579884544-2944839523991-kC5uCZaYnvDUnBQnyba46pDg'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)

