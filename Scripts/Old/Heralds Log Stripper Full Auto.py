import codecs

new_log = open("strippednwclientLog1.txt", "w", encoding="utf-8")
dm_name = "DM Herald" #Replace with your DM name here

def speaker_detector():
    speakerList = []
    speakerListRemoval = ['DM', dm_name]
    try:
        with codecs.open("nwclientLog1.txt", "r", encoding="utf-8", errors="replace") as original_log:
            for line in original_log:
                start_index = line.find('[') + 1  
                end_index = line.find(']')  
                if start_index != -1 and end_index != -1 and start_index < end_index:
                    extracted_text = line[start_index:end_index]
                    speakerList.append(extracted_text)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    speakerList = [item for item in speakerList if item not in speakerListRemoval]
    if speakerList:
        most_frequent = max(speakerList, key=speakerList.count)
        return most_frequent
    return None

def log_stripper(dm_name, player):
    try:
        with codecs.open("nwclientLog1.txt", "r", encoding="utf-8", errors="replace") as original_log:
            for line in original_log:
                if line.startswith("["+ dm_name + "]") or (player and player in line):
                    new_log.write(line)
    except Exception as e:
        print(f"Error processing file: {e}")
    finally:
        new_log.close()

player = speaker_detector()
if player:
    log_stripper(dm_name, player)
else:
    print("Could not detect a player. Please check the log file.")

# Uncomment the following lines if you want to use the clipboard functionality
# import pyperclip
# def copy_to_clipboard():
#     with open("strippednwclientLog1.txt", 'r', encoding="utf-8") as file:
#         file_contents = file.read()
#         pyperclip.copy(file_contents)
# copy_to_clipboard()