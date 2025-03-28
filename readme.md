# Mangadex-Backup
A simple utility to backup your Mangadex reading lists and transfer it between accounts. The list is stored in a human readable json format, best viewed through an IDE like vscode.

This tool does not download any of the chapters themselves, this tool is simply for preserving and transfering your on-site reading list.

# Setup
Before you can backup or restore your lists you need to setup your api client. If you already know how to do this, just enter the required information in backup-config.yaml and restore-config.yaml. You can ignore the restore-config.yaml if you do not intend to copy your history to another account. **Do not use the same account for both backup-config.yaml and restore-config.yaml, that would be pointless.**

```
git clone https://github.com/BetaDoggo/Mangadex-backup.git
cd Mangadex-backup
pip install -r requirements.txt
```

Go to settings->API Clients

![step1](https://github.com/BetaDoggo/Mangadex-backup/blob/main/images/step%201.png) ![step2](https://github.com/BetaDoggo/Mangadex-backup/blob/main/images/step%202.png)

Create a new personal API Client

![step3](https://github.com/BetaDoggo/Mangadex-backup/blob/main/images/step%203.png)

![step4](https://github.com/BetaDoggo/Mangadex-backup/blob/main/images/step%204.png)

Copy your client information into `backup-config.py` or `restore-config.py`

Then run:

```
python backup.py
```


## Notes
For safety reasons the restore script is only able to mark chapters as read. Wiping the existing read chapters is fairly trivial (and can be done with only 2 line changes in restore.py) but I don't feel like making that readily available because I'd feel bad if someone accidentally wiped their reading lists, even if it was 100% user error.

I've done my best to handle any missing data or errors that might appear but my list probably isn't large or niche enough to find every single issue. If your list causes a problem please open an issue and I'll try to figure it out.
