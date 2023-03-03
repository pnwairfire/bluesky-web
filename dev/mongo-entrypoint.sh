#!/usr/bin/env bash
echo "Creating mongo users..."
mongo --ssl --sslPEMKeyFile /etc/ssl/bluesky-web-mongod.pem  \
    --sslAllowInvalidHostnames --sslAllowInvalidCertificates  \
    blueskyweb --authenticationDatabase admin --host localhost \
    -u blueskywebadmin -p blueskywebmongopasswordadmin \
    --eval "db.createUser({user: 'blueskyweb', pwd: 'blueskywebmongopassword', roles: [{role: 'readWrite', db: 'blueskyweb'}]});"
echo "Mongo users created."
