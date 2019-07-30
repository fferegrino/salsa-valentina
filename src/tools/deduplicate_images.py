from pathlib import Path
import time

from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES
import click
import logging
import click_log

from glob import glob

from tqdm import tqdm

from tools import get_data_file
import os
import matplotlib.pyplot as plt
import shutil
from PIL import Image

logger = logging.getLogger("deduplicate_images")
click_log.basic_config(logger)


def index_existing_images(ses, existing_path):
    image_paths = list(existing_path.glob('*.jpg'))
    logger.info(f'Will index {len(image_paths)}')
    for image_path in tqdm(image_paths):
        ses.add_image(str(image_path))


@click.command()
@click.argument('es_host', envvar='ES_HOST')
@click.argument('es_port', envvar='ES_PORT', type=click.INT)
@click.argument('es_index', envvar='ES_INDEX')
@click.option('--existing_path', '-ep', type=click.Path(exists=True, file_okay=False), default=None)
@click.option("--dry-run", "-t", default=False, is_flag=True)
@click.option("--quiet", default=False, is_flag=True)
def deduplicate_images(es_host, es_port, es_index, existing_path, dry_run, quiet):
    print(locals())

    if quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    es = Elasticsearch([{'host': es_host, 'port': es_port}])
    ses = SignatureES(es, index=es_index)
    logger.info(f'Connected to Elasticsearch at {es_host}:{es_port}')

    if existing_path:
        existing_path = Path(existing_path)
        index_existing_images(ses, existing_path)
    import pdb; pdb.set_trace()
    pass


if __name__ == "__main__":
    deduplicate_images()
