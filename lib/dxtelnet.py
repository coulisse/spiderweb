# *************************************************************************************
# Module used to interface with telnet cluster and get connected nodes
# *************************************************************************************
__author__ = "IU1BOW - Corrado"

import telnetlib3
import asyncio
import struct
import logging

def parse_who(lines):
    lines = lines.splitlines()
    row_headers = ("callsign", "type", "started", "name", "average_rtt", "link")
    payload = []

    for i in range(3, len(lines) - 1):
        line = lines[i].lstrip()
        logging.debug(line)
        line_splitted_by_first_space = line.split(" ", 1)
        first_part = line_splitted_by_first_space[0]
        second_part = line_splitted_by_first_space[1]
        ln = len(second_part)

        try:
            if ln > 32:
                fields = [first_part]  # aggiunge il callsign

                if ln > 45:
                    fieldstruct = struct.Struct("10s 18s 9s 2x 5s")
                else:
                    fieldstruct = struct.Struct("10s 18s 9s")

                parse = fieldstruct.unpack_from
                logging.debug(second_part)
                fields += list(parse(second_part.encode()))  # aggiunge il resto delle informazioni

                for j, item_field in enumerate(fields):
                    try:
                        # Decodifica ogni campo da bytes a str, tranne il primo
                        if isinstance(item_field, bytes):
                            fields[j] = item_field.decode('utf-8').strip()
                        else:
                            fields[j] = item_field.strip()
                    except AttributeError:
                        logging.error(item_field)

                payload.append(dict(zip(row_headers, fields)))

        except Exception as e1:
            logging.error(e1)

    return payload

async def who(host, port, user, password=None):
    logging.debug(f"telnet host: {host}")
    logging.debug(f"telnet port: {port}")
    logging.debug(f"telnet user: {user}")

    WAIT_LOGIN = b"login:"
    WAIT_PASS = b"password:"
    WAIT_FOR = b"dxspider >"

    reader, writer = await telnetlib3.open_connection(host, port, encoding=None)
    res = None

    try:
        await reader.readuntil(WAIT_LOGIN)
        writer.write(user.encode('utf-8') + b'\n')

        if password:
            try:
                await asyncio.wait_for(reader.readuntil(WAIT_PASS), timeout=5)  # Timeout di 5 secondi
                writer.write(password.encode('utf-8') + b'\n')
            except asyncio.TimeoutError:
                logging.error("Timeout waiting for password prompt")
                return ""

        await reader.readuntil(WAIT_FOR)
        logging.debug("Login successful")

        # Send 'who' command and capture the output
        writer.write(b'who\n')
        response = await reader.readuntil(WAIT_FOR)
        res = response
        logging.debug(f"Response to 'who': {res}")

        writer.write(b'exit\n')
        await reader.readuntil(b'\n')
        logging.debug("Executed 'exit' command")

    except EOFError as eof:
        logging.debug("End of buffer reached")
    except Exception as e:
        logging.error(f"could not connect to telnet dxspider host: {e}")
    finally:
        writer.close()
        reader.feed_eof()
        logging.debug("Connection closed")

    if res:
        return parse_who(res.decode('utf-8'))
    else:
        return ""