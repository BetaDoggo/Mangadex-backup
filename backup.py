import requests
import yaml
import time
import json
import os

def get_manga_list(session):
    # gets a list title ids from the user's lists
    response = session.get(
        "https://api.mangadex.org/manga/status",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"status": None}
    )
    response.raise_for_status()
    return response.json().get('statuses', {})

def get_read_chapters(manga_id,session):
    # returns a list of read chapters
    response = session.get(
        f"https://api.mangadex.org/manga/{manga_id}/read",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response.raise_for_status()
    return response.json()["data"]

def get_raw_chapter(chapter_id,session):
    # gets full chapter info
    response = session.get(
        f"https://api.mangadex.org/chapter/{chapter_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response.raise_for_status()
    return response.json()["data"]

def get_manga_info(manga_id,session):
    # gets full manga info
    response = session.get(
        f"https://api.mangadex.org/manga/{manga_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response.raise_for_status()
    return response.json()["data"]

def get_formatted_chapter(chapter_id, title,session):
    chapter = get_raw_chapter(chapter_id, session)
    formatted_chapter = {
        "chapter_number": chapter['attributes']['chapter'],
        "title": chapter['attributes']['title'] or "",
        "volume": chapter['attributes']['volume'] or "none",
        "id": chapter['id'],
        "pages": chapter['attributes']['pages'],
    }
    print(f"Got '{title}' chapter {chapter['attributes']['chapter']}")
    return(formatted_chapter)

def get_manga(title_id,reader_status,session):
    # gets required information from a title, also returns title
    info = get_manga_info(title_id, session)
    try:
        title = info['attributes']['title']['en']
    except: # if no en title
        title = next(iter(info['attributes']['title'].values()))
    read_chapters = get_read_chapters(title_id, session)
    
    chapters = []
    for chapter in read_chapters:
        time.sleep(0.1)
        try:
            chapters.append(get_formatted_chapter(chapter,title,session))
        except:
            print(f"Failed to get chapter: {chapter} of '{title}'\nIt may have been removed.")

    tags = []
    for tag in info['attributes']['tags']:
        tags.append(tag['attributes']['name']['en'])

    # put everything together (and hopefully avoid getting snagged on)
    full_info = {
        "title": title,
        "altTitles": info['attributes'].get('altTitles', []),
        "id": info['id'],
        "description": info['attributes']['description'].get('en', ""), 
        "originalLanguage": info['attributes'].get('originalLanguage', 'unknown'),
        "status": info['attributes'].get('status'),
        "reader_status": reader_status,
        "contentRating": info['attributes'].get('contentRating', 'unknown'),
        "tags": tags,
        "chapters": chapters,
    }
    return(full_info, title)

session = requests.Session()

# Load config
with open('backup-config.yaml') as f:
    config = yaml.safe_load(f)

# Get token
auth_response = session.post(
    "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token",
    data={
        "grant_type": "password",
        "username": config['username'],
        "password": config['password'],
        "client_id": config['client_id'],
        "client_secret": config['client_secret']
    }
).json()
access_token = auth_response['access_token']


print(f"\nAccount: {config['username']}\nClient: {config['client_id']}\n")
filename = input("Enter filename for new backup: ")
if not '.json' in filename:
    filename += '.json'
if os.path.exists(filename):
    print("That file already exists. Exiting to avoid potential data loss.")
    exit()
input("Press enter to start.")


full_data = {}
# get list of titles
titles = get_manga_list(session)
titles = dict(titles).items()
# get chapters
for item in titles:
    uuid = item[0]
    status = item[1]
    data, title = (get_manga(uuid,status,session))
    full_data[title] = data

with open(filename, "w", encoding="utf-8") as f:
    json.dump(full_data, f, indent=4)

print("done")