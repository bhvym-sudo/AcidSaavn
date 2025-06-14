from get_media_url import get_jiosaavn_results
import requests
import json

def get_auth_token(encrypted_media_url):
    url = "https://www.jiosaavn.com/api.php"
    
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
        "authority": "www.jiosaavn.com",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "cookie": "geo=59.91.162.189%2CIN%2CHaryana%2CEllenabad%2C125102; mm_latlong=29.4505%2C74.6588; CH=G03%2CA07%2CO00%2CL03; _pl=web6dot0-; DL=english; B=5aa4ec84dc72c3d1a917b82303bbf5a9; CT=MTgzNzYyNzc4Ng%3D%3D; L=hindi",
        "pragma": "no-cache",
        "referer": "https://www.jiosaavn.com/",
        "sec-ch-ua": "\"Brave\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, params=params)
    data = json.loads(response.text)
    return data


results = get_jiosaavn_results("apocalypse")
final_data = []

for song in results:
    title = song.get("title", "")
    subtitle = song.get("subtitle", "")
    image = song.get("image", "")
    encrypted_media_url = song.get("encrypted_media_url", "")
    
    token_data = get_auth_token(encrypted_media_url)
    auth_url = token_data.get('auth_url', '')
    if auth_url:
        auth_url = auth_url.split('?')[0]
        auth_url = auth_url.replace("ac.cf.saavncdn.com", "aac.saavncdn.com")
    
    final_data.append({
        "title": title,
        "subtitle": subtitle,
        "image": image,
        "url": auth_url
    })


for result in final_data:
    print(f"Title: {result['title']}")
    print(f"Subtitle: {result['subtitle']}")
    print(f"Image: {result['image']}")
    print(f"URL: {result['url']}\n")
