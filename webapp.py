import flask
from flask import request, render_template
import MySQLdb as my
import json
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# A route to return all of the available entries in our catalog.
@app.route('/', methods=['GET'])
def spots(): 

    db = my.connect(host='localhost',
                    user='webdb',
                    passwd='Zw73dp',
                    db='dxcluster'
                    )

    cursor = db.cursor()
    number_of_rows = cursor.execute('''SET NAMES 'utf8';''')
    number_of_rows = cursor.execute('''SELECT rowid, spotter, freq, spotcall, comment, time from dxcluster.spot ORDER BY rowid desc limit 100;''')
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    rv=cursor.fetchall()
    payload=[]
    for result in rv:
        payload.append(dict(zip(row_headers,result)))

    db.close()
    #print payload
    return render_template(
            'results.html',
           # response=json.dumps(payload)
           payload=payload
    )

app.run(host='0.0.0.0',port=8080)

