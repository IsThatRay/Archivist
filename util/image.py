from PIL import Image
import requests
import aiohttp
import os
import re
import io

from util.threading import to_thread

async def get_image(url):
    async with aiohttp.ClientSession(auto_decompress=False) as session:
        async with session.get(url) as response:
            if response.status == 200:
                buffer = io.BytesIO(await response.read())
                img = Image.open(buffer)
                return img
            else:
                print("Non-OK Response from Server:", response.status)
                return None
            
async def get_raw(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                    return response.text()
            else:
                return None

async def convert_to_png(path, filename, ext):
    img = Image.open(path + filename)
    img.save(path + filename[:-len(ext)] + ".png", "PNG")

async def get_from_url(url, path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    img = await get_image(url)
    if not img:
        return None
    
    filename = os.path.basename(url)
    query = filename.find("?")
    if query != -1:
        filename = filename[:query].split(".")[0]
    
    i = 0
    while os.path.isfile(path + filename + ".png"):
        i += 1
        filename = filename + str(i)
    filename = filename + ".png"

    img.save(path + filename, "PNG")
    print("Downloaded",filename,"from weblink")
    return filename

@to_thread
def get_tenor_gif(url, path):
    if not os.path.exists(path):
        os.makedirs(path)
    res = get_raw(url)
    url = None
    for match in re.finditer(r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])", res):
        url = match[0]
        if url.find("media1.tenor") != -1:
            break
    if url:
        url = "https://c.tenor.com/" + url.split("/m/")[1]
    
        img = get_image(url)
        if img:
            filename = os.path.basename(url)
            img.save(path + filename, "GIF", save_all=True)
            print("Downloaded gif",filename,"from web link")
            return filename
        else:
            return None
    else:
        return None