# BlueSky Web APIs

The API docs are divided into four categories:

 - [Met reladed APIs](API-MET.md)
 - [Fuelbeds & Emissions APIs](API-RUNS-REALTIME.md)
 - [Plumerise & Dispersion APIs](API-RUNS-ASYNC.md)
 - [Run Status & Output APIs](API-RUNS-STATUS-OUTPUT.md)

In each of the docs linked to above, API urls contain the env
var `$BLUESKY_API_ROOT_URL`. `$BLUESKY_API_ROOT_URL` would be
something like 'http://localhost:8887/bluesky-web' in development or
'https://www.blueskywebhost.com/bluesky-web' in production.  In bash,
you can set it in a terminal session with:

    export BLUESKY_API_ROOT_URL=https://www.blueskywebhost.com/bluesky-web
