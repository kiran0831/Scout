import os
from dotenv import load_dotenv
from groq import Groq
import json
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup


load_dotenv()  # load env variables from .env file
Groq_Api = os.getenv("GROQ_API_KEY")  # grab API key
client = Groq(api_key=Groq_Api)  # init Groq client


def scrape_url(url):
    try:
        # disguise as a real browser, else sites block us
        headers = {"User-Agent": "Mozilla/5.0"}

        # fetch the raw HTML
        response = requests.get(url, headers=headers, timeout=5)

        # parse HTML into a navigable tree
        soup = BeautifulSoup(response.text, "html.parser")

        # remove JS, CSS, noscript — pure noise
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # extract visible text, spaces between tags, no extra whitespace
        text = soup.get_text(separator=" ", strip=True)

        # cap at 3000 chars to stay within LLM context limits
        return text[:3000]

    except:
        # site blocked / timeout / any error → skip silently
        return ""


def save_report(report, filename="report.md"):
    # write report string to a markdown file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved successfully as {filename}")


def generate_report(results):
    # build one big context string from all scraped results
    context = "\n\n".join([
        f"""
Title: {r['title']}
URL: {r['url']}

CONTENT:
{r['content']}
"""
        for r in results
    ])

    # send context to LLM with strict research analyst instructions
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a senior research analyst AI.

You are given multiple web search results (title, snippet, and URL). Your task is to synthesize them into a high-quality research report.

STRICT RULES:
- Only use provided information. Do not hallucinate.
- If sources disagree, mention the conflict.
- Prefer more recent and detailed sources.
- Do not repeat the same point.
- Every major section must be supported by at least one source.

OUTPUT FORMAT:

Title:
- A clear report title

Executive Summary:
- Short 3–5 line summary

Detailed Analysis:
- Organize into logical sections based on the topic
- Use bullet points and headings where needed

Key Insights:
- Most important takeaways (5–8 bullets max)

Limitations:
- What could not be confirmed from sources

Sources:
- List all unique URLs"""
            },
            {
                "role": "user",
                "content": context  # actual scraped data goes here
            }
        ]
    )

    return response.choices[0].message.content  # extract text from response


def search_web(query, max_results=5):
    results = []
    # DDGS = DuckDuckGo Search, no API key needed
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r["title"],
                "snippet": r["body"],
                "url": r["href"]
            })
    return results


def get_search_terms(query):
    # ask LLM to expand user query into 3 focused search terms
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a research assistant. Given a user query, generate 3 specific search terms that are directly related to the topic. Terms must be closely related to the original query. Return only a JSON array of 3 strings. No explanation, no markdown."
            },
            {
                "role": "user",
                "content": f"Generate 3 search terms for: {query}"
            }
        ]
    )
    # parse JSON array from LLM response
    terms = json.loads(response.choices[0].message.content)
    return terms


def main():
    print("Scout - AI Web Research Agent")
    query = input("\nEnter your research topic: ").strip()

    print("\nGenerating search terms...")
    terms = get_search_terms(query)  # LLM generates 3 smart search terms

    print("\nSearching the web...")
    all_results = []
    for term in terms:
        results = search_web(term)  # search each term separately
        all_results.extend(results)

    # deduplicate by URL using a set
    seen = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen:
            unique_results.append(r)
            seen.add(r["url"])

    print("\nScraping web pages...")
    scraped_results = []
    for r in unique_results[:5]:  # cap at 5 pages for speed
        content = scrape_url(r["url"])

        if content:  # skip empty results (blocked/failed pages)
            scraped_results.append({
                "title": r["title"],
                "url": r["url"],
                "content": content
            })

    print("\nGenerating report...\n")
    report = generate_report(scraped_results)  # LLM synthesizes final report
    print(report)

    print("Do you want to save the report? y/n")
    ch = input("Enter choice: ").strip()
    if ch == 'y':
        save_report(report)  # write to report.md


main()
