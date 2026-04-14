import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime

import tornado.log

import blueskyconfig

__all__ = [
    'extractRawDataPngs'
]


def extractRawDataPngs(fires_manager):
    wlconfig = blueskyconfig.get('hysplit_weatherlayers_pwfsl')
    if not wlconfig.get('enabled') or not fires_manager.dispersion:
        return

    try:
        hysplit_output = fires_manager.dispersion['output']

        _extract(hysplit_output, wlconfig['docker_image'])
        _upload_images(fires_manager, hysplit_output, wlconfig['docker_image'])

        metadata = _parse_metadata(hysplit_output)

        metadata.update({
            'aws_region': os.environ.get('AWS_REGION'),
            's3_bucket': os.environ.get('S3_BUCKET'),
            's3_key_prefix': os.path.join(
                os.environ.get('S3_BSP_PREFIX', ''),
                fires_manager.run_id
            ),
        })
        return metadata

    except Exception as e:
        import traceback
        tornado.log.gen_log.error(f"Failed to extract raw pngs: {e}")
        tornado.log.gen_log.error(f"Stack: {traceback.format_exc()}")


def _extract(hysplit_output, docker_image):
    tornado.log.gen_log.info("Extracting data images from hysplit output using weatherlayers")

    do_clean_up = False
    if (not os.path.exists(hysplit_output['directory'])
            and os.path.exists(f"{hysplit_output['directory']}.tar.gz")):
        parent_dir = os.path.dirname(hysplit_output['directory'])
        tornado.log.gen_log.info(
            f"Untarring {hysplit_output['directory']}.tar.gz -> {parent_dir}")
        subprocess.run(
            ['tar', '-xzf', f"{hysplit_output['directory']}.tar.gz", '-C', parent_dir],
            check=True)
        do_clean_up = True

    tornado.log.gen_log.info(
        f"Generating raw data pngs in "
        f"{hysplit_output['directory']}/weather-layers")

    # Need to use sh for docker script, since worker docker container
    # doesn't have bash
    script_content = f"""#!/usr/bin/env sh

    docker run --rm \\
        -v {hysplit_output['directory']}:{hysplit_output['directory']} \\
        {docker_image} bsp process \\
        --output-file-type png --output-file-type geotiff \\
        --conc {hysplit_output['directory']}/{hysplit_output['grid_filename']} \\
        -o {hysplit_output['directory']}/weather-layers
"""

    script_name = os.path.join(hysplit_output['directory'], 'run-docker-weatherlayers-process.sh')
    _run_script(script_content, script_name)

    if do_clean_up:
        tornado.log.gen_log.info(f"Removing {hysplit_output['directory']}")
        shutil.rmtree(hysplit_output['directory'], ignore_errors=True)


def _upload_images(fires_manager, hysplit_output, docker_image):
    tornado.log.gen_log.info("Uploading extracted images to s3")

    script_content = f"""#!/usr/bin/env sh

    docker run --rm \\
        -v {hysplit_output['directory']}:{hysplit_output['directory']} \\
        {docker_image} bsp upload \\
        -k {fires_manager.run_id} \\
        -o {hysplit_output['directory']}/weather-layers
"""

    script_name = os.path.join(hysplit_output['directory'], 'run-docker-weatherlayers-upload.sh')
    _run_script(script_content, script_name)


def _run_script(script_content, script_name):
    tornado.log.gen_log.info(f"Running {script_name}")

    with open(script_name, 'w') as f:
        f.write(script_content)
    os.chmod(script_name, 0o755)

    tornado.log.gen_log.debug("About to call subprocess.run")
    subprocess.run([script_name], check=True)


def _parse_metadata(hysplit_output):
    try:
        file_name = os.path.join(hysplit_output['directory'], fires_manager.run_id)
        with open(file_name) as f:
            data = json.load(f)

        return {
            'init_time_iso': data.get('init_time_iso'),
            'forecast_step': data.get('forecast_step'),
            'num_hours': len(data.get('forecast_hours', [])),
            'variables': data.get('variables'),
        }
    except Exception as e:
        tornado.log.gen_log.error(f"Error reading metadata file from disk: {e}")
        return {}
