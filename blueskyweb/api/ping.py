"""blueskyweb.api.ping"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2015, AirFire, PNW, USFS"

from fastapi import APIRouter
from bluesky import __version__

router = APIRouter()

__all__ = ['router']


@router.get("/api/ping")
@router.get("/api/ping/")
async def ping():
    # TODO: return anything else?
    return {"msg": "pong", "blueskyVersion": __version__}
