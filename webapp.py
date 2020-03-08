import os
import flask
from flask import request, render_template, jsonify
import MySQLdb as my
import json

__author__ = 'IU1BOW - Corrado'


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'secret!'

#load config file
with open('cfg/config.json') as json_data_file:
        cfg = json.load(json_data_file)

#load bands file
with open('cfg/bands.json') as json_bands:
        band_frequencies = json.load(json_bands)

#load country file (and send it to front-end)
def load_country():
    filename = os.path.join(app.static_folder, 'country.json')
    with open(filename) as country_file:
        return json.load(country_file)

#find band in json frequency array
def find_band_freq(json_object, name):
    return [obj for obj in json_object if obj['id']==name][0]

def spotquery():

    try:
        # trancodificare cqdx da regione AF a cq
        # costruire query con nulla,  spotcq, spotde, band in successione 
        
        #get url parameters
        band=(request.args.getlist('b'))
        dere=(request.args.getlist('e'))
        dxre=(request.args.getlist('x'))

        #construct band query decoding frequencis with json file
        band_qry_string = '(('
        for i in range(len(band)):
            freq=find_band_freq(band_frequencies["bands"],band[i])
            if i > 0:
                band_qry_string += ') OR ('

            band_qry_string += 'freq BETWEEN ' + str(freq["min"]) + ' AND ' + str(freq["max"])

        band_qry_string += '))'
        query_string="SELECT rowid, spotter AS de, freq, spotcall AS dx, comment AS comm, time, spotdxcc from dxcluster.spot "                                  
        if len(band) > 0:
            query_string += " WHERE "   
            query_string += band_qry_string
        
        query_string += " ORDER BY rowid desc limit 50;"  
        print query_string

        #connect to db
        db = my.connect(host=cfg['mysql']['host'],
                    user=cfg['mysql']['user'],
                    passwd=cfg['mysql']['passwd'],
                    db=cfg['mysql']['db']
                    )

        cursor = db.cursor()
        number_of_rows = cursor.execute('''SET NAMES 'utf8';''')
        cursor.execute(query_string)
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        rv=cursor.fetchall()
        payload=[]
        for result in rv:
            payload.append(dict(zip(row_headers,result)))
        cursor.close()
        return payload
    except Exception as e:
        print(e)

    finally:
        db.close()

@app.route('/spotlist', methods=['GET']) 
def spotlist():
    response=flask.Response(json.dumps(spotquery()))
    return response

@app.route('/', methods=['GET']) 
def spots():
    payload=spotquery()
    country_data=load_country()
    response=flask.Response(render_template('index.html',payload=payload,timer_interval=cfg['timer']['interval'],country_data=country_data))
    #response=flask.Response(render_template('index.html',payload=payload,timer_interval=cfg['timer']['interval']))
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')
