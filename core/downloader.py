import requests

def download_song(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
