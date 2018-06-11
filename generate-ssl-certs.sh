#! /usr/bin/env bash

# Generates cert, key, and pem files for monogd server and client
#
# Links:
#  - https://docs.mongodb.com/manual/tutorial/configure-ssl/
#  - https://docs.mongodb.com/manual/tutorial/configure-ssl-clients/
#  - https://stackoverflow.com/questions/10175812/how-to-create-a-self-signed-certificate-with-openssl#10176685

if [ $# -lt 2 ] || [ $# -gt 3 ]
  then
    echo "Dev:"
    echo "   $0 ./dev/ssl/ client"
    echo "   $0 ./dev/ssl/ mongod"
    echo "   $0 ./dev/ssl/ rabbitmq"
    echo ""
    echo "Production:"
    echo "   $0 /etc/ssl/ client"
    echo "   $0 /etc/ssl/ mongod"
    echo "   $0 /etc/ssl/ rabbitmq"
    echo ""
    exit 1
fi

# trim trailing slash from root dir
ROOT_DIR=$(echo $1 | sed 's:/*$::')
NAME=$2
CERTFILE=$ROOT_DIR/bluesky-web-$NAME-cert.crt
KEYFILE=$ROOT_DIR/bluesky-web-$NAME-cert.key
PEMFILE=$ROOT_DIR/bluesky-web-$NAME.pem
CONFIGFILE=$ROOT_DIR/bluesky-web-$NAME-ssl.ini

mkdir -p $ROOT_DIR

# possibility 3:
cat <<EOT >>$CONFIGFILE
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
OU = BlueSkyWeb $NAME
CN = bluesky-web-$NAME

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.bluesky-web-$NAME
DNS.2 = bluesky-web-$NAME
EOT


# ~10 year cert
openssl req -newkey rsa:2048 -new -x509 -days 3650 \
    -nodes -out $CERTFILE -keyout $KEYFILE \
    -config $CONFIGFILE

cat $KEYFILE $CERTFILE > $PEMFILE
