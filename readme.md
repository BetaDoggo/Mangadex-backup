# Mangadex-Backup
A simple utility to backup your Mangadex reading library and transfer it between accounts. The list is stored in a human readable json format, best viewed through an ide like vscode.


# Setup
Before you can backup or restore your lists you need to setup your api client. If you already know how to do this, just enter the required information in backup-config.yaml and restore-config.yaml. You can ignore the restore-config.yaml if you do not intend to copy your history to another account. **Do not use the same account for both backup-config.yaml and restore-config.yaml, that would be pointless.**


## Notes
For safety reasons the restore script is only able to mark chapters as read. Wiping the existing read chapters is fairly trivial (and can be done with only 2 line changes in restore.py) but I don't feel like making that readily available because I'd feel bad if someone accidentally wiped their reading lists, even if it was 100% user error.