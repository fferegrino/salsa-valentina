import json
import logging
import sys
from pathlib import Path

import click
import click_log
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

from tools.files import create_folder
from tools.utils import relative2absolute

logger = logging.getLogger('split_train_test')
click_log.basic_config(logger)


def txt_to_frame(txt, headers=False):
    df = pd.read_csv(txt, sep=' ', header=None)
    if headers:
        df.columns = ['class', 'cx', 'cy', 'width', 'height']
    return df


def annotation_to_frame(images_path, annotations, classes, ids_to_keep):
    in_collection = []
    for annotation_file in annotations:
        image_path = Path(images_path, f'{annotation_file.stem}.jpg')
        im = Image.open(image_path)
        values = []
        for i, row in txt_to_frame(annotation_file, headers=True).iterrows():
            class_id = row['class']
            if class_id in ids_to_keep:
                x, y, w, h = relative2absolute(row['cx'], row['cy'], row['width'], row['height'],
                                               img_w=im.size[0], img_h=im.size[1])

                values.append([str(image_path), classes[class_id], w, h, x, y, x + w, y + h])
        in_collection.extend(values)
    labels = pd.DataFrame(in_collection,
                          columns=['filename', 'class', 'width', 'height', 'xmin', 'ymin', 'xmax', 'ymax'])
    return labels


@click.command()
@click.argument('annotations_path', type=click.Path(exists=True, file_okay=False))
@click.argument('images_path', type=click.Path(exists=True, file_okay=False))
@click.argument('output_path', type=click.Path(exists=False, file_okay=False))
@click.option('--class', '-c', 'class_', multiple=True, type=click.STRING)
@click.option('--random-state', '-r', type=click.INT)
@click.option('--test-size', '-t', type=click.FLOAT, default=0.25)
@click.option('--dry-run', '-t', default=False, is_flag=True)
@click.option('--quiet', default=False, is_flag=True)
def split_train_test(annotations_path, images_path, output_path, class_, random_state, test_size, dry_run, quiet):
    if quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    if not class_:
        logger.error('Must specify at least one class')
        sys.exit(-1)

    logger.info(
        f'Making train/test split with: random_state={random_state}, '
        f'test_size={test_size:f}, classes=\"{", ".join(class_)}\"')

    output_path = Path(output_path)
    create_folder(output_path, dry_run, logger)

    classes_to_keep = set(class_)
    class_labels = {label: idx for idx, label in enumerate(sorted(class_))}

    classes_path = Path(annotations_path, 'classes.txt')
    with open(classes_path) as readable:
        classes = {i: tag.strip() for i, tag in enumerate(readable)}
        rev_class = {v: k for k, v in classes.items()}
    ids_to_keep = set([rev_class[k] for k in classes_to_keep])

    annotation_files = [annotation for annotation in Path(annotations_path).glob('[!classes]*.txt')]
    filtered_annotations = []
    for annotation_file in annotation_files:
        annotation = txt_to_frame(annotation_file)
        classes_in_image = set(annotation[0].values)
        intersection = classes_in_image.intersection(ids_to_keep)
        if intersection:
            filtered_annotations.append(annotation_file)

    logger.info(f'Original file count: {len(annotation_files)}. '
                f'Filtered file count: {len(filtered_annotations)}.')

    train_annotations, test_annotations = train_test_split(filtered_annotations, random_state=random_state,
                                                           test_size=test_size)
    logger.info(f'Train file count: {len(train_annotations)}. '
                f'Test file count: {len(test_annotations)}')

    train_frame = annotation_to_frame(images_path, train_annotations, classes, ids_to_keep)
    test_frame = annotation_to_frame(images_path, test_annotations, classes, ids_to_keep)

    train_summary = train_frame.groupby('class')['class'].count().to_dict()

    test_summary = test_frame.groupby('class')['class'].count().to_dict()

    logger.info(f'Train summary: {train_summary}')
    logger.info(f'Test summary: {test_summary}')

    train_file_path = Path(output_path, 'train.csv')
    test_file_path = Path(output_path, 'test.csv')
    class_output_path = Path(output_path, 'labels.json')

    if not dry_run:
        train_frame.to_csv(train_file_path)
        test_frame.to_csv(test_file_path)
        with open(class_output_path, 'w') as writable:
            json.dump(class_labels, writable)
        logger.info(f'Written to {train_file_path}, {test_file_path} and {class_output_path}')
    else:
        logger.info(f'Would have written to {train_file_path}, {test_file_path} and {class_output_path}')


if __name__ == '__main__':
    split_train_test()
