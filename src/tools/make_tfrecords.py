import io
import json
import logging
from collections import namedtuple
from pathlib import Path

import click
import click_log
import pandas as pd
import tensorflow as tf
from object_detection.utils import dataset_util
from PIL import Image
from tools.files import create_folder

logger = logging.getLogger("make_tfrecords")
click_log.basic_config(logger)


def split(df, group):
    data = namedtuple("data", ["filename", "frame"])
    gb = df.groupby(group)
    return [
        data(filename, gb.get_group(x))
        for filename, x in zip(gb.groups.keys(), gb.groups)
    ]


def create_tf_example(group, label_map):
    with tf.gfile.GFile(group.filename, "rb") as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode("utf8")
    image_format = b"jpg"
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.frame.iterrows():
        xmins.append(row["xmin"] / width)
        xmaxs.append(row["xmax"] / width)
        ymins.append(row["ymin"] / height)
        ymaxs.append(row["ymax"] / height)
        classes_text.append(row["class"].encode("utf8"))
        classes.append(label_map[row["class"]])

    tf_example = tf.train.Example(
        features=tf.train.Features(
            feature={
                "image/height": dataset_util.int64_feature(height),
                "image/width": dataset_util.int64_feature(width),
                "image/filename": dataset_util.bytes_feature(filename),
                "image/source_id": dataset_util.bytes_feature(filename),
                "image/encoded": dataset_util.bytes_feature(encoded_jpg),
                "image/format": dataset_util.bytes_feature(image_format),
                "image/object/bbox/xmin": dataset_util.float_list_feature(xmins),
                "image/object/bbox/xmax": dataset_util.float_list_feature(xmaxs),
                "image/object/bbox/ymin": dataset_util.float_list_feature(ymins),
                "image/object/bbox/ymax": dataset_util.float_list_feature(ymaxs),
                "image/object/class/text": dataset_util.bytes_list_feature(
                    classes_text
                ),
                "image/object/class/label": dataset_util.int64_list_feature(classes),
            }
        )
    )

    return tf_example


def write_tfrecords(input_frame, output_file, label_map):
    writer = tf.python_io.TFRecordWriter(str(output_file))
    examples = input_frame
    grouped = split(examples, "filename")
    for group in grouped:
        tf_example = create_tf_example(group, label_map)
        writer.write(tf_example.SerializeToString())


@click.command()
@click.argument("input_path", type=click.Path(exists=True, file_okay=False))
@click.argument("output_path", type=click.Path(file_okay=False))
@click.option("--dry-run", "-t", default=False, is_flag=True)
@click.option("--quiet", default=False, is_flag=True)
def make_tfrecord(input_path, output_path, dry_run, quiet):
    if quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    input_path = Path(input_path)
    output_path = Path(output_path)

    train_path = Path(input_path, "train.csv")
    test_path = Path(input_path, "test.csv")
    labels_path = Path(input_path, "labels.json")

    for path in [train_path, test_path, labels_path]:
        if not path.exists():
            logger.error(f"The file {path} does not exist")

    with open(labels_path) as readable:
        label_map = json.load(readable)

    logger.info(f"Will generate records using {label_map}")

    create_folder(output_path, dry_run, logger)
    output_train = Path(output_path, "train.tfrecord")
    output_test = Path(output_path, "test.tfrecord")

    train_frame = pd.read_csv(train_path, index_col=0)
    test_frame = pd.read_csv(test_path, index_col=0)

    if not dry_run:
        write_tfrecords(train_frame, output_train, label_map)
        write_tfrecords(test_frame, output_test, label_map)
        logger.info(f"Written to {output_train} and {output_test}")
    else:
        logger.info(f"Would have written to {output_train} and {output_test}")


if __name__ == "__main__":
    make_tfrecord()
