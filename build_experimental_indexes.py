"""
Phase 8: Image Metadata & Topic Indexing (Experimental)
Generates enhanced articles, image index, and topic index with HTML wrappers.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
import html

# Configuration
BASE_URL = "https://Criscras13.github.io/API_testing"
BASE_DIR = Path("site_src/static/api/v2/help_center/en-us")
ARTICLES_DIR = BASE_DIR / "articles"
EXPERIMENTAL_DIR = BASE_DIR / "experimental"
IMAGE_CAPTIONS_FILE = Path("image_captions.json")

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that'
}


def generate_html_wrapper(json_data, title="Data"):
    """Generate HTML wrapper for JSON data (matching production pattern)."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <pre>{json.dumps(json_data, indent=2)}</pre>
</body>
</html>"""


def load_image_captions():
    """Load image_captions.json."""
    if not IMAGE_CAPTIONS_FILE.exists():
        print(f"ERROR: {IMAGE_CAPTIONS_FILE} not found!")
        return None
    with open(IMAGE_CAPTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_images_from_html(html_content, image_captions):
    """Extract images with descriptions from HTML (single-quoted attributes)."""
    if not html_content:
        return []
    
    # Unescape HTML entities (&lt; to <, etc.) since article bodies are HTML-escaped
    html_content = html.unescape(html_content)
    
    images = []
    position = 0
    
    # Updated pattern to match single-quoted HTML attributes
    img_pattern = re.compile(r"<img[^>]+src='([^']+)'[^>]*>", re.IGNORECASE)
    
    for match in img_pattern.finditer(html_content):
        position += 1
        url = match.group(1)
        description = image_captions.get(url, "")
        
        context_start = max(0, match.start() - 200)
        context_text = html_content[context_start:match.start()]
        context = extract_context(context_text)
        
        images.append({
            "url": url,
            "alt": description,
            "position": position,
            "context": context
        })
    
    return images


def extract_context(text_snippet):
    """Extract meaningful context from surrounding text."""
    text = re.sub(r'<[^>]+>', '', text_snippet).strip()
    
    step_match = re.search(r'(Step \d+[:\-\s]+[^<.]+)', text, re.IGNORECASE)
    if step_match:
        return step_match.group(1).strip()
    
    sentences = text.split('. ')
    if sentences:
        return sentences[-1].strip()[:100]
    return ""


def extract_keywords(text):
    """Extract keywords from text."""
    if not text:
        return []
    text = re.sub(r'<[^>]+>', '', text)
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_-]*\b', text)
    return words


def extract_topics(article_title, section_name, category_name, image_descriptions):
    """Generate topic keywords."""
    topics = set()
    topics.update(extract_keywords(article_title))
    if section_name:
        topics.update(extract_keywords(section_name))
    if category_name:
        topics.update(extract_keywords(category_name))
    for desc in image_descriptions:
        topics.update(extract_keywords(desc))
    
    topics = {t.lower() for t in topics if t.lower() not in STOP_WORDS}
    topics = {t for t in topics if len(t) > 2 and not t.isdigit()}
    return sorted(list(topics))


def load_section_and_category_mapping():
    """Load sections and categories for metadata."""
    sections_file = BASE_DIR / "sections.json"
    categories_file = BASE_DIR / "categories.json"
    
    section_map = {}
    category_map = {}
    
    if sections_file.exists():
        with open(sections_file, 'r', encoding='utf-8') as f:
            sections_data = json.load(f)
            for section in sections_data.get('sections', []):
                section_map[section['id']] = {
                    'name': section.get('name', ''),
                    'category_id': section.get('category_id')
                }
    
    if categories_file.exists():
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
            for category in categories_data.get('categories', []):
                category_map[category['id']] = category.get('name', '')
    
    return section_map, category_map


def process_articles(image_captions, section_map, category_map):
    """Process all articles and create enhanced versions."""
    if not ARTICLES_DIR.exists():
        print(f"ERROR: Articles directory not found: {ARTICLES_DIR}")
        return None, None, None
    
    exp_articles_dir = EXPERIMENTAL_DIR / "articles"
    exp_articles_dir.mkdir(parents=True, exist_ok=True)
    
    image_index = {}
    articles_list = []
    article_count = 0
    total_images = 0
    
    print("Processing articles...")
    
    for article_file in ARTICLES_DIR.glob("*.json"):
        article_count += 1
        if article_count % 100 == 0:
            print(f"  Processed {article_count} articles, {total_images} images...")
        
        # Debug: show first few article names
        if article_count <= 3:
            print(f"  DEBUG: Processing article {article_file.name}")
        
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Article data is nested under 'article' key
                article = data.get('article', {})
        except Exception as e:
            if article_count <= 5:
                print(f"  DEBUG: Failed to load {article_file.name}: {e}")
            continue
        
        body = article.get('body', '')
        if article_count <= 3:
            print(f"  DEBUG: Body length: {len(body)}, contains <img: {'<img' in body}, contains &lt;img: {'&lt;img' in body}")
        
        images = extract_images_from_html(body, image_captions)
        
        if images and article_count <= 5:
            print(f"  DEBUG: Found {len(images)} images in {article_file.name}")
        
        if not images:
            continue
        
        total_images += len(images)
        
        section_id = article.get('section_id')
        section_info = section_map.get(section_id, {})
        section_name = section_info.get('name', '')
        category_id = section_info.get('category_id')
        category_name = category_map.get(category_id, '')
        
        image_descriptions = [img['alt'] for img in images if img['alt']]
        topics = extract_topics(
            article.get('title', ''),
            section_name,
            category_name,
            image_descriptions
        )
        
        # Create enhanced article with FULL URLs
        article_id = article['id']
        enhanced_article = article.copy()
        enhanced_article['url'] = f"{BASE_URL}/api/v2/help_center/en-us/experimental/articles/{article_id}.json"
        enhanced_article['html_url'] = f"{BASE_URL}/api/v2/help_center/en-us/experimental/articles/{article_id}.html"
        enhanced_article['images'] = images
        enhanced_article['metadata'] = {
            'category': category_name,
            'section': section_name,
            'topics': topics,
            'image_count': len(images)
        }
        
        # Save enhanced article JSON
        output_json = exp_articles_dir / f"{article_id}.json"
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(enhanced_article, f, indent=2)
        
        # Save enhanced article HTML
        output_html = exp_articles_dir / f"{article_id}.html"
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(generate_html_wrapper(enhanced_article, f"Article {article_id}"))
        
        # Add to articles list
        articles_list.append({
            'id': article_id,
            'title': article.get('title', ''),
            'url': enhanced_article['url'],
            'html_url': enhanced_article['html_url'],
            'image_count': len(images),
            'topics': topics[:10]  # First 10 topics
        })
        
        # Build image index with image IDs as keys (article_id_position)
        for img in images:
            image_id = f"{article_id}_{img['position']}"
            image_index[image_id] = {
                'url': img['url'],
                'description': img['alt'],
                'article_id': article_id,
                'article_title': article.get('title', ''),
                'article_url': enhanced_article['url'],
                'article_html_url': enhanced_article['html_url'],
                'category': category_name,
                'section': section_name,
                'topics': topics,
                'position_in_article': img['position'],
                'context': img['context']
            }
    
    print(f"\nCompleted: {article_count} articles, {total_images} images indexed")
    return image_index, articles_list, exp_articles_dir


def build_topic_index(image_index):
    """Build topic-to-images reverse index using image IDs only."""
    topic_index = defaultdict(list)
    
    # Store only image IDs, not full metadata (reduces from 2.3 GB to ~3 MB)
    for image_id, metadata in image_index.items():
        for topic in metadata['topics']:
            topic_index[topic].append(image_id)
    
    return dict(sorted(topic_index.items()))


def save_with_html(data, filename, title):
    """Save JSON and HTML wrapper."""
    json_file = EXPERIMENTAL_DIR / f"{filename}.json"
    html_file = EXPERIMENTAL_DIR / f"{filename}.html"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(generate_html_wrapper(data, title))
    
    size_kb = json_file.stat().st_size / 1024
    print(f"  {filename}.json: {size_kb:.1f} KB")
    print(f"  {filename}.html: Created")
    return json_file, html_file


def main():
    """Main execution flow."""
    print("=" * 60)
    print("Phase 8: Image Metadata & Topic Indexing (Experimental)")
    print("=" * 60)
    print()
    
    print("Loading image_captions.json...")
    image_captions = load_image_captions()
    if not image_captions:
        return
    print(f"  Loaded {len(image_captions)} image descriptions\n")
    
    print("Loading section and category mappings...")
    section_map, category_map = load_section_and_category_mapping()
    print(f"  Loaded {len(section_map)} sections, {len(category_map)} categories\n")
    
    image_index, articles_list, exp_articles_dir = process_articles(
        image_captions, section_map, category_map
    )
    
    if not image_index:
        print("ERROR: No images found")
        return
    print()
    
    print("Saving articles list...")
    save_with_html(articles_list, "articles", "Enhanced Articles List")
    print()
    
    print("Saving image index...")
    save_with_html(image_index, "image_index", "Image Index")
    print()
    
    print("Building and saving topic index...")
    topic_index = build_topic_index(image_index)
    print(f"  Generated {len(topic_index)} topics")
    save_with_html(topic_index, "topics_to_images", "Topic Index")
    print()
    
    print("=" * 60)
    print("EXPERIMENTAL INDEXING COMPLETE")
    print("=" * 60)
    print(f"Enhanced articles: {exp_articles_dir}")
    print(f"Indexes: {EXPERIMENTAL_DIR}")
    print("\nProduction files: UNCHANGED ✓")
    print()


if __name__ == "__main__":
    main()
