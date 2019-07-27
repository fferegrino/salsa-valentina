import os
from os.path import join

EXPERIMENT_ROOT = os.getenv('EXPERIMENT_ROOT')


def get_file(file):
    return join(EXPERIMENT_ROOT, file)


def get_data_file(source, file):
    return join(EXPERIMENT_ROOT, 'data', source, file)


def get_bin_file(file):
    return join(EXPERIMENT_ROOT, 'bin', file)


def create_folder(output_path, dry_run, logger):
    if not output_path.exists():
        if dry_run:
            logger.info(f"Would have created the folder {str(output_path)}")
        else:
            logger.info(f"Creating folder {str(output_path)}")
            output_path.mkdir(parents=True)
    else:
        logger.info(f"Output folder {str(output_path)} already exists")
