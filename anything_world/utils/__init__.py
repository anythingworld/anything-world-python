import os

from typing import Optional


def get_extension(filename: str) -> str:
    """
    Get the file extension from a given filename.

    :param filename: str, File name to get extension from
    :return: str, The file extension
    """
    return filename.split(".")[-1].lower()


def get_mimetype(file_path: str) -> str:
    """
    Get mimetype by file extension.
    
    Note: this is not a reliable way to get mimetype, but it's good enough for our
    purposes without adding extra requirements.
    If you need a more reliable way, please use python-magic.

    :param file_path: str, path to file
    :return: str, mimetype of file
    """
    extensions = {
        "mtl": "text/plain",
        "obj": "text/plain",
        "txt": "text/plain",
        "gltf": "text/plain",
        "fbx": "application/octet-stream",
        "bin": "application/octet-stream",
        "dae": "application/xml",
        "glb": "model/gltf-binary",
        "zip": "application/zip",
        "jpeg": "image/jpeg",
        "jpg": "image/jpg",
        "png": "image/png",
        "bmp": "image/bmp",
        "gif": "image/gif",
        "tif": "image/tiff",
        "tiff": "image/tiff",
        "tga": "image/x-tga",
        "targa": "image/x-tga"
    }
    try:
        return extensions.get(get_extension(file_path))
    except IndexError:
        raise Exception(f"Could not get extension for file {file_path}")


def get_env(key: str) -> Optional[str]:
    """
    Retrieves the value of an environment variable.

    This function retrieves the value of the specified environment variable. If the environment variable is not set,
    it raises an exception.

    :param key: str, the name of the environment variable.
    :return: str, optional, the value of the environment variable, or None if the environment variable is not set.
    :raises Exception: If the environment variable is not set.
    """
    value = os.getenv(key)
    if not value:
        raise Exception(f"Environment variable {key} is not set")
    return value


def read_files(files_dir: str) -> list:
    """
    Read files from a directory (or single file), returning a tuple with
    filename, full path to file and its mimetype (inferred by its
    extension-only for now).

    :param files_dir: str, path to asset directory (or single asset file)
    :return: list, files as tuples (file name, local path, mime type)
    """
    files_to_get = []
    if os.path.isdir(files_dir):
        files_to_get = os.listdir(files_dir)
    else:
        files_to_get = [files_dir]
    files = []
    for filename in files_to_get:
        if filename == files_dir:
            file_path = filename
        else:
            file_path = os.path.join(files_dir, filename)
        mimetype = get_mimetype(file_path)
        files.append((os.path.basename(file_path), file_path, mimetype)) 
    return files

