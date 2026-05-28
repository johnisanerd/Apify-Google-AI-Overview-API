"""
Google AI Overview API: A Quick Start Example
See more at: https://apify.com/johnvc/Google-AI-Overview-API?fpr=9n7kx3
Input schema: https://apify.com/johnvc/Google-AI-Overview-API/input-schema?fpr=9n7kx3

This script shows how to call the Google AI Overview API on Apify from Python
and read its structured JSON output. The API returns Google's AI Overview (the
AI-generated answer shown atop search results) for a query, plus the sources it
cites. It exercises several input parameters so you can see what is configurable,
while keeping the run small so your first call stays cheap.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3
"""

import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

# Initialize the Apify client with your API token (read from .env)
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

# Build the Actor input.
# Inputs are kept small (a single query) to keep this first run inexpensive:
# one query bills one retrieval, and two only when Google defers generation.
# Raise these once you have your own API key and know your budget. To look up
# several questions in one run, pass "queries": ["q1", "q2", ...] instead.
run_input = {
    "query": "what is retrieval augmented generation",
    "gl": "us",   # country (ISO 3166-1), e.g. us, gb, ca
    "hl": "en",   # language (ISO 639-1); AI Overviews are English-only
    # "location": "Austin, Texas, United States",  # optional, narrows results
}

# Run the Actor and wait for it to finish
run = client.actor("johnvc/Google-AI-Overview-API").call(run_input=run_input)

# Read structured results from the run's default dataset (one row per query)
items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(f"Returned {len(items)} item(s).\n")

# Show a few key fields from each item.
for item in items:
    if item.get("result_type") != "ai_overview":
        print("Note:", item.get("error_message") or item.get("note"))
        continue

    print(f"Query: {item['query']}")
    print(
        f"AI Overview present: {item['ai_overview_present']} "
        f"(retrievals used: {item['retrievals_used']})"
    )

    # The answer is a list of text blocks; print the first paragraph snippet.
    first_snippet = next(
        (b.get("snippet") for b in item.get("text_blocks", []) if b.get("snippet")),
        None,
    )
    if first_snippet:
        print(f"Answer: {first_snippet[:200]}...")

    # Cited sources behind the overview.
    references = item.get("references", [])
    if references:
        print("Sources:")
        for ref in references[:5]:
            print(f"  - {ref.get('title')} ({ref.get('source')}): {ref.get('link')}")
    print()
