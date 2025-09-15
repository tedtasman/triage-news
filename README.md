# News Summarizer

A lightweight news filtering and summarization pipeline. This project classifies news articles based on relevance to US citizens and generates concise, structured summaries.

---

## Features

- Stage 1: Filter news articles (YES/NO) based on importance.
- Stage 2: Summarize important articles into structured bullet points:
  - WHO, WHAT, WHEN, WHERE, IMPACT
- US-centric and focused on actionable information.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/news-summarizer.git
cd news-summarizer
```

### 2. Set up Python venv

**MacOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```cmd
python -m venv venv
source venv\Scripts\activate
```

### 3. Install requirements

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

Create a .env in the project root and add your environment variables:

```bash
OPENAI_API_KEY=<your_api_key>
PROMPTS_FILE=<custom_prompts_file>
```

## Usage

```bash
python3 triage-script.py
```

**Windows**

```cmd
python triage-script.py
```

## News Sources

Currently, news is pulled from AP News' Top News topic via rss.app. If you wish to alter this source, modifications to the html parser will likely be required
