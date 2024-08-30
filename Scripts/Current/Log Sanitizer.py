import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import codecs
import json
import os
import threading
import pyperclip
import re

CONFIG_FILE = "log_sanitizer_config.json"

class LogSanitizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Log Sanitizer")
        self.master.geometry("800x600")
        self.master.configure(bg='#f0f0f0')

        self.config = self.load_config()
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')

        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left frame widgets
        ttk.Label(left_frame, text="DM Name:").pack(pady=5)
        self.dm_name_entry = ttk.Entry(left_frame, width=30)
        self.dm_name_entry.insert(0, self.config.get("dm_name", ""))
        self.dm_name_entry.pack(pady=5)

        self.speaker_method = tk.StringVar(value="auto")
        ttk.Radiobutton(left_frame, text="Auto-detect Speaker", variable=self.speaker_method, value="auto", command=self.toggle_speaker_entry).pack(pady=5)
        ttk.Radiobutton(left_frame, text="Manual Speaker Entry", variable=self.speaker_method, value="manual", command=self.toggle_speaker_entry).pack(pady=5)

        ttk.Label(left_frame, text="Speaker Name:").pack(pady=5)
        self.speaker_name_entry = ttk.Entry(left_frame, width=30, state="disabled")
        self.speaker_name_entry.pack(pady=5)

        ttk.Button(left_frame, text="Select Input File", command=self.select_input).pack(pady=10)
        self.input_file_label = ttk.Label(left_frame, text="Current input file: None", wraplength=200)
        self.input_file_label.pack(pady=5)

        ttk.Button(left_frame, text="Process Log", command=self.process_log).pack(pady=10)

        # Search widgets
        ttk.Label(left_frame, text="Search:").pack(pady=5)
        self.search_entry = ttk.Entry(left_frame, width=30)
        self.search_entry.pack(pady=5)
        ttk.Button(left_frame, text="Search", command=self.search_log).pack(pady=5)
        ttk.Button(left_frame, text="Clear Search", command=self.clear_search).pack(pady=5)

        ttk.Button(left_frame, text="Help", command=self.show_help).pack(pady=10)

        # Right frame widgets
        self.output_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=60, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Button(right_frame, text="Copy Log to Clipboard", command=self.copy_output).pack(pady=10)

        self.input_file = self.config.get("last_input", "")
        if self.input_file:
            self.input_file_label.config(text=f"Current input file: {os.path.basename(self.input_file)}")

        # Bind the window close event
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_speaker_entry(self):
        if self.speaker_method.get() == "auto":
            self.speaker_name_entry.config(state="disabled")
        else:
            self.speaker_name_entry.config(state="normal")

    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def select_input(self):
        self.input_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.input_file:
            self.config["last_input"] = self.input_file
            self.save_config(self.config)
            self.input_file_label.config(text=f"Current input file: {os.path.basename(self.input_file)}")

    def process_log(self):
        dm_name = self.dm_name_entry.get()
        if not dm_name:
            messagebox.showerror("Error", "Please enter a DM name.")
            return

        if not self.input_file or not os.path.exists(self.input_file):
            messagebox.showerror("Error", "Please select a valid input file.")
            return

        def process():
            if self.speaker_method.get() == "auto":
                player = self.speaker_detector(self.input_file, dm_name)
                if not player:
                    messagebox.showwarning("Warning", "Could not detect a player. Please check the log file or use manual entry.")
                    return
            else:
                player = self.speaker_name_entry.get()
                if not player:
                    messagebox.showerror("Error", "Please enter a speaker name.")
                    return

            sanitized_content = self.log_stripper(self.input_file, dm_name, player)
            if sanitized_content:
                self.output_text.delete('1.0', tk.END)
                self.output_text.insert(tk.END, sanitized_content)

                # Check for lines spoken by the manual speaker
                if self.speaker_method.get() == "manual" and player not in sanitized_content:
                    messagebox.showwarning("Warning", f"No lines found for the speaker '{player}'. Please check the log file or enter a different speaker name.")

                messagebox.showinfo("Success", "Log has been sanitized. You can copy the content using the 'Copy Log to Clipboard' button.")
            else:
                messagebox.showwarning("Warning", "No content was generated. Please check the input file and speaker name.")

            # Save config
            self.config["dm_name"] = dm_name
            self.save_config(self.config)

        threading.Thread(target=process).start()

    def copy_output(self):
        content = self.output_text.get('1.0', tk.END).strip()
        if content:
            pyperclip.copy(content)
            messagebox.showinfo("Copied", "Log has been copied to clipboard.")
        else:
            messagebox.showwarning("Warning", "No content to copy. Please process a log first.")

    def on_closing(self):
        self.config["dm_name"] = self.dm_name_entry.get()
        self.save_config(self.config)
        self.master.destroy()

    @staticmethod
    def speaker_detector(input_file, dm_name):
        speaker_list = []
        try:
            with codecs.open(input_file, "r", encoding="utf-8", errors="replace") as original_log:
                for line in original_log:
                    start_index = line.find('[') + 1
                    end_index = line.find(']')
                    if start_index != -1 and end_index != -1 and start_index < end_index:
                        extracted_text = line[start_index:end_index]
                        speaker_list.append(extracted_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")
            return None

        # Exclude DM and empty names
        speaker_list = [item for item in speaker_list if item and item != dm_name]
        if speaker_list:
            most_frequent = max(speaker_list, key=speaker_list.count)
            return most_frequent
        return None

    @staticmethod
    def clean_line(line):
        # Remove unwanted tags and clean up lines
        line = re.sub(r'\[[a-zA-Z0-9]+\]\s*', '', line)  # Remove random ID tags
        line = re.sub(r'\[Talk\]\s*', '', line)  # Remove [Talk] tags
        line = re.sub(r'<c[^>]*>\[[^\]]+\]:<\/c>\s*', '', line)  # Remove language tags
        line = re.sub(r'<c[^>]*>:<\/c>\s*', '', line)  # Remove empty tags
        line = re.sub(r'<c[^>]*>\[Use object\]<\/c>\s*', '', line)  # Remove use object tags
        line = re.sub(r'<[^>]+>', '', line)  # Remove any remaining HTML-like tags
        line = re.sub(r'\[DM ([^\]]+)\] DM \1 :\s*', r'DM \1: ', line)  # Clean DM prefix
        return line.strip()

    @classmethod
    def log_stripper(cls, input_file, dm_name, player):
        try:
            sanitized_content = []
            dm_pattern = re.compile(rf'(?:^|\s){re.escape(dm_name)}(?:\s|:)')  # Pattern to detect DM name
            player_pattern = re.compile(rf'(?:^|\s)\[?{re.escape(player)}\]?')  # Pattern to detect player name with or without brackets
            tell_pattern = re.compile(r'\[Tell\]')  # Pattern to detect [Tell] tag

            with codecs.open(input_file, "r", encoding="utf-8", errors="replace") as original_log:
                for line in original_log:
                    # Check if line contains DM name, player name, or [Tell] tag
                    if dm_pattern.search(line) or player_pattern.search(line) or tell_pattern.search(line):
                        cleaned_line = cls.clean_line(line)
                        if cleaned_line and not cleaned_line.endswith(':'):  # Only add non-empty lines
                            sanitized_content.append(cleaned_line + '\n')
            return ''.join(sanitized_content)
        except Exception as e:
            messagebox.showerror("Error", f"Error processing file: {e}")
            return None

    def search_log(self):
        search_term = self.search_entry.get().lower()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return

        content = self.output_text.get('1.0', tk.END)
        if not content.strip():
            messagebox.showwarning("Warning", "No content to search. Please process a log first.")
            return

        # Clear previous highlighting
        self.output_text.tag_remove('search_highlight', '1.0', tk.END)

        # Search and highlight
        start_pos = '1.0'
        while True:
            start_pos = self.output_text.search(search_term, start_pos, stopindex=tk.END, nocase=1)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.output_text.tag_add('search_highlight', start_pos, end_pos)
            start_pos = end_pos

        self.output_text.tag_config('search_highlight', background='yellow', foreground='black')

        # Scroll to the first occurrence
        self.output_text.see('search_highlight.first')

        # Count occurrences
        occurrences = len(self.output_text.tag_ranges('search_highlight')) // 2
        if occurrences > 0:
            messagebox.showinfo("Search Results", f"Found {occurrences} occurrence(s) of '{search_term}'.")
        else:
            messagebox.showinfo("Search Results", f"No occurrences of '{search_term}' found.")

    def clear_search(self):
        self.output_text.tag_remove('search_highlight', '1.0', tk.END)
        self.search_entry.delete(0, tk.END)

    def show_help(self):
        help_window = tk.Toplevel(self.master)
        help_window.title("Help")
        help_window.geometry("400x400")

        help_text = """Welcome to the Log Sanitizer Help!

1. Enter the name of the DM (Dungeon Master) in the DM Name field.
2. Select the method to detect the speaker:
   - Auto-detect Speaker: The system will automatically detect the player who speaks the most.
   - Manual Speaker Entry: Enter the name of the player manually.
3. Click "Select Input File" to choose the log file you wish to sanitize.
4. Click "Process Log" to sanitize the log.
5. The sanitized log will appear on the right. You can copy it to the clipboard.
6. To search within the processed log:
   - Enter a search term in the Search field.
   - Click "Search" to highlight matching lines in the log.
   - Use "Clear Search" to remove highlighting.
7. Use "Copy Log to Clipboard" to copy the entire sanitized log.

If you have any issues, please contact DM Herald."""

        help_label = tk.Label(help_window, text=help_text, wraplength=350, justify="left")
        help_label.pack(pady=10, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = LogSanitizerApp(root)
    root.mainloop()