import json
import os
import time
import urllib.request
import urllib.error
import re

BASE_URL = "https://support.knowbe4.com/api/v2/help_center/en-us"
GITHUB_URL = "https://Criscras13.github.io/API_testing/api/v2/help_center/en-us"
OUTPUT_DIR = "site_src/static/api/v2/help_center/en-us"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def fetch_url(url):
    print(f"Fetching {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def transform_url(url):
    if not url:
        return url
    # Handle both support.knowbe4.com and knowbe4.zendesk.com
    url = url.replace("https://support.knowbe4.com/api/v2/help_center/en-us", GITHUB_URL)
    url = url.replace("https://knowbe4.zendesk.com/api/v2/help_center/en-us", GITHUB_URL)
    return url

def transform_html_url(html_url, item_id, resource_name):
    # Point html_url to the HTML wrapper so the GEM can browse it
    # Format: .../articles/ID.html
    return f"{GITHUB_URL}/{resource_name}/{item_id}.html"

def save_html_wrapper(item, resource_name, item_id):
    """Creates a simple HTML wrapper for the JSON data."""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{resource_name} {item_id}</title>
    <meta name="robots" content="noindex">
</head>
<body>
    <pre>{json.dumps(item, indent=2)}</pre>
</body>
</html>
"""
    with open(os.path.join(OUTPUT_DIR, resource_name, f"{item_id}.html"), 'w', encoding='utf-8') as f:
        f.write(html_content)

def transform_item(item, resource_name):
    if 'url' in item:
        item['url'] = transform_url(item['url'])
    
    if 'html_url' in item and 'id' in item:
        item['html_url'] = transform_html_url(item['html_url'], item['id'], resource_name)
        
    return item

def rewrite_pagination(content_str):
    # Rewrite pagination links in the string representation
    # Pattern: articles.json?page=2&per_page=30 -> articles_2.json
    # Pattern: articles.json?page=2 -> articles_2.json
    
    def replace_pagination(match):
        resource = match.group(1)
        page = match.group(2)
        return f"{resource}_{page}.json"

    # Regex for pagination links
    # Matches: (articles|sections|categories).json?page=(\d+)
    content_str = re.sub(r'(articles|sections|categories)\.json\?page=(\d+)(?:&[^"]*)?', replace_pagination, content_str)
    
    return content_str

def process_resource(resource_name, singular_name):
    ensure_dir(os.path.join(OUTPUT_DIR, resource_name))
    
    url = f"{BASE_URL}/{resource_name}.json?per_page=30"
    page = 1
    
    while url:
        data = fetch_url(url)
        if not data:
            break
            
        # Process individual items
        items = data.get(resource_name, [])
        for item in items:
            item_id = item.get('id')
            if item_id:
                # Transform the item (rewrite URLs)
                item = transform_item(item, resource_name)
                
                # Create wrapper object (e.g. {"article": {...}})
                wrapper = {singular_name: item}
                
                # Save individual JSON file
                with open(os.path.join(OUTPUT_DIR, resource_name, f"{item_id}.json"), 'w', encoding='utf-8') as f:
                    json.dump(wrapper, f, indent=2)
                
                # Save HTML wrapper
                save_html_wrapper(wrapper, resource_name, item_id)
        
        # Process list file (current page)
        # We need to rewrite the next/previous links in the response object
        data_str = json.dumps(data, indent=2)
        data_str = rewrite_pagination(data_str)
        
        # Determine output filename
        if page == 1:
            filename = f"{resource_name}.json"
        else:
            filename = f"{resource_name}_{page}.json"
            
        # Save JSON file
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(data_str)
        
        # Save HTML wrapper for the list (only for first page)
        if page == 1:
            html_filename = f"{resource_name}.html"
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{resource_name}</title>
    <meta name="robots" content="noindex">
</head>
<body>
    <pre>{data_str}</pre>
</body>
</html>
"""
            with open(os.path.join(OUTPUT_DIR, html_filename), 'w', encoding='utf-8') as f:
                f.write(html_content)
            
        # Get next page URL
        url = data.get('next_page')
        page += 1
        
        # Be nice to the API
        time.sleep(0.2)

def main():
    ensure_dir(OUTPUT_DIR)
    
    resources = [
        ("categories", "category"),
        ("sections", "section"),
        ("articles", "article")
    ]
    
    for resource, singular in resources:
        print(f"Processing {resource}...")
        process_resource(resource, singular)
        
    print("Data transformation complete.")

if __name__ == "__main__":
    main()
