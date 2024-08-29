import pyperclip #run "pip install pyperclip" in terminal

new_log = open("strippednwclientLog1.txt", "w")
dm_name = "DM Herald" #Replace with your DM name here

player_name = input("Player/Character Name: ");

def log_stripper(dm_name, player_name):
    original_log = open("nwclientLog1.txt", "r")
    for line in original_log:
        if line.__contains__(dm_name) or line.__contains__(player_name):
            new_log.write(line)
    new_log.close()
    
def copy_to_clipboard():
    file = open("strippednwclientLog1.txt", 'r')
    file_contents = file.read()
    pyperclip.copy(file_contents)
    
log_stripper(dm_name, player_name)
copy_to_clipboard()

