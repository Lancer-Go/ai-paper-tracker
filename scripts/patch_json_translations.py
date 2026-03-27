import json
import glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator

def translate_text(text):
    if not text:
        return ""
    try:
        # deep-translator has a 5000 character limit, abstract might be long but usually < 3000 chars
        # We split by newlines if it's too long, but papers usually fit.
        if len(text) > 4000:
            text = text[:4000]
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except Exception as e:
        print(f"Translate error: {e}")
        return text

def process_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    papers = data.get('papers', [])
    
    # Translate title and abstract if not already present
    def process_paper(p):
        modified = False
        if 'title_zh' not in p or not p['title_zh']:
            p['title_zh'] = translate_text(p.get('title', ''))
            modified = True
        if 'abstract_zh' not in p or not p['abstract_zh']:
            p['abstract_zh'] = translate_text(p.get('abstract', ''))
            modified = True
        return modified

    any_modified = False
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_paper, papers))
        if any(results):
            any_modified = True
            
    if any_modified:
        # Save back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Updated {filepath} with translations!")
    else:
        print(f"No translation updates needed for {filepath}.")

if __name__ == '__main__':
    exports_dir = Path("frontend/public/data/exports")
    json_files = exports_dir.glob("*.json")
    for jf in json_files:
        if jf.name == "index.json":
            continue
        process_file(jf)
    print("Done patching translations!")
