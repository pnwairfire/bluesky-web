#! /usr/bin/env python3

"""Generates cert, key, and pem files for monogd server and client

Links:
 - https://docs.mongodb.com/manual/tutorial/configure-ssl/
 - https://docs.mongodb.com/manual/tutorial/configure-ssl-clients/
 - https://stackoverflow.com/questions/10175812/how-to-create-a-self-signed-certificate-with-openssl#10176685
"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2018, AirFire, PNW, USFS"

import os
import subprocess
import sys

import afscripting as scripting

# Note: the trailing space seems to be the only way to add an extra trailing line
EPILOG_STR = """
Dev:

  $ {script_name} -d ./dev

Production:

  $ {script_name} -d ./ssl

 """.format(script_name=sys.argv[0])

REQUIRED_ARGS = [
    {
        'short': '-d',
        'long': '--dir',
        'help': 'where to create cert, key, and pem files'
    }
]

OPTIONAL_ARGS = [
]

CONFIG_FILE_TEMPLATE = """
[req]
default_bits = 2048
prompt = no
default_md = sha256
x509_extensions = v3_req
distinguished_name = req_distinguished_name

[req_distinguished_name]
C = US
ST = WA
L = Seattle
O = ORGANIZATION
OU = BlueSkyWeb {client_or_server}
CN = bluesky-web-mongo

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.bluesky-web-mongo
DNS.2 = bluesky-web-mongo
"""

def create_config_file(args, client_or_server):
    contents = CONFIG_FILE_TEMPLATE.format(
        client_or_server=client_or_server.capitalize())
    filename = os.path.join(args.dir, 'mongo-' + client_or_server + '-ssl.ini')
    with open(filename, 'w') as f:
        f.write(contents)

    return filename

def generate(args, client_or_server):
    cmd_args = {
        "certfile": os.path.join(args.dir,
            'mongo-' + client_or_server + '-cert.crt'),
        "keyfile": os.path.join(args.dir,
            'mongo-' + client_or_server + '-cert.key'),
        "pemfile": os.path.join(args.dir,
            'mongo-' + client_or_server + '.pem'),
        "configfile": create_config_file(args, client_or_server)
    }
    # ~10 year cert
    cmd = ("openssl req -newkey rsa:2048 -new -x509 -days 3650 "
        "-nodes -out {certfile} -keyout {keyfile} "
        "-config {configfile}".format(**cmd_args))
    subprocess.run(cmd, shell=True, check=True)

    cmd = ("cat {keyfile} {certfile} > {pemfile}".format(**cmd_args))
    subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    parser, args = scripting.args.parse_args(REQUIRED_ARGS, OPTIONAL_ARGS,
        epilog=EPILOG_STR)

    os.makedirs(args.dir)

    generate(args, 'server')
    generate(args, 'client')
