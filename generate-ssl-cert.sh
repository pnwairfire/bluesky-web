#! /usr/bin/env bash

# Generates cert, key, and pem files for monogd server and client
#
# Links:
#  - https://docs.mongodb.com/manual/tutorial/configure-ssl/
#  - https://docs.mongodb.com/manual/tutorial/configure-ssl-clients/
#  - https://stackoverflow.com/questions/10175812/how-to-create-a-self-signed-certificate-with-openssl#10176685

SHOW_HELP=false
ROOT_DIR=false
NAME=false
COUNTRY=false
STATE=false
LOCALITY=false
ORGANIZATION=false
ORGANIZATIONAL_UNIT=false

while [ -n "$1" ]; do # while loop starts
    case "$1" in
    -h) SHOW_HELP=true && shift ;;
    --help) SHOW_HELP=true && shift ;;
    -r) ROOT_DIR="$2" && shift && shift ;;
    --root-dir) ROOT_DIR="$2" && shift && shift ;;
    -n) NAME="$2" && shift && shift ;;
    --name) NAME="$2" && shift && shift ;;
    -c) COUNTRY="$2" && shift && shift ;;
    --country) COUNTRY="$2" && shift && shift ;;
    -s) STATE="$2" && shift && shift ;;
    --state) STATE="$2" && shift && shift ;;
    -l) LOCALITY="$2" && shift && shift ;;
    --locality) LOCALITY="$2" && shift && shift ;;
    -o) ORGANIZATION="$2" && shift && shift ;;
    --organization) ORGANIZATION="$2" && shift && shift ;;
    -u) ORGANIZATIONAL_UNIT="$2" && shift && shift ;;
    --organizational-unit) ORGANIZATIONAL_UNIT="$2" && shift && shift ;;
    *) echo "Option $1 not recognized" && exit 1 ;;
    esac
done

if [ "$SHOW_HELP" = true ] ; then
    echo ""
    echo "Options:"
    echo "   -h/--help                 - print this help message"
    echo "   -r/--root-dir             - e.g. /etc/ssl/"
    echo "   -n/--name                 - 'client', 'mongod', or 'rabbitmq'"
    echo "   -c/--country              - country name"
    echo "   -s/--state                - state or province name"
    echo "   -l/--locality             - locality name (e.g. city)"
    echo "   -o/--organization         - oraninization name (e.g. company)"
    echo "   -u/--organizational-unit  - organizational unit name (e.g. section)"
    echo ""
    echo "Usage:"
    echo "  Dev:"
    echo "    $0 -r ./dev/ssl/ -n client -c US -s WA -l SEATTLE -o ACME -u BlueSkyWeb"
    echo "    $0 -r ./dev/ssl/ -n mongod -c US -s WA -l SEATTLE -o ACME -u BlueSkyWeb"
    echo "    $0 -r ./dev/ssl/ -n rabbitmq -c US -s WA -l SEATTLE -o ACME -u BlueSkyWeb"
    echo ""
    echo "  Production:"
    echo "    $0 -r /etc/ssl/ -n client -c US -s WA -l SEATTLE -o ACME -u BlueSkyWeb"
    echo "    $0 -r /etc/ssl/ -n mongod -c US -s WA -l SEATTLE -o ACME -u BlueSkyWeb"
    echo "    $0 -r /etc/ssl/ -n rabbitmq -c US -s WA -l SEATTLE -o ACME -u BlueSkyWeb"
    echo ""
    echo ""
    exit 0
fi

check_arg () {
    if [ "$1" = false ] ; then
        echo "*ERROR: Specifify $2/$3   (use -h/--help to see usage)"
        exit 1
    fi
}

check_arg $ROOT_DIR -r --root-dir
check_arg $NAME -n --name
check_arg $COUNTRY -c --country
check_arg $STATE -s --state
check_arg $LOCALITY -l --locality
check_arg $ORGANIZATION -o --organization
check_arg $ORGANIZATIONAL_UNIT -u --organizational-unit


# trim trailing slash from root dir
ROOT_DIR=$(echo $ROOT_DIR | sed 's:/*$::')
CERTFILE=$ROOT_DIR/bluesky-web-$NAME-cert.crt
KEYFILE=$ROOT_DIR/bluesky-web-$NAME-cert.key
PEMFILE=$ROOT_DIR/bluesky-web-$NAME.pem
CONFIGFILE=$ROOT_DIR/bluesky-web-$NAME-ssl.ini

mkdir -p $ROOT_DIR

# possibility 3:
cat <<EOT >$CONFIGFILE
[req]
default_bits = 2048
prompt = no
default_md = sha256
x509_extensions = v3_req
distinguished_name = req_distinguished_name

[req_distinguished_name]
C = $COUNTRY
ST = $STATE
L = $LOCALITY
O = $ORGANIZATION
OU = $ORGANIZATIONAL_UNIT
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
