import requests
from pathlib import Path


def download(url, dest, verbose=False):
    if verbose:
        print('Downloading ' + url)
    r = requests.get(url)
    r.raise_for_status()
    if isinstance(dest, Path):
        fd = dest.open('wb')
        close_fd = True
    else:
        fd = dest
        close_fd = False
    try:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    finally:
        if close_fd:
            fd.close()
