import os

from django.conf import settings

from .models import Review

from ai_engine.services import (
    generate_rag_reply,
    detect_spam,
    detect_duplicate_review,
    analyze_sentiment,
)


def _load_knowledge_base_context():
    """Load the hotel/business knowledge base used to ground the AI reply."""

    knowledge_file = os.path.join(
        settings.BASE_DIR,
        "knowledge_base.txt",
    )

    if not os.path.exists(knowledge_file):
        return ""

    from ai_engine.services import load_and_split_text

    chunks = load_and_split_text(knowledge_file)

    return "\n\n".join(chunk.page_content for chunk in chunks)


def create_review_with_ai(business, customer_name, rating, review_text):
    """
    Validate a submitted review, run spam/duplicate/sentiment checks,
    generate an AI reply, and save the Review.

    Returns a tuple: (review_or_None, error_message_or_None)
    """

    customer_name = (customer_name or "").strip()
    review_text = (review_text or "").strip()

    if not customer_name:
        return None, "Please enter your name."

    if not rating:
        return None, "Please select a rating."

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return None, "Invalid rating."

    if rating < 1 or rating > 5:
        return None, "Rating must be between 1 and 5."

    if not review_text:
        return None, "Please enter a review."

    # ---------------------------------------------------------
    # DUPLICATE DETECTION
    # ---------------------------------------------------------

    existing_reviews = Review.objects.filter(business=business)

    is_duplicate, duplicate_message = detect_duplicate_review(
        review_text,
        existing_reviews,
    )

    if is_duplicate:
        return None, duplicate_message

    # ---------------------------------------------------------
    # SPAM DETECTION
    # ---------------------------------------------------------

    is_spam = detect_spam(review_text)

    # ---------------------------------------------------------
    # SENTIMENT ANALYSIS
    # ---------------------------------------------------------

    sentiment = analyze_sentiment(review_text)

    # ---------------------------------------------------------
    # CREATE REVIEW
    # ---------------------------------------------------------

    review = Review.objects.create(
        business=business,
        customer_name=customer_name,
        rating=rating,
        review_text=review_text,
        sentiment=sentiment,
        spam=is_spam,
        spam_reason="Spam content detected" if is_spam else None,
        approved=False,
    )

    # ---------------------------------------------------------
    # AI REPLY
    # ---------------------------------------------------------

    if not is_spam:
        try:
            context = _load_knowledge_base_context()
            review.ai_reply = generate_rag_reply(review_text, context)
        except Exception as e:
            print("AI REPLY ERROR:", e)
            review.ai_reply = (
                "AI reply could not be generated. Please try again."
            )
    else:
        review.ai_reply = (
            "This review was detected as spam and requires manual review."
        )

    review.approved = False
    review.published_reply = None
    review.save()

    return review, None
