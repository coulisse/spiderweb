# *************************************************************************************
# Module used to interface with telnet cluster and get connected nodes
# *************************************************************************************
__author__ = "IU1BOW - Corrado"

import telnetlib
import struct
import logging


def parse_who(lines):
    # print(lines.decode('ascii'))

    # create a list o lines and define the structure
    lines = lines.splitlines()
    fmtstring = "2x 9s 10s 18s 9s 8s 15s"
    fieldstruct = struct.Struct(fmtstring)

    row_headers = ("callsign", "type", "started", "name", "average_rtt", "link")

    # skip first lines and last line
    payload = []
    for i in range(3, len(lines) - 1):
        line = lines[i]
        ln = len(line)

        padding = bytes(" " * (struct.calcsize(fmtstring) - ln), "utf-8")
        line = line + padding

        if ln > 10:
            parse = fieldstruct.unpack_from
            fields = list(parse(line))

            for j, item_field in enumerate(fields):
                try:
                    fields[j] = item_field.decode("utf-8").strip()
                except AttributeError:
                    print(item_field)
            payload.append(dict(zip(row_headers, fields)))

    #   payload = json.dumps(payload)

    return payload


def who(host, port, user, password):

    WAIT_FOR = b"dxspider >"
    WAIT_PASS = b"password:"

    TIMEOUT = 1
    res = 0

    try:
        tn = telnetlib.Telnet(host, port, TIMEOUT)
        try:
            tn.read_until(b"login: ", TIMEOUT)
            tn.write(user.encode("ascii") + b"\n")
            #if password:
            tn.read_until(WAIT_PASS, TIMEOUT)
            tn.write(password.encode("ascii") + b"\n")

            res = tn.read_until(WAIT_FOR, TIMEOUT)
            tn.write(b"who\n")
            res = tn.read_until(WAIT_FOR, TIMEOUT)
            tn.write(b"exit\n")

        except EOFError:
            logging.error(
                "could not autenticate to telnet dxspider host: check configuration "
            )
            logging.error(res)
            res = 0
    except:
        logging.error("could not connect to telnet dxspider host: check telnet configuration")
        ret = ""

    if res != 0:
        ret = parse_who(res)
    else:
        ret = ""

    return ret
