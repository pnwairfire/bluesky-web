# BlueSky-Web Admin

## Dev Setup

create file `.env` defining `PUBLIC_API_URL`, `PUBLIC_STATS_RUNID_OPTIONS`, e.g.

    PUBLIC_API_URL=http://web1/bluesky-web/api/v4.2`
    PUBLIC_STATS_RUNID_OPTIONS={"emissions":"Emissions","dispersion":"Dispersion"}

## Running outside of docker

    cd pnwairfire-bluesky-web/blueskyadmin
    ./run-no-docker

## Running in docker

See [README](../README.md) in repo root.
