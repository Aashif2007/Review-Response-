import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# NOTE: previously this module raised a ValueError at IMPORT time if the
# key was missing, which crashed the entire Django app (every request,
# even ones unrelated to AI replies) whenever a developer hadn't set up
# a .env file. The client and heavy ML models below are now created
# lazily, on first use, so the app can start and run normally and only
# the AI-reply feature degrades gracefully if it's not configured.

_client = None
_sentiment_analyzer = None


def _get_client():
    global _client

    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Add it to a .env file "
                "to enable AI-generated replies."
            )

        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)

    return _client


def _get_sentiment_analyzer():
    global _sentiment_analyzer

    if _sentiment_analyzer is None:
        from transformers import pipeline

        _sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )

    return _sentiment_analyzer


# =========================================================
# 1. LOAD AND SPLIT KNOWLEDGE BASE
# =========================================================
def load_and_split_text(file_path):

    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    loader = TextLoader(
        file_path,
        encoding="utf-8"
    )

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=80,
        chunk_overlap=0
    )

    chunks = splitter.split_documents(
        documents
    )

    return chunks


# =========================================================
# 2. CREATE EMBEDDINGS
# =========================================================

def create_embeddings():

    from langchain_community.embeddings import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings


# =========================================================
# 3. SENTIMENT ANALYSIS
# =========================================================

def analyze_sentiment(review_text):

    try:
        analyzer = _get_sentiment_analyzer()
        result = analyzer(review_text)[0]

        if result["label"] == "POSITIVE":
            return "Positive"

        return "Negative"

    except Exception as e:
        # Fall back to a lightweight keyword heuristic if the
        # transformer model can't be loaded (e.g. no internet access,
        # missing dependency, out of memory, etc.) so review
        # submission never breaks because of this.
        print("SENTIMENT ANALYSIS ERROR:", e)

        text = review_text.lower()

        negative_words = [
            "bad", "worst", "terrible", "awful", "poor", "rude",
            "dirty", "horrible", "disappointing", "never again",
        ]

        if any(word in text for word in negative_words):
            return "Negative"

        return "Positive"


# =========================================================
# 4. SPAM DETECTION
# =========================================================

def detect_spam(review_text):

    spam_words = [
        "buy now",
        "click here",
        "free money",
        "visit my website",
        "http://",
        "https://",
        "win money",
        "make money fast"
    ]

    text = review_text.lower()

    for word in spam_words:

        if word in text:
            return True

    return False


# =========================================================
# 5. DUPLICATE REVIEW DETECTION
# =========================================================

def detect_duplicate_review(
    review_text,
    existing_reviews
):

    new_text = review_text.strip().lower()

    for review in existing_reviews:

        old_text = review.review_text.strip().lower()

        if new_text == old_text:

            return True, "Duplicate review detected"

    return False, ""


# =========================================================
# 6. GENERATE AI REPLY USING RETRIEVED CONTEXT
# =========================================================

def generate_rag_reply(review_text, context):

    prompt = f"""
You are a customer-service assistant for a business.

Write a polite, professional reply to the customer.

Use ONLY the business information provided below.
Do not invent policies or information.

Business information:
{context}

Customer review:
{review_text}

Rules:
- Reply in the SAME language the customer used in their review.
  If the review is in Urdu, reply in Urdu. If it's in English, reply in English.
- Keep the reply short.
- Be friendly and professional.
- If the customer has a complaint, acknowledge it.
- Do not mention AI, Gemini, FAISS, or the knowledge base.
- Return only the reply.
"""

    client = _get_client()

    response = client.models.generate_content(
       model="gemini-flash-latest",
       contents=prompt
   )

    return response.text.strip()
