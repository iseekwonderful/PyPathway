from shutil import copytree


def copy_dir(source, target):
    copytree(source, target)