import os
from dotenv import load_dotenv
import requests
from xml.etree import ElementTree
from bs4 import BeautifulSoup
from openai import OpenAI
import json
import logging

# ======== Configuration ========
load_dotenv()

RSS_FEED_URL = os.getenv("RSS_FEED_URL")
if not RSS_FEED_URL:
    raise ValueError("RSS_FEED_URL environment variable not set")

PROMPTS_FILE = os.getenv("PROMPTS_FILE", "prompts.json")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# ========= OpenAI API Setup ========

client = OpenAI(api_key=OPENAI_API_KEY)

prompts = {}
with open(PROMPTS_FILE, "r") as f:
    prompts = json.load(f)

# ======== RSS Feed Fetching ========
def fetch_rss_feed(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def parse_rss_feed(rss_content: bytes) -> list:
    root = ElementTree.fromstring(rss_content)
    items = []
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        items.append({'title': title, 'link': link})
    return items

# ======== Article Content Extraction ========
def fetch_article_content(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_article_content(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    story_page = soup.find("bsp-story-page")
    if story_page:
        text = story_page.get_text(separator="\n", strip=True)
        text = text.split("Related Stories")[0]
        text = text.replace("\n", " ").replace("  ", " ")
        return text
    return ""

# ======== Classification with OpenAI ========
def classify_article(article_text: str, prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Article:\n{article_text}"}
            ],
            max_tokens=50,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        return "ERROR"

# ======== Summarization ========

def summarize_article(article_text: str, prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Article:\n{article_text}"}
            ],
            max_tokens=250,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        return "ERROR"


# ======== Pipeline Execution ========
def article_pipeline(article_url: str) -> str:
    article_content = fetch_article_content(article_url)
    article_text = parse_article_content(article_content)
    classification = classify_article(article_text, prompts.get("relevance_classifiers", {}).get("absolute", "Is this article absolutely relevant?"))
    if classification.lower() == "yes":
        summary = summarize_article(article_text, prompts.get("summarization", {}).get("detailed", "Summarize the article in a few sentences."))
        return summary
    return "Not Relevant"

def main():
    rss_content = fetch_rss_feed(RSS_FEED_URL)
    items = parse_rss_feed(rss_content)

    not_relevant_count = 0
    output_data = []
    total = len(items)

    print(f"Processing {total} articles...")

    for idx, item in enumerate(items[:5], 1):
        print(f"[{idx}/{min(5, total)}] Processing: {item['title']}")
        summary = article_pipeline(item['link'])
        if summary == "Not Relevant":
            not_relevant_count += 1
            continue
        try:
            summary_json = json.loads(summary)
        except Exception:
            summary_json = {"summary": summary}
        output_data.append({
            "title": item['title'],
            "link": item['link'],
            "summary": summary_json
        })

    result = {
        "articles": output_data,
        "skipped_irrelevant": not_relevant_count
    }

    with open("output2.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Processing complete. Results written to output.json.")

if __name__ == "__main__":
    main()