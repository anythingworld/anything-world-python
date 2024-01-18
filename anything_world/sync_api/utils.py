import requests

from typing import Optional


def create_form_data(files: list, key_value_data: dict) -> dict:
    """
    Create a dict encoding files (with the
    right filename and content type) and key-value data, provided as a dict.

    :param files: list, asset files represented as tuple like
        (filename, filepath, mimetype)
    :param key_value_data: dict, representing key-value pairs to encode as
        form-data fields
    :return: dict, data to be sent as form-data
    """
    data = []
    for filename, filepath, mimetype in files:
        data.append(('files', (filename, open(filepath, 'rb'), mimetype)))
    for key, value in key_value_data.items():
        data[key] = (None, value)
    return data


def download_file(url: str, file_path: str):
    """
    Downloads a file from a URL.

    This function sends a GET request to the specified URL and writes the response to a file at the specified path.

    :param url: str, the URL of the file to download.
    :param file_path: str, the path where the downloaded file should be saved.
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)


def send_request(url: str,
                       method: Optional[str] = "POST",
                       request_timeout: Optional[int] = 500,
                       **kwargs) -> dict:
    """
    Sends a request to a URL.

    This function sends a GET or POST request to the specified URL and returns the response. If the response content
    type is not "application/json", it raises an exception.

    :param url: str, the URL to send the request to.
    :param method: str, optional, the HTTP method to use. Defaults to "POST".
    :param request_timeout: int, optional, the total timeout for the request in seconds. Defaults to 500.
    :param kwargs: additional keyword arguments to pass to the request.
    :return: dict, the JSON response from the server encoded as a dict.
    :raises Exception: If the response content type is not "application/json".
    """
    if method == "GET":
        res = requests.get(url, **kwargs)
    else:
        res = requests.post(url, **kwargs)
    content_type = res.headers["content-type"]
    if "application/json" in content_type:
        content = res.json()
        if res.status_code in [200, 403]:
            return content
        if "code" in content and "message" in content:
            raise Exception(f"{content['code']}: {content['message']}.")
        else:
            raise Exception(f"Unexpected response: {content}.")
    else:
        raise Exception(f"Unexpected response content type: {content_type}.")