import click
from tools import get_data_file
from glob import glob
from pathlib import Path
import pandas as pd
from PIL import Image
import os
from tools.utils import relative2absolute
from sklearn.model_selection import train_test_split

def txt_to_frame(txt, headers=False):
    df = pd.read_csv(txt, sep=' ', header=None)
    if headers:
        df.columns = ['class', 'cx', 'cy', 'width', 'height']
    return df

def annotation_to_frame(annotations):
    in_collection = []
    for annotation_file in annotations:
        image_path = Path('../data/raw/images/', f'{annotation_file.stem}.jpg')
        im = Image.open(image_path)
        values = []
        for i, row in txt_to_frame(annotation_file, headers=True).iterrows():
            class_id = row['class']
            if class_id  in ids_to_keep:
                x, y, w, h = relative2absolute(row['cx'], row['cy'], row['width'], row['height'], 
                                               img_w=im.size[0], img_h=im.size[1])
                
                values.append([str(image_path), classes[class_id], w, h, x, y, x+w, y+h ])
        in_collection.extend(values)
    labels = pd.DataFrame(in_collection, columns=['filename','class',  'width', 'height', 'xmin', 'ymin', 'xmax', 'ymax'])
    return labels

@click.command()
@click.argument('annotations_path', type=click.Path(exists=True, file_ok=False))
@click.argument('images_path', type=click.Path(exists=True, file_ok=False))
@click.argument('output_path', type=click.Path(exists=True, file_ok=False))
@click.option('--class', '-c', 'class_', multiple=True, type=click.STRING)
@click.option('--random-state', '-r', type=click.INT)
@click.option('--test-size', '-t', type=click.FLOAT)
@click.option('--dry-run', '-t', type=click.FLOAT)
def split_train_test(annotations_path, images_path, output_path, class_, random_state, test_size, dry_run):
    classes_to_keep = set(class_)

    print(class_, annotations_path, images_path, output_path, random_state, test_size, dry_run)
    return
    classes_path = Path(annotations_path, 'classes.txt')
    with open(classes_path) as readable:
        classes = { i:tag.strip() for i, tag in enumerate(readable) }
        rev_class = {v:k for k,v in classes.items()}
    ids_to_keep = set([ rev_class[k] for k in classes_to_keep ])


    annotation_files = [annotation for annotation in Path(annotations_path).glob('[!classes]*.txt')]
    filtered_annotations = []
    annotation = None
    for annotation_file in annotation_files:
        annotation = txt_to_frame(annotation_file)
        classes_in_image = set(annotation[0].values)
        intersection = classes_in_image.intersection(ids_to_keep)
        if intersection:
            filtered_annotations.append(annotation_file)

    train_frame = annotation_to_frame(train_annotations)
    test_frame = annotation_to_frame(test_annotations)

if __name__ == '__main__':
    split_train_test()