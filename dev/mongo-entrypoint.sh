#!/usr/bin/env bash
echo "Creating mongo users..."
mongosh --tls --tlsCertificateKeyFile /etc/ssl/bluesky-web-mongod.pem  \
    --tlsAllowInvalidHostnames --tlsAllowInvalidCertificates  \
    blueskyweb --authenticationDatabase admin --host localhost \
    -u blueskywebadmin -p blueskywebmongopasswordadmin \
    --eval "db.createUser({user: 'blueskyweb', pwd: 'blueskywebmongopassword', roles: [{role: 'readWrite', db: 'blueskyweb'}]});"
echo "Mongo users created."
