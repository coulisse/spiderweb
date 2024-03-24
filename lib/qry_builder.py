# find id  in json : ie frequency / continent
def find_id_json(json_object, name):
    return [obj for obj in json_object if obj["id"] == name][0]

def query_build_callsign(logger,callsign):

    query_string = ""
    if len(callsign) <= 14:
        query_string = (
            "(SELECT rowid, spotter AS de, freq, spotcall AS dx, comment AS comm, time, spotdxcc from spot WHERE spotter='"
            + callsign
            + "'"
        )
        query_string += " ORDER BY rowid desc limit 10)"
        query_string += " UNION "
        query_string += (
            "(SELECT rowid, spotter AS de, freq, spotcall AS dx, comment AS comm, time, spotdxcc from spot WHERE spotcall='"
            + callsign
            + "'"
        )
        query_string += " ORDER BY rowid desc limit 10);"
    else:
        logger.warning("callsign too long")
    return query_string


def query_build(logger,parameters,band_frequencies,modes_frequencies,continents_cq,enable_cq_filter):

    try:
        last_rowid = str(parameters["lr"])  # Last rowid fetched by front end

        get_param = lambda parameters, parm_name: parameters[parm_name] if (parm_name in parameters) else []
        dxcalls=get_param(parameters, "dxcalls")  
        band=get_param(parameters, "band")        
        dere=get_param(parameters, "de_re")  
        dxre=get_param(parameters, "dx_re")  
        mode=get_param(parameters, "mode")
        exclft8=get_param(parameters, "exclft8")
        exclft4=get_param(parameters, "exclft4")   
        
        decq = []
        if "cqdeInput" in parameters:
            decq[0] = parameters["cqdeInput"] 

        dxcq = []
        if "cqdxInput" in parameters:   
            dxcq[0] = parameters["cqdxInput"] 

        query_string = ""

        #construct  callsign of spot dx callsign 
        dxcalls_qry_string = " AND spotcall IN (" + ''.join(map(lambda x: "'" + x + "'," if x != dxcalls[-1] else "'" + x + "'", dxcalls)) + ")"
        # construct band query decoding frequencies with json file
        band_qry_string = " AND (("
        for i, item_band in enumerate(band):
            freq = find_id_json(band_frequencies["bands"], item_band)
            if i > 0:
                band_qry_string += ") OR ("

            band_qry_string += (
                "freq BETWEEN " + str(freq["min"]) + " AND " + str(freq["max"])
            )

        band_qry_string += "))"
        # construct mode query
        mode_qry_string = " AND  (("
        for i, item_mode in enumerate(mode):
            single_mode = find_id_json(modes_frequencies["modes"], item_mode)
            if i > 0:
                mode_qry_string += ") OR ("
            for j in range(len(single_mode["freq"])):
                if j > 0:
                    mode_qry_string += ") OR ("
                mode_qry_string += (
                    "freq BETWEEN "
                    + str(single_mode["freq"][j]["min"])
                    + " AND "
                    + str(single_mode["freq"][j]["max"])
                )

        mode_qry_string += "))"

        #Exluding FT8 or FT4 connection
        ft8_qry_string = " AND ("
        if exclft8:
            ft8_qry_string += "(comment NOT LIKE '%FT8%')"
            single_mode = find_id_json(modes_frequencies["modes"], "digi-ft8")
            for j in range(len(single_mode["freq"])):
                ft8_qry_string += (
                    " AND (freq NOT BETWEEN "
                    + str(single_mode["freq"][j]["min"])
                    + " AND "
                    + str(single_mode["freq"][j]["max"])
                    + ")"
                )
        ft8_qry_string += ")" 

        ft4_qry_string = " AND ("
        if exclft4:
            ft4_qry_string += "(comment NOT LIKE '%FT4%')"
            single_mode = find_id_json(modes_frequencies["modes"], "digi-ft4")
            for j in range(len(single_mode["freq"])):
                ft4_qry_string += (
                    " AND (freq NOT BETWEEN "
                    + str(single_mode["freq"][j]["min"])
                    + " AND "
                    + str(single_mode["freq"][j]["max"])
                    + ")"
                )
        ft4_qry_string += ")" 

        # construct DE continent region query
        dere_qry_string = " AND spottercq IN ("
        for i, item_dere in enumerate(dere):
            continent = find_id_json(continents_cq["continents"], item_dere)
            if i > 0:
                dere_qry_string += ","
            dere_qry_string += str(continent["cq"])
        dere_qry_string += ")"

        # construct DX continent region query
        dxre_qry_string = " AND spotcq IN ("
        for i, item_dxre in enumerate(dxre):
            continent = find_id_json(continents_cq["continents"], item_dxre)
            if i > 0:
                dxre_qry_string += ","
            dxre_qry_string += str(continent["cq"])
        dxre_qry_string += ")"

        if enable_cq_filter == "Y":
            # construct de cq query
            decq_qry_string = ""
            if len(decq) == 1:
                if decq[0].isnumeric():
                    decq_qry_string = " AND spottercq =" + decq[0]
            # construct dx cq query
            dxcq_qry_string = ""
            if len(dxcq) == 1:
                if dxcq[0].isnumeric():
                    dxcq_qry_string = " AND spotcq =" + dxcq[0]

        if last_rowid is None:
            last_rowid = "0"
        if not last_rowid.isnumeric():
            last_rowid = 0

        query_string = "SELECT rowid, spotter AS de, freq, spotcall AS dx, comment AS comm, time, spotdxcc from spot WHERE rowid > "+(str(last_rowid))
        

        if dxcalls:
            query_string += dxcalls_qry_string

        if len(band) > 0:
            query_string += band_qry_string

        if len(mode) > 0:
            query_string += mode_qry_string

        if exclft8:
            query_string += ft8_qry_string

        if exclft4:
            query_string += ft4_qry_string

        if len(dere) > 0:
            query_string += dere_qry_string

        if len(dxre) > 0:
            query_string += dxre_qry_string

        if enable_cq_filter == "Y":
            if len(decq_qry_string) > 0:
                query_string += decq_qry_string

            if len(dxcq_qry_string) > 0:
                query_string += dxcq_qry_string

        query_string += " ORDER BY rowid desc limit 50;"

        logger.debug (query_string)

    except Exception as e:
        logger.error(e)
        query_string = ""

    return query_string


query_build_callsing_list = lambda: 'SELECT spotcall AS dx FROM (select spotcall from spot  order by rowid desc limit 50000) s1  GROUP BY spotcall ORDER BY count(spotcall) DESC, spotcall LIMIT 100;'