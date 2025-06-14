import requests
import json

def get_stream_url(encrypted_media_url,query):
    url = "https://www.jiosaavn.com/api.php"
    print(query)
    
    params = {
        "__call": "song.generateAuthToken",
        "url": encrypted_media_url,
        "bitrate": "128",
        "api_version": "4",
        "_format": "json",
        "ctx": "web6dot0",
        "_marker": "0"
    }
    headers = {
        'authority': 'www.jiosaavn.com',
        'method': 'GET',
        'path': f'/api.php?__call=song.generateAuthToken&url={encrypted_media_url}&bitrate=128&api_version=4&_format=json&ctx=web6dot0&_marker=0',
        'scheme': 'https',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'cookie': 'CH=G03%2CA07%2CO00%2CL03; _pl=web6dot0-; DL=english; B=5aa4ec84dc72c3d1a917b82303bbf5a9; CT=MTgzNzYyNzc4Ng%3D%3D; L=hindi; geo=117.207.74.183%2CIN%2CHaryana%2CSirsa%2C125055; mm_latlong=29.5386%2C75.0272',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://www.jiosaavn.com/search/song/{query}',
        'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }


    response = requests.get(url, params=params)
    data = json.loads(response.text)

    auth_url = data.get("auth_url", "")
    if auth_url:
        auth_url = auth_url.split('?')[0]
        auth_url = auth_url.replace("ac.cf.saavncdn.com", "aac.saavncdn.com")
    return auth_url
