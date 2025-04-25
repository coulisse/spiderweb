import telnetlib3
import asyncio
import struct
import logging
import re  

def parse_who(lines):
    lines = lines.splitlines()
    logging.debug(f"Response to 'who': {lines}")
    row_headers = ("callsign", "type", "state", "started", "name", "average_rtt", "link")
    payload = []

    filler =  " " * 50
    # Skip the first line (header) and the last line (prompt)
    for i in range(1, len(lines) - 1):
        line = lines[i].lstrip()
        
        # Skip the header line if it exists
        if line.startswith("Callsign"):
            continue  # Skip this line

        logging.debug(f"line ({i}): {line}")
        line_parts = line.split(" ", 1)
        first_part = line_parts[0]
        second_part = line_parts[1]
        ln = len(second_part)

        try:
            if ln > 32:
                fields = [first_part]
                second_part += filler
                fieldstruct = struct.Struct("10s 8s 18s 11s 2x 5s")
                fields += list(fieldstruct.unpack_from(second_part.encode()))
                fields = [f.decode('utf-8').strip() if isinstance(f, bytes) else f.strip() for f in fields]  
                payload.append(dict(zip(row_headers, fields)))
        except Exception as e1:
            logging.error(e1)
    return payload

async def fetch_who_and_version(host, port, user, password=None):
    logging.debug(f"Connecting to {host}:{port} for WHO and SH/VERSION")
    WAIT_LOGIN = b"login:"
    WAIT_PASS = b"password:"
    WAIT_FOR = b"dxspider >"

    reader, writer = await telnetlib3.open_connection(host, port, encoding=None)
    who_data = ""
    version_info = "Unknown"

    try:
        await reader.readuntil(WAIT_LOGIN)
        writer.write(user.encode('utf-8') + b'\n')
        if password:
            try:
                await asyncio.wait_for(reader.readuntil(WAIT_PASS), timeout=5)
                writer.write(password.encode('utf-8') + b'\n')
            except asyncio.TimeoutError:
                logging.error("Timeout waiting for password prompt")
                return [], "Login timeout"

        await reader.readuntil(WAIT_FOR)
        logging.debug("Login successful")

        writer.write(b'who\n')
        who_response = await reader.readuntil(WAIT_FOR)
        who_data = who_response.decode('utf-8')

        writer.write(b'sh/version\n')
        version_response = await reader.readuntil(WAIT_FOR)
        res = version_response.decode('utf-8').strip().splitlines()
        logging.debug(f"Full SH/VERSION Response:\n{res}")

        for line in res:
            logging.debug(f"Processing Line: {line}")
            match = re.search(r"DXSpider v([\d.]+) \(build (\d+)", line)
            if match:
                version_info = f"DXSpider v{match.group(1)} build {match.group(2)}"
                logging.debug(f"Extracted DXSpider Version: {version_info}")
                break  
        else:
            logging.debug("No valid DXSpider version found in the response.")

    except EOFError:
        logging.error("End of buffer reached unexpectedly")
    except Exception as e:
        logging.error(f"Error retrieving WHO and version info: {e}")
    finally:
        writer.close()
        reader.feed_eof()
        logging.debug("Connection closed")

    return parse_who(who_data), version_info
