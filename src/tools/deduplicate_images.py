import logging
import os
import shutil
import tempfile
import uuid
from collections import defaultdict
from pathlib import Path

import click
import click_log
import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES
from matplotlib.patches import Rectangle
from PIL import Image
from tqdm import tqdm

logger = logging.getLogger("deduplicate_images")
click_log.basic_config(logger)


def attach_tqdm(items, quiet):
    if not quiet:
        yield from tqdm(items)
    else:
        yield from items


def index_existing_images(ses, image_paths):
    for image_path in image_paths:
        ses.add_image(str(image_path))


def find_to_keep(results, thresholds):
    paths = []
    for path, result_list in results.items():
        path = Path(path)
        if not result_list:
            paths.append(path)
        else:
            for r in result_list:
                if r[1] < thresholds:
                    break
                else:
                    paths.append(path)
                    break
    return list(paths)


def move_images(destination, images):
    for image in images:
        destination_path = Path(destination, image.name)
        shutil.move(str(image), str(destination_path))


def query_images(ses, image_paths, max_results=5):
    query_results = defaultdict(list)
    for image_path in image_paths:
        results = ses.search_image(str(image_path))
        logger.debug(f"Query {str(image_path)}, results: {len(results)}")
        filtered = []
        for i, r in enumerate(sorted(results, key=lambda res: res["dist"])):
            if i >= max_results:
                break
            filtered.append((r["path"], r["dist"]))

        query_results[str(image_path)] = filtered
    return query_results


def preprocess_images(image_paths, tempdir, new_size=(500, 500)):
    new_paths = []
    for image_path in image_paths:
        new_image_path = Path(tempdir, f"{uuid.uuid4()}.jpg")
        im = Image.open(image_path)
        if im.mode == "RGBA":
            im = im.convert("RGB")
        resized_im = im.resize(new_size, Image.ANTIALIAS)
        resized_im.save(new_image_path, "JPEG", optimize=True)
        new_paths.append(new_image_path)
    return new_paths


def show_images(results_, count, max_results=5, imgsize=15):
    to_show = min(len(results_), count)

    f, ax = plt.subplots(
        to_show,
        1 + max_results,
        figsize=(imgsize * to_show, (1 + max_results) * imgsize),
    )

    for i, (query_path, results) in enumerate(results_.items()):
        if i >= to_show:
            break

        im = plt.imread(query_path)
        ax[i][0].imshow(im)
        for j, (path, distance) in enumerate(results):
            im = plt.imread(path)
            rectangle = Rectangle(
                (0, 0), 0.2 * im.shape[0], 0.1 * im.shape[1], fill="black"
            )
            ax[i, j + 1].imshow(im)
            ax[i, j + 1].add_patch(rectangle)
            ax[i, j + 1].text(5, 40, f"{distance:.2f}", color="white")

    for i in range(to_show):
        for j in range(max_results + 1):
            ax[i][j].axis("off")

    plt.tight_layout()
    plt.show()


@click.command()
@click.argument("es_host", envvar="ES_HOST")
@click.argument("es_port", envvar="ES_PORT", type=click.INT)
@click.argument("es_index", envvar="ES_INDEX")
@click.argument("new_path", type=click.Path(exists=True, file_okay=False))
@click.argument("staging_path", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--existing_path",
    "-ep",
    type=click.Path(exists=True, file_okay=False),
    default=None,
)
@click.option("--example-count", type=click.INT, default=5)
@click.option("--quiet", default=False, is_flag=True)
def deduplicate_images(
    es_host,
    es_port,
    es_index,
    new_path,
    staging_path,
    existing_path,
    example_count,
    quiet,
):
    if quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    es = Elasticsearch([{"host": es_host, "port": es_port}])
    ses = SignatureES(es, index=es_index)
    temp_dir = tempfile.mkdtemp("salsa-valentina")
    logger.info(f"Connected to Elasticsearch at {es_host}:{es_port}")

    if existing_path:
        existing_path = Path(existing_path)
        image_paths = list(existing_path.glob("*.jpg"))
        logger.info(f"Will index {len(image_paths)} images")
        index_existing_images(ses, attach_tqdm(image_paths, quiet))
        logger.info(f"Done indexing existing images")

    staging_path = Path(staging_path)
    new_path = Path(new_path)
    image_paths = list(new_path.glob("*.*"))

    logger.info(f"Will process {len(image_paths)}")
    new_paths = preprocess_images(attach_tqdm(image_paths, quiet), temp_dir)
    logger.info(f"Ended with {len(new_paths)}")

    logger.info(f"Will try to add {len(new_paths)} new images")
    similarity_results = query_images(ses, attach_tqdm(new_paths, quiet))
    logger.info(f"Done performing queries existing images")

    click.echo(
        "View the images and if you are ok with the results, press Q to close the window and continue"
    )
    show_images(similarity_results, example_count)

    threshold = click.prompt(
        "Please input a distance threshold between (0-1], Any other value will abort the program",
        confirmation_prompt=True,
        default=-1,
        type=float,
    )
    try:
        threshold = float(threshold)
        if 0.0 > threshold or threshold > 1.0:
            raise ValueError(
                f"The selected threshold ({threshold}) is not between 0.0 and 1.0"
            )
    except ValueError:
        logger.error("Error with the selected threshold")

    images_to_keep = find_to_keep(similarity_results, threshold)
    logger.info(f"Moving images {len(images_to_keep)}")
    move_images(staging_path, images_to_keep)

    logger.info("Cleanup")
    shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    deduplicate_images()
