import requests
import yaml
import time
import json
import os

session = requests.session()

def read_chapters(session, access_token, id, chapter_list):
    response = session.post(
    f"https://api.mangadex.org/manga/{id}/read",
    headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    json={"chapterIdsRead": chapter_list}
    )
    response.raise_for_status()
    #print(response.json())

# function only for testing, I take no responsibility for any damage you may do
def unread_chapters(session, access_token, id, chapter_list):
    response = session.post(
    f"https://api.mangadex.org/manga/{id}/read",
    headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    json={"chapterIdsUnread": chapter_list}
    )
    response.raise_for_status()
    #print(response.json())

def set_reading_status(session, access_token, id, status):
    response = session.post(
    f"https://api.mangadex.org/manga/{id}/status",
    headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    json={"status": status}
    )
    response.raise_for_status()
    #print(response.json())

# function only for testing, I take no responsibility for any damage you may do
def unset_reading_status(session, access_token, id, status):
    response = session.post(
    f"https://api.mangadex.org/manga/{id}/status",
    headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    json={"status": None}
    )
    response.raise_for_status()
    #print(response.json())

# Load config
with open('restore-config.yaml') as f:
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


print("Starting the restore script with the following account:\n")
print(f"\nAccount: {config['username']}\nClient: {config['client_id']}\n")
print("The restore process is NON-DESTRUCTIVE in most cases, it cannot unread or unfollow series, but it can change the list a series is in.\nThis script is intended for transferring read chapters between accounts, not restoring the exact state of a reading list on the same account.\n")

while True:
    filepath = os.path.normpath(input("Enter the file path of your backup: "))
    if os.path.exists(filepath):
        break
    else:
        print(f"Couldn't find file located at {filepath}")

# open file
with open(filepath, 'r', encoding='utf-8') as f:
    backup = json.load(f)

# add each title
for title in backup.keys():
    chapter_list = []
    print(f"Restoring: {backup[title]['title']}")
    chapter_list = [chapter['id'] for chapter in backup[title]['chapters']]
    set_reading_status(session, access_token, backup[title]['id'], backup[title]['reader_status'])
    if len(chapter_list) > 50: # chunk to avoid going over the 10KB limit
        chunk = 0
        while chunk < len(chapter_list):
            read_chapters(session, access_token, backup[title]['id'], chapter_list[chunk:(chunk+51)])
            chunk += 50
            time.sleep(0.2) # rate limits
    else:
        read_chapters(session, access_token, backup[title]['id'], chapter_list)
    time.sleep(0.5) # let's try not to ddos them

print("done")