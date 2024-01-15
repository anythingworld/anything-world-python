import os
import aiohttp
import aiofiles
import magic
from typing import Optional


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
        mime = magic.Magic(mime=True)
        mimetype = mime.from_buffer(open(file_path, "rb").read(4096))
        files.append((os.path.basename(file_path), file_path, mimetype))
    return files


def create_form_data(files: list, key_value_data: dict) -> aiohttp.FormData:
    """
    Create an instance of `aiohttp.FormData` encoding files (with the
    right filename and content type) and key-value data, provided as a dict.

    :param files: list, asset files represented as tuple like
        (filename, filepath, mimetype)
    :param key_value_data: dict, representing key-value pairs to encode as
        form-data fields
    :return: FormData, data to be sent as form-data
    """
    data = aiohttp.FormData()
    for filename, filepath, mimetype in files:
        data.add_field(
            filename,
            open(filepath, 'rb'),
            filename=filename,
            content_type=mimetype)
    for key, value in key_value_data.items():
        data.add_field(key, value)
    return data


async def download_file(url: str, file_path: str):
    """
    Asynchronously downloads a file from a URL.

    This function sends a GET request to the specified URL and writes the response to a file at the specified path.

    :param url: str, the URL of the file to download.
    :param file_path: str, the path where the downloaded file should be saved.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(file_path, mode='wb')
                await f.write(await resp.read())
                await f.close()


async def send_request(url: str,
                       method: Optional[str] = "POST",
                       request_timeout: Optional[int] = 500,
                       **kwargs) -> dict:
    """
    Asynchronously sends a request to a URL.

    This function sends a GET or POST request to the specified URL and returns the response. If the response content
    type is not "application/json", it raises an exception.

    :param url: str, the URL to send the request to.
    :param method: str, optional, the HTTP method to use. Defaults to "POST".
    :param request_timeout: int, optional, the total timeout for the request in seconds. Defaults to 500.
    :param kwargs: additional keyword arguments to pass to the request.
    :return: dict, the JSON response from the server encoded as a dict.
    :raises Exception: If the response content type is not "application/json".
    """
    timeout = aiohttp.ClientTimeout(total=request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        if method == "GET":
            res = await session.get(url, **kwargs)
        else:
            res = await session.post(url, **kwargs)
        if res.content_type == "application/json":
            content = await res.json()
            if res.status in [200, 403]:
                return content
            if res.status in [400, 404]:
                raise Exception(f"{content['code']}: {content['message']}.")
        else:
            raise Exception(f"Unexpected response content type: {res.content_type}.")