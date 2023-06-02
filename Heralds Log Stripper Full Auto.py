import pyperclip #run "pip install pyperclip" in terminal

new_log = open("strippednwclientLog1.txt", "w")
dm_name = "DM Herald" #Replace with your DM name here

def speaker_detector():
    original_log = open("nwclientLog1.txt", "r")
    speakerList = []
    speakerListRemoval = ['DM', dm_name]
    for line in original_log:
        start_index = line.find('[') + 1  
        end_index = line.find(']')  

        if start_index != -1 and end_index != -1 and start_index < end_index:
            extracted_text = line[start_index:end_index]
            speakerList.append(extracted_text)
    speakerList = [item for item in speakerList if item not in speakerListRemoval]
    most_frequent = max(speakerList, key=speakerList.count)
    return most_frequent
    original_log.close()

def log_stripper(dm_name, player):
    original_log = open("nwclientLog1.txt", "r")
    for line in original_log:
        if line.startswith("["+ dm_name + "]") or line.__contains__(player):
            new_log.write(line)
    new_log.close()
    
def copy_to_clipboard():
    file = open("strippednwclientLog1.txt", 'r')
    file_contents = file.read()
    pyperclip.copy(file_contents)
    
log_stripper(dm_name, speaker_detector())
copy_to_clipboard()

