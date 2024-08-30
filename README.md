# Interview Log Sanitizer README

## Installation Instructions:
1. Clone or download the repository from GitHub. Only the Log Sanitizer executable  file is relevant for normal usage. All other files are present for reference and review.
2. Enable logging for the NWN client, if this has not already been done. Game Options > Game > Logging > Enable Game Log Chat Text > Advanced > Server Log Rotation.
3. Move the Log Sanitizer executable to the logs folder. The logs folder is typically found in Documents > Neverwinter Nights > logs.

## Set Up Instructions:
1. Open the Log Sanitizer executable. This may take several seconds as the required packages to run the executable are unpacked.
2. In the DM name section, enter your name as it would appear in the logs, including the DM title.
3. Select the input file, which will be named nwnclientLog1.txt by default.
4. The DM name and the input file are saved onto the log_sanitizer_config.json file for future usage.

## Usage Instructions:
1. Open the Log Sanitizer executable. This may take several seconds as the required packages to run the executable are unpacked.
2. Select the speaker detection method:
    - Auto-detect Speaker will parse through the log file to see which individual has spoken the most lines who is also not the individual described in DM name, that individual will be set as the active speaker.
    - Manual Speaker Entry allows the user to define the individual being spoken to. If the speaker defined by the user is not found by the Log Sanitizer, the user will receive a warning message.
3. Click on "Process Log".
4. Click on "Copy Log to Clipboard" at the bottom of the screen.
5. Sanitized logs are now ready to be attached to a case file on the Astrolabe.

## Additional Feature(s):
1. To search for specific phrases, enter the phrase in the search box and click "Search". The search is case insensitive and will highlight all results in the stripped logs matching the query. To clear the highlighting, click on the "Clear Search" button.