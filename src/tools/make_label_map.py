import json
import logging
from pathlib import Path

import click
import click_log
from tools.files import create_folder
from tools.utils import generate_label_map

logger = logging.getLogger("make_label_map")
click_log.basic_config(logger)


@click.command()
@click.argument("input_path", type=click.Path(exists=True, file_okay=False))
@click.argument("output_path", type=click.Path(file_okay=False))
@click.option("--dry-run", "-t", default=False, is_flag=True)
@click.option("--quiet", default=False, is_flag=True)
def make_label_map(input_path, output_path, dry_run, quiet):
    if quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    input_path = Path(input_path)
    output_path = Path(output_path)
    label_map_path = Path(output_path, "label_map.pbtxt")

    train_path = Path(input_path, "train.csv")
    test_path = Path(input_path, "test.csv")
    labels_path = Path(input_path, "labels.json")

    for path in [train_path, test_path, labels_path]:
        if not path.exists():
            logger.error(f"The file {path} does not exist")

    with open(labels_path) as readable:
        label_map = json.load(readable)

    create_folder(output_path, dry_run, logger)

    logger.info(f"Will generate records using {label_map}")

    if not dry_run:
        string_label_map = generate_label_map(label_map)
        with open(label_map_path, "w") as writable:
            writable.write(string_label_map)
        logger.info(f"Written to {label_map_path}")
    else:
        logger.info(f"Would have written to {label_map_path}")


if __name__ == "__main__":
    make_label_map()
