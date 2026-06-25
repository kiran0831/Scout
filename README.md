# Scout 🔍
AI-powered web research agent that searches, scrapes, and summarizes topics into structured reports.

## What it does
- Takes a research topic from you
- Generates 3 smart search terms using AI
- Searches the web via DuckDuckGo
- Scrapes actual page content
- Synthesizes everything into a clean research report
- Optionally saves report as `report.md`

## Tech Stack
- **Groq** — LLM inference (Llama 3.3 70b)
- **DDGS** — DuckDuckGo search
- **BeautifulSoup** — web scraping
- **requests** — HTTP calls
- **python-dotenv** — API key management

## Setup

1. Clone the repo
   git clone https://github.com/yourusername/scout.git
   cd scout

2. Install dependencies
   pip install -r requirements.txt

3. Create a `.env` file
   GROQ_API_KEY=your_groq_api_key_here

4. Run
   python scout.py

## Usage
Enter any research topic when prompted:
   Enter your research topic: impact of AI on jobs

Scout will search, scrape, and generate a full report automatically.

## Project Structure
   ```
   scout/
   ├── scout.py          # main agent
   ├── requirements.txt  # dependencies
   ├── .env              # API keys (never commit this)
   ├── .gitignore        # ignores .env
   └── README.md
   ```

## Notes
- Get your free Groq API key at console.groq.com
- Reports are saved as report.md in the same directory
