To upgrade mongo, you must successively upgrade major releases.  This repo
initially used mongo v3.4.6.  Depending on when you started bluesky-web,
you'll need to use the code at varying points in the commit history
in order to use the latest version.

# Mongo 3.4.6 -> 3.6.23

Just check out a version of the code when it was using 3.6.23

    git checkout mongo-3.6.23


# Mongo 3.6.23 -> 4.0.28

This is a little more involved.  First, check the 'featureCompatibilityVersion'

    docker exec -ti bluesky-web-mongo \
        mongo -u blueskywebadmin -p blueskywebmongopasswordadmin --ssl \
        --sslCAFile /etc/ssl/bluesky-web-mongod.pem \
        --sslAllowInvalidHostnames --sslAllowInvalidCertificates \
        blueskyweb --authenticationDatabase admin --eval 'db.adminCommand( { getParameter: 1, featureCompatibilityVersion: 1 } )'

if it's not 3.6, set it to 3.6:

    docker exec -ti bluesky-web-mongo \
        mongo -u blueskywebadmin -p blueskywebmongopasswordadmin --ssl \
        --sslCAFile /etc/ssl/bluesky-web-mongod.pem \
        --sslAllowInvalidHostnames --sslAllowInvalidCertificates \
        blueskyweb --authenticationDatabase admin --eval 'db.adminCommand( { setFeatureCompatibilityVersion: "3.6" } )'

Now, you can check out a version of the code using 4.0.28

    git checkout mongo-4.0.28


# Mongo 4.0.28 -> 4.2.24

Like the upgrade to 4.0.28, we need to set setFeatureCompatibilityVersion,
this time to 4.0

    docker exec -ti bluesky-web-mongo \
        mongo -u blueskywebadmin -p blueskywebmongopasswordadmin --ssl \
        --sslCAFile /etc/ssl/bluesky-web-mongod.pem \
        --sslAllowInvalidHostnames --sslAllowInvalidCertificates \
        blueskyweb --authenticationDatabase admin --eval 'db.adminCommand( { setFeatureCompatibilityVersion: "4.0" } )'

Now, you can check out a version of the code using 4.2.24

    git checkout mongo-4.2.24

# Mongo 4.2.24 -> 4.4.18

Again, first set setFeatureCompatibilityVersion, this time to 4.2

    docker exec -ti bluesky-web-mongo \
        mongo -u blueskywebadmin -p blueskywebmongopasswordadmin --ssl \
        --sslCAFile /etc/ssl/bluesky-web-mongod.pem \
        --sslAllowInvalidHostnames --sslAllowInvalidCertificates \
        blueskyweb --authenticationDatabase admin --eval 'db.adminCommand( { setFeatureCompatibilityVersion: "4.2" } )'

Now, check out a version of the code using 4.4.18

    git checkout mongo-4.4.18

# Mongo 4.4.18 -> 5.0.15

Again, first set setFeatureCompatibilityVersion, this time to 4.4

    docker exec -ti bluesky-web-mongo \
        mongo -u blueskywebadmin -p blueskywebmongopasswordadmin --ssl \
        --sslCAFile /etc/ssl/bluesky-web-mongod.pem \
        --sslAllowInvalidHostnames --sslAllowInvalidCertificates \
        blueskyweb --authenticationDatabase admin --eval 'db.adminCommand( { setFeatureCompatibilityVersion: "4.4" } )'

Now, check out a version of the code using 5.0.15

    git checkout mongo-5.0.15

# Mongo 5.0.15 -> 6.0.4

Again, first set setFeatureCompatibilityVersion, this time to 5.0

    docker exec -ti bluesky-web-mongo \
        mongo -u blueskywebadmin -p blueskywebmongopasswordadmin --tls \
        --tlsCAFile /etc/ssl/bluesky-web-mongod.pem \
        --tlsAllowInvalidHostnames --tlsAllowInvalidCertificates \
        blueskyweb --authenticationDatabase admin --eval 'db.adminCommand( { setFeatureCompatibilityVersion: "5.0" } )'

Now, check out a version of the code using 6.0.4

    git checkout mongo-6.0.4

# Mongo 6.0.4 -> 6.0.11

Note that the mongo shell `mongo` is replaced by `mongosh` in the
following command, since it was removed in 6.0.

However, nothing else is needed to upgrade from 6.0.4 to 6.0.11.
