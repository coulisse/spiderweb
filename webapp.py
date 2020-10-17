import os
import flask
from flask import request, render_template, jsonify
import MySQLdb as my
import json

__author__ = 'IU1BOW - Corrado'

app = flask.Flask(__name__)
app.config["DEBUG"] = False 
app.config['SECRET_KEY'] = 'secret!'

#load config file
with open('cfg/config.json') as json_data_file:
        cfg = json.load(json_data_file)

#load bands file
with open('cfg/bands.json') as json_bands:
        band_frequencies = json.load(json_bands)

#load mode file
with open('cfg/modes.json') as json_modes:
        modes_frequencies = json.load(json_modes)

#load continents-cq file
with open('cfg/continents.json') as json_continents:
        continents_cq = json.load(json_continents)

#load country file (and send it to front-end)
def load_country():
    filename = os.path.join(app.static_folder, 'country.json')
    with open(filename) as country_file:
        return json.load(country_file)

#find id  in json : ie frequency / continent
def find_id_json(json_object, name):
    return [obj for obj in json_object if obj['id']==name][0]


#the main query to show spots
#it gets url parameter in order to apply the build the right query
#and apply the filter required. It returns a json with the spots
def spotquery():

    try:
        #get url parameters
        band=(request.args.getlist('b'))
        dere=(request.args.getlist('e'))
        dxre=(request.args.getlist('x'))
        mode=(request.args.getlist('m'))
        callsign=request.args.get('c')  
        query_string=''
        if callsign:
            #construct the query, to show last 6 month
#           query_string="SELECT rowid, spotter AS de, freq, spotcall AS dx, comment AS comm, time, spotdxcc from dxcluster.spot WHERE (spotter='"+callsign+"' OR spotcall='"+callsign+"')"                    
#           query_string+=" AND  time > UNIX_TIMESTAMP()-16070400"
#           query_string+=" ORDER BY  CASE spotter  WHEN '"+callsign+"' THEN 1 ELSE -1 END ASC, rowid desc limit 20;"

            query_string="(SELECT rowid, spotter AS de, freq, spotcall AS dx, comment AS comm, time, spotdxcc from dxcluster.spot WHERE spotter='"+callsign+"'"                    
            query_string+=" ORDER BY rowid desc limit 10)"

            query_string+=" UNION "

            query_string+="(SELECT rowid, spotter AS de, freq, spotcall AS dx, comment AS comm, time, spotdxcc from dxcluster.spot WHERE spotcall='"+callsign+"'" 
            query_string+=" ORDER BY rowid desc limit 10);"

        else:    
            #construct band query decoding frequencies with json file
            band_qry_string = ' AND (('
            for i in range(len(band)):
                freq=find_id_json(band_frequencies["bands"],band[i])
                if i > 0:
                    band_qry_string += ') OR ('

                band_qry_string += 'freq BETWEEN ' + str(freq["min"]) + ' AND ' + str(freq["max"])

            band_qry_string += '))'

            #construct mode query 
            mode_qry_string = ' AND  (('
            for i in range(len(mode)):
                single_mode=find_id_json(modes_frequencies["modes"],mode[i])
                if i > 0: 
                        mode_qry_string +=') OR ('
                for j in range(len(single_mode["freq"])):
                    if j > 0: 
                        mode_qry_string +=') OR ('
                    mode_qry_string += 'freq BETWEEN ' +str(single_mode["freq"][j]["min"]) + ' AND ' + str(single_mode["freq"][j]["max"])

            mode_qry_string += '))'

            #construct DE continent region query
            dere_qry_string = ' AND spottercq IN ('
            for i in range(len(dere)):
                continent=find_id_json(continents_cq["continents"],dere[i])
                if i > 0:
                    dere_qry_string +=','
                dere_qry_string += str(continent["cq"])
            dere_qry_string +=')'
        
            #construct DX continent region query
            dxre_qry_string = ' AND spotcq IN ('
            for i in range(len(dxre)):
                continent=find_id_json(continents_cq["continents"],dxre[i])
                if i > 0:
                    dxre_qry_string +=','
                dxre_qry_string += str(continent["cq"])
            dxre_qry_string +=')'


            query_string="SELECT rowid, spotter AS de, freq, spotcall AS dx, comment AS comm, time, spotdxcc from dxcluster.spot WHERE 1=1"                                  
            if len(band) > 0:
                query_string += band_qry_string

            if len(mode) > 0:
                query_string += mode_qry_string

            if len(dere) > 0:
                query_string += dere_qry_string

            if len(dxre) > 0:
                query_string += dxre_qry_string
            
            query_string += " ORDER BY rowid desc limit 50;"  

        #connect to db
        db = my.connect(host=cfg['mysql']['host'],
                    user=cfg['mysql']['user'],
                    passwd=cfg['mysql']['passwd'],
                    db=cfg['mysql']['db']
                    )

        cursor = db.cursor()
        number_of_rows = cursor.execute('''SET NAMES 'utf8';''')
        #print ("*** QUERY: "+query_string)   
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
@app.route('/index.html', methods=['GET']) 
def spots():
    payload=spotquery()
    country_data=load_country()
    response=flask.Response(render_template('index.html',mycallsign=cfg['mycallsign'],telnet=cfg['telnet'],mail=cfg['mail'],menu_list=cfg['menu']['menu_list'],payload=payload,timer_interval=cfg['timer']['interval'],country_data=country_data))
    return response

@app.route('/service-worker.js', methods=['GET'])
def sw():
    print ("call service worker")
    return app.send_static_file('service-worker.js')

@app.route('/offline.html')
def root():
        return app.send_static_file('html/offline.html')


@app.route('/plotlist', methods=['GET']) 
def plotlist():
    #get url parameters
    idxfile=os.path.join(app.root_path,os.path.basename(app.static_url_path),'plots','plots.json')
    if os.path.exists(idxfile):
        with open(idxfile,'r') as jsonfile:
            json_content = json.load(jsonfile)
    else:
        json_content={}

    response=json_content
    return response

@app.route('/plots.html')
def plots():
    payload=plotlist()  
    response=flask.Response(render_template('plots.html',mycallsign=cfg['mycallsign'],menu_list=cfg['menu']['menu_list'],payload=payload,timer_interval=cfg['plot_refresh_timer']['interval']))
    return response


@app.route('/cookies.html', methods=['GET'])
def cookies():
    response=flask.Response(render_template('cookies.html',mycallsign=cfg['mycallsign'],menu_list=cfg['menu']['menu_list']))
    return response

@app.route('/sitemap.xml')
def sitemap():
        return app.send_static_file('sitemap.xml')

@app.route('/callsign.html', methods=['GET']) 
def callsign():
    payload=spotquery()  
    country_data=load_country()
    callsign=request.args.get('c')
    response=flask.Response(render_template('callsign.html',mycallsign=cfg['mycallsign'],menu_list=cfg['menu']['menu_list'],payload=payload,country_data=country_data,callsign=callsign))
    return response
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')
