import os
import shutil
import time
import re
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_community.llms import Ollama

# 1. Configuration
llm = Ollama(model="llama3")
TARGET_DIRS = [os.path.expanduser("~/Desktop"), os.path.expanduser("~/Downloads")]

# 2. The "Classifier" Logic
def get_category(filename):
    prompt = f"Categorize this filename into one word (Images, Documents, Software, Media, or Chalmers). If it doesn't fit, output Misc: {filename}. Reply with ONLY the category name."
    category = llm.invoke(prompt).strip()
    
    valid_categories = ["Images", "Documents", "Books", "Finance", "Software", "Media", "Chalmers", "Misc"]
    return category if category in valid_categories else "Misc"

def process_duplicate(file_path: Path, notify: bool = False):
    filename = file_path.name
    # Match files ending in ' (1)', ' 1', or ' copy' before the extension
    match = re.match(r'^(.*?)\s+(?:\(\d+\)|\d+|copy)(\.[^.]+)?$', filename, re.IGNORECASE)
    if not match:
        return False
        
    original_base = match.group(1)
    extension = match.group(2) or ""
    original_name = original_base + extension
    
    target_dir = file_path.parent
    
    # Places to check for the existing original file (the main dir + known category dirs)
    directories_to_check = [target_dir] + [target_dir / cat for cat in  ["Images", "Documents", "Books", "Finance", "Software", "Media", "Chalmers", "Misc"]]
    
    for check_dir in directories_to_check:
        if (check_dir / original_name).exists():
            print(f"[Duplicate Detected] '{original_name}' already exists. Moving duplicate '{filename}' to Bin.")
            try:
                bin_dir = target_dir / "Bin"
                bin_dir.mkdir(exist_ok=True)
                
                dest_path = bin_dir / filename
                if dest_path.exists():
                    dest_path = bin_dir / f"{int(time.time())}_{filename}"
                    
                shutil.move(str(file_path), str(dest_path))
                
                if notify:
                    safe_name = filename.replace('"', '\\"')
                    os.system(f'osascript -e \'display notification "{safe_name} was moved to the Bin folder!" with title "Duplicate File Found"\'')
                
                return True
            except Exception as e:
                print(f"[Agent Error] Could not move duplicate {filename}: {e}")
                return False
                
    return False

# 3. Phase 1: The "Initial Sweep" (Existing Files)
def organize_existing_files():
    print("\n### Phase 1: Sweeping Existing Files ###")
    for target in TARGET_DIRS:
        target_path = Path(target)
        if not target_path.exists():
            continue
            
        for file in os.listdir(target):
            file_path = target_path / file
            
            # Guard Clause: Skip directories and hidden files
            if file_path.is_dir() or file.startswith('.'):
                continue
                
            if process_duplicate(file_path):
                continue
            
            print(f"Analyzing existing file: {file}")
            category = get_category(file)
            dest_dir = target_path / category
            dest_dir.mkdir(exist_ok=True)
            
            print(f"Moving: {file} -> {category}/")
            shutil.move(str(file_path), str(dest_dir / file))
    print("### Phase 1 Complete ###\n")

# 4. Phase 2: The Agent's Sensory System (New Files)
class AgentEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        filename = file_path.name
        
        # Guard Clause: Ignore hidden files and active downloads
        if filename.startswith('.') or filename.endswith(('.crdownload', '.part', '.tmp')):
            return
            
        time.sleep(1.5) 
        
        if process_duplicate(file_path, notify=True):
            return
        
        print(f"\n[Agent Alert] New file detected: {filename}")
        
        try:
            category = get_category(filename)
            target_dir = file_path.parent
            dest_dir = target_dir / category
            dest_dir.mkdir(exist_ok=True)
            
            print(f"Agent moving: {filename} -> {category}/")
            shutil.move(str(file_path), str(dest_dir / filename))
        except Exception as e:
            print(f"[Agent Error] Could not process {filename}: {e}")

# 5. The Main Initialization Routine
def start_agent():
    # First, clean up the existing mess
    organize_existing_files()
    
    # Then, activate the Watchdog for future files
    print("### Phase 2: Activating Background Watchdog ###")
    observer = Observer()
    event_handler = AgentEventHandler()
    
    for target in TARGET_DIRS:
        if Path(target).exists():
            observer.schedule(event_handler, target, recursive=False)
        
    observer.start()
    print(f"Agent Online. Actively guarding: {TARGET_DIRS}")
    print("Press Ctrl+C to terminate.")
    
    try:
        while True:
            time.sleep(1) # Keeps the main thread alive 
    except KeyboardInterrupt:
        observer.stop()
        print("\n### Agent Shutting Down ###")
    observer.join()

if __name__ == "__main__":
    start_agent()