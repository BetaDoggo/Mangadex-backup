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

def get_chapters_info(ids, session):
    # returns info for all of the read chapters in a series
    full_info = []
    batch_size = 100  # MangaDex's batch limit

    for offset in range(0, len(ids), batch_size):
        current_batch = ids[offset:offset+batch_size]
        response = session.get(
            "https://api.mangadex.org/chapter",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"ids[]": current_batch, "limit": batch_size,}
        )
        
        if response.status_code == 429:
            print("Ran into rate limit, this shouldn't happen unless you've modified the hardcoded limits, or maybe there's someone else on your network abusing the api.\nYou should wait a while before trying again.")
            exit()
        elif response.status_code == 403:
            print("It looks like you've been temporarily ip banned, you'll have to wait quite a while before trying again. This should never happen unless you've disabled the previous protections.")
            exit()

        full_info.extend(response.json().get('data', []))
        time.sleep(0.2)  # rate limits
    return full_info

def get_manga_info(manga_id,session):
    # gets full manga info
    try:
        response = session.get(
            f"https://api.mangadex.org/manga/{manga_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(f"Manga: {manga_id} returned 404.'\nIt may not be available anymore.")
        elif response.status_code == 429:
            print("Ran into rate limit, this shouldn't happen unless you've modified the the hardcoded limits, or maybe there's someone else on your network abusing the api.\nPausing for 60 seconds to let it cool down.")
            time.sleep(60)
            response = session.get(
                f"https://api.mangadex.org/manga/{manga_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
        elif response.status_code == 403:
            print("It looks like you've been temporarily ip banned, you'll have to wait a while before trying again. This should never happen unless you've messed with the required pauses.")
            exit()
    return response.json()["data"]

def get_formatted_chapters(read_chapters, title,session):
    raw_info = get_chapters_info(read_chapters, session)
    #print(raw_info)
    chapters = []
    for chapter in raw_info:
        formatted_chapter = {
            "chapter_number": chapter['attributes']['chapter'],
            "title": chapter['attributes']['title'] or "",
            "volume": chapter['attributes']['volume'] or "none",
            "id": chapter['id'],
            "language": chapter['attributes']['translatedLanguage'] or "unknown",
            "pages": chapter['attributes']['pages'],
        }
        chapters.append(formatted_chapter)
        print(f"Got '{title}' chapter {chapter['attributes']['chapter']}")
        chapters.sort(key=lambda x: float(x['chapter_number'])) # holy shit a use for lambda
    return(chapters)

def get_manga(title_id,reader_status,session):
    # gets required information from a title, also returns title
    info = get_manga_info(title_id, session)
    try:
        title = info['attributes']['title']['en']
    except: # if no en title
        title = next(iter(info['attributes']['title'].values()))
    read_chapters = get_read_chapters(title_id, session)
    
    chapters = [] # fallback if no chapters are read
    chapters = (get_formatted_chapters(read_chapters,title,session))

    tags = []
    for tag in info['attributes']['tags']:
        tags.append(tag['attributes']['name']['en'])

    # put everything together (and hopefully avoid getting snagged on missing data)
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
try:
    access_token = auth_response['access_token']
except:
    print("Error:", auth_response['error_description'])
    exit()

print(f"\nAccount: {config['username']}\nClient: {config['client_id']}\n")

while True:
    filename = input("Enter filename for new backup: ")
    if filename.strip() != "":
        if not '.json' in filename:
            filename += '.json'
        if not os.path.exists(filename):
            break
        else:
            print(f"{filename} already exists. Overwriting files is not allowed to avoid data loss.")
    else:
        print("You must enter a filename")

input("Press enter to start.")

full_data = {}
# get list of titles
titles = get_manga_list(session)
titles = dict(titles).items()
# get chapters
for item in titles:
    time.sleep(0.2) # rate limits
    uuid = item[0]
    status = item[1]
    data, title = (get_manga(uuid,status,session))
    full_data[title] = data

full_data = dict(sorted(full_data.items())) # sort titles

with open(filename, "w", encoding="utf-8") as f:
    json.dump(full_data, f, indent=4)

print("done")