import os
import re
import math
import aiohttp
from discord import Message, Attachment
from markdown_pdf import MarkdownPdf, Section
from util.image import convert_to_png, get_from_url, get_tenor_gif

def fix_code_block_formatting(text):
    fixed_content = text
    # for i, match in enumerate(re.finditer("```", text)):
    #     if i % 2:
    #         if fixed_content[match.start()+i-1] != "\n":
    #             fixed_content = fixed_content[:match.start()+i] + "\n" + fixed_content[match.start()+i:]
    #     else:
    #         if fixed_content[match.end()+i] != "\n":
    #             fixed_content = fixed_content[:match.end()+i] + "\n" + fixed_content[match.end()+i:]

    blocks = list(re.finditer("```", fixed_content))
    MAX_LEN = 70
    for i in range(len(blocks)//2):
        offoffset = 0
        if i > 0:
            offoffset = blocks[(i*2)-1].start() - offset
        offset = blocks[2*i].end() + offoffset + 1
        content = fixed_content[offset:blocks[(2*i)+1].start()-1+offoffset]
        lines = content.split("\n")
        for line in lines:
            if len(line) > MAX_LEN:
                words = line.split()
                num_lines = math.ceil(len(line)/MAX_LEN)
                start = -1
                split_point = max(MAX_LEN - 20, len(line)//num_lines)
                for word in words:
                    if len(word) > split_point:
                        while len(word) > split_point:
                            offset += split_point
                            fixed_content = fixed_content[:offset] + "-\n" + fixed_content[offset:]
                            word = word[split_point-start-2:]
                            start = 0
                        start = len(word) + 1
                    elif start + len(word) + 1 > split_point:
                        offset += start
                        fixed_content = fixed_content[:offset] + "\n" + fixed_content[offset+1:]
                        start = len(word) + 1
                    else:
                        start += len(word) + 1
                offset += start + 1
            else:
                offset += len(line) + 1
    return fixed_content

async def get_headers(url):
    async with aiohttp.ClientSession() as session:
        try:
            return await session.head(url)
        except Exception as e:
            print("Error gettings header of", url, "If this is unexpected then yell at Ray")
            print(e)
            return None

async def save_attachment(attachment: Attachment, path: str, has_type: bool = True):
    if not os.path.exists(path + "images/"):
        os.makedirs(path + "images/")

    filename = attachment.filename
    i = 0
    while os.path.isfile(path + "images/" + filename):
        i += 1
        filename = attachment.filename[:attachment.filename.rfind(".")] + str(i) + attachment.filename[attachment.filename.rfind("."):]
    await attachment.save(path + "images/" + filename)

    is_webp = attachment.content_type.endswith("webp") if attachment.content_type else filename.endswith("webp")
    if is_webp:
        await convert_to_png(path + "images/", filename, ".webp")
        os.remove(path + "images/" + filename)
        filename = filename[:-5] + ".png"

    print("Saved attachment:", filename)
    return filename

async def message_to_markdown(message: Message, path: str, show_user = True):
    markdown = ""
    if show_user:
        markdown = f"### **{message.author.global_name}** | {message.created_at.astimezone().strftime("%d/%m/%Y | %I:%M %p")}\n\n"

    markdown += fix_code_block_formatting(message.content)
    for user in message.mentions:
        markdown = markdown.replace(user.mention, f"@{user.global_name}")
    
    for attachment in message.attachments:
        # If content_type exists
        if attachment.content_type and (attachment.content_type.startswith("image") or attachment.content_type.startswith("video")):
            try:
                filename = await save_attachment(attachment, path)
            except Exception as e:
                print("Error while downloading attachment!")
                print(e)
                print("Skipping this image!")
            else:
                if attachment.content_type.startswith("image"):
                    markdown += f"\n\n![{filename}](./images/{filename})"
                else:
                    markdown += f"\n\nVideo Attachment: [{filename}]"
        # If content_type doesn't exist
        elif attachment.filename and (attachment.filename[-4:] in ("webp", "jpeg") or attachment.filename[-3:] in ("jpg", "png", "gif", "mp4", "mov", "avi")):
            try:
                filename = await save_attachment(attachment, path, has_type=False)
            except Exception as e:
                print("Error while downloading attachment!")
                print(e)
                print("Skipping this image!")
            else:
                if attachment.filename[-3:] in ("mp4", "mov", "avi"):
                    markdown += f"\n\nVideo Attachment: [{filename}]"
                else:
                    markdown += f"\n\n![{filename}](./images/{filename})"

    url_reg = r"([\w+]+\:\/\/)?([\w\d-]+\.)*[\w-]+[\.\:]\w+([\/\?\=\&\#.]?[\w-]+)*\/?"
    matches = re.finditer(url_reg, message.content)
    for match in matches:
        headers = await get_headers(match[0])
        if not headers:
            print("Error processing this URL, potentially due to availability. Ignore if not URL:", match[0])
            continue
        if headers.content_type.startswith("image"):
            print("Pulling image from:", match[0])
            try:
                filename = await get_from_url(match[0], path + "images/")
            except Exception as e:
                print("An error occurred trying to fetch an image from a URL")
                print(e)
                print("Skipping this image!")
            else:
                markdown += f"\n\n![{filename}](./images/{filename})"
        if match[0].find("tenor") != -1:
            print("Pulling gif from:", match[0])
            try:
                filename = await get_tenor_gif(match[0], path + "images/")
            except Exception as e:
                print("An error occurred trying to fetch an image from Tenor")
                print(e)
                print("Skipping this image!")
            else:
                markdown += f"\n\n![{filename}](./images/{filename})"
    return markdown

async def markdown_to_pdf(md_file, path):
    old_path = os.getcwd()
    os.chdir(path)
    with open(md_file, "r", encoding="utf-8") as md:
        content = md.read()
        pdf = MarkdownPdf(toc_level=2, optimize=True)
        pdf.add_section(Section(content, toc=False))
        pdf.save(md_file[:-3] + ".pdf")
    os.chdir(old_path)