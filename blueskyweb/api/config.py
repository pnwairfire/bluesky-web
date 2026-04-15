"""blueskyweb.api.config"""

from fastapi import APIRouter, Request

import blueskyconfig
from . import get_boolean_arg, make_json_response

router = APIRouter()

__all__ = ['router']


@router.get("/api/v{api_version}/config/defaults")
async def config_defaults(api_version: str, request: Request):
    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response(blueskyconfig.ConfigManagerSingleton().config, verbose=verbose)
