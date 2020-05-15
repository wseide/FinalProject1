from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'bioData'
mysql.init_app(app)


@app.route('/', methods=['GET'])
def index():
    user = {'username': 'Stats'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM bioStats ORDER BY name')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, stats=result)


@app.route('/view/<int:bio_id>', methods=['GET'])
def record_view(bio_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM bioStats WHERE id=%s', bio_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', bio=result[0])


@app.route('/edit/<int:bio_id>', methods=['GET'])
def form_edit_get(bio_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM bioStats WHERE id=%s', bio_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Stats', bio=result[0])


@app.route('/edit/<int:bio_id>', methods=['POST'])
def form_update_post(bio_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('name'), request.form.get('sex'), request.form.get('age'),
                 request.form.get('height'), request.form.get('weight'), bio_id)
    sql_update_query = """UPDATE bioStats t SET t.name = %s, t.sex = %s, t.age = %s, t.height_in = 
    %s, t.weight_lbs = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/stats/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Stats Form')


@app.route('/stats/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('name'), request.form.get('sex'), request.form.get('age'),
                 request.form.get('height'), request.form.get('weight'))
    sql_insert_query = """INSERT INTO bioStats (name,sex,age,height,weight) VALUES (%s,%s,%s,%s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/delete/<int:bio_id>', methods=['POST'])
def form_delete_post(bio_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM bioStats WHERE id = %s """
    cursor.execute(sql_delete_query, bio_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/api/v1/stats', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM bioStats')
    result = cursor.fetchall()
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/stats/<int:bio_id>', methods=['GET'])
def api_retrieve(bio_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM bioStats WHERE id=%s', bio_id)
    result = cursor.fetchall()
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/stats', methods=['POST'])
def api_add() -> str:
    content = request.json
    cursor = mysql.get_db().cursor()
    inputData = (content['name'], content['sex'], content['age'], content['height'], content['weight'])
    sql_insert_query = """INSERT INTO bioStats (name,sex,age,height,weight) VALUES (%s,%s,%s,%s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/stats/<int:bio_id>', methods=['PUT'])
def api_edit(bio_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['name'], content['sex'], content['age'], content['height'], content['weight'], bio_id)
    sql_update_query = """UPDATE bioStats t SET t.name = %s, t.sex = %s, t.age = %s, t.height = 
    %s, t.weight = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/stats/<int:bio_id>', methods=['DELETE'])
def api_delete(bio_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM bioStats WHERE id = %s """
    cursor.execute(sql_delete_query, bio_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)