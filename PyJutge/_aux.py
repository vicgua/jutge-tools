import requests


def download(url, dest, verbose=False):
    if verbose:
        print('Downloading ' + url)
    r = requests.get(url)
    r.raise_for_status()
    with dest.open('wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
