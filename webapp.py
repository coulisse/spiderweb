import flask
from flask import request, render_template
import MySQLdb as my
import json

__author__ = 'IU1BOW - Corrado'


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'secret!'

with open('config.json') as json_data_file:
        cfg = json.load(json_data_file)

def spotquery():

    db = my.connect(host=cfg['mysql']['host'],
                    user=cfg['mysql']['user'],
                    passwd=cfg['mysql']['passwd'],
                    db=cfg['mysql']['db']
                    )
    cursor = db.cursor()
    number_of_rows = cursor.execute('''SET NAMES 'utf8';''')
    number_of_rows = cursor.execute('''SELECT rowid, spotter AS de, freq, spotcall AS dx, comment AS comm, time from dxcluster.spot ORDER BY rowid desc limit 50;''')
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    rv=cursor.fetchall()
    payload=[]
    for result in rv:
        payload.append(dict(zip(row_headers,result)))

    db.close()
    return payload

@app.route('/spotlist', methods=['GET']) 
def spotlist():
    response=flask.Response(json.dumps(spotquery()))
    return response

@app.route('/', methods=['GET']) 
def spots():
    payload=spotquery()
    response=flask.Response(render_template('index.html',payload=payload))
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')
