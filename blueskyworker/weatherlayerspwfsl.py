import json
import logging
import os
import shutil
import subprocess
import tempfile
from datetime import datetime

import blueskyconfig

logger = logging.getLogger(__name__)

__all__ = [
    'extract_raw_data_pngs'
]


def extract_raw_data_pngs(fires_manager):
    wlconfig = blueskyconfig.get('hysplit_weatherlayers_pwfsl')
    if not wlconfig.get('enabled'):
        logger.debug("Weatherlayers-pwfsl not enabled")
        return

    if not fires_manager.dispersion:
        logger.debug("Missing dispersion output information needed to run weatherlayers-pwfsl")
        return

    try:
        hysplit_output = fires_manager.dispersion['output']

        _extract(hysplit_output, wlconfig['docker_image'])
        _upload_images(fires_manager, hysplit_output, wlconfig['docker_image'])

        metadata = _parse_metadata(hysplit_output)
        s3_vars = _get_s3_env_vars()
        if s3_vars:
            metadata.update({
                'aws_region': s3_vars.get('AWS_REGION'),
                's3_bucket': s3_vars.get('S3_BUCKET'),
                's3_key_prefix': os.path.join(
                    s3_vars.get('S3_BSP_PREFIX', ''),
                    fires_manager.run_id),
                })

        return metadata

    except Exception as e:
        import traceback
        logger.error(f"Failed to extract raw pngs: {e}")
        logger.error(f"Stack: {traceback.format_exc()}")


def _extract(hysplit_output, docker_image):
    logger.info("Extracting data images from hysplit output using weatherlayers")

    do_clean_up = False
    if (not os.path.exists(hysplit_output['directory'])
            and os.path.exists(f"{hysplit_output['directory']}.tar.gz")):
        parent_dir = os.path.dirname(hysplit_output['directory'])
        logger.info(
            f"Untarring {hysplit_output['directory']}.tar.gz -> {parent_dir}")
        subprocess.run(
            ['tar', '-xzf', f"{hysplit_output['directory']}.tar.gz", '-C', parent_dir],
            check=True)
        do_clean_up = True

    logger.info(
        f"Generating raw data pngs in "
        f"{hysplit_output['directory']}/weatherlayers")

    # Need to use sh for docker script, since worker docker container
    # doesn't have bash
    script_content = f"""#!/usr/bin/env sh

    docker run --rm \\
        -v {hysplit_output['directory']}:{hysplit_output['directory']} \\
        {docker_image} bsp process \\
        --output-file-type png --output-file-type geotiff \\
        --conc {hysplit_output['directory']}/{hysplit_output['grid_filename']} \\
        -o {hysplit_output['directory']}/weatherlayers
"""

    script_name = os.path.join(hysplit_output['directory'], 'run-docker-weatherlayers-process.sh')
    _run_script(script_content, script_name)

    if do_clean_up:
        logger.info(f"Removing {hysplit_output['directory']}")
        shutil.rmtree(hysplit_output['directory'], ignore_errors=True)


def _upload_images(fires_manager, hysplit_output, docker_image):
    logger.info("Uploading extracted images to s3")

    script_content = f"""#!/usr/bin/env sh

    docker run --rm \\
        -v {hysplit_output['directory']}:{hysplit_output['directory']} \\
        {docker_image} bsp upload \\
        -k {fires_manager.run_id} \\
        -o {hysplit_output['directory']}/weatherlayers
"""

    script_name = os.path.join(hysplit_output['directory'], 'run-docker-weatherlayers-upload.sh')
    _run_script(script_content, script_name)


def _run_script(script_content, script_name):
    logger.info(f"Running {script_name}")

    with open(script_name, 'w') as f:
        f.write(script_content)
    os.chmod(script_name, 0o755)

    logger.debug("About to call subprocess.run")
    subprocess.run([script_name], check=True)


def _parse_metadata(hysplit_output):
    try:
        file_name = os.path.join(hysplit_output['directory'], 'weatherlayers', 'metadata.json')
        with open(file_name) as f:
            data = json.load(f)

        return {
            'init_time_iso': data.get('init_time_iso'),
            'forecast_step': data.get('forecast_step'),
            'num_hours': len(data.get('forecast_hours', [])),
            'variables': data.get('variables'),
        }
    except Exception as e:
        logger.error(f"Error reading metadata file from disk: {e}")
        return {}

def _get_s3_env_vars():
    # Run the command and capture stdout
    # shell=True is used if your command relies on shell features (like pipes or redirects)
    command = 'docker run --rm --entrypoint "/bin/sh" weatherlayers-pwfsl -c "cat /app/.env"'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)

    env_dict = {}
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Split only on the first '=' to handle values that contain '='
            if '=' in line:
                key, value = line.split('=', 1)
                # Optional: strip quotes if your .env file uses them
                env_dict[key.strip()] = value.strip().strip('"').strip("'")

    return env_dict
