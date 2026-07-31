
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from .models import Review
from business.models import Business
from .services import create_review_with_ai


# =========================================================
# HOME
# =========================================================

def home(request):

    return render(
        request,
        "reviews/home.html"
    )


# =========================================================
# REVIEW LIST
# =========================================================

@login_required
def review_list(request):

    business = get_object_or_404(
        Business,
        owner=request.user
    )

    reviews = Review.objects.filter(
        business=business
    ).order_by("-created_at")

    return render(
        request,
        "reviews/review_list.html",
        {
            "reviews": reviews
        }
    )


# =========================================================
# ADD REVIEW
# =========================================================

@login_required
def add_review(request):

    # Get logged-in owner's business
    business = get_object_or_404(
        Business,
        owner=request.user
    )

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name",
            ""
        ).strip()

        if not customer_name:
            customer_name = request.user.username

        rating = request.POST.get("rating")

        review_text = request.POST.get(
            "review_text",
            ""
        ).strip()

        review, error = create_review_with_ai(
            business,
            customer_name,
            rating,
            review_text,
        )

        if error:
            return render(
                request,
                "reviews/add_review.html",
                {"error": error}
            )

        return redirect(
            "review_list"
        )

    return render(
        request,
        "reviews/add_review.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    business = get_object_or_404(
        Business,
        owner=request.user
    )

    reviews = Review.objects.filter(
        business=business
    )

    total_reviews = reviews.count()

    positive_reviews = reviews.filter(
        sentiment="Positive"
    )

    negative_reviews = reviews.filter(
        sentiment="Negative"
    )

    spam_reviews = reviews.filter(
        spam=True
    )

    approved_reviews = reviews.filter(
        approved=True
    )

    pending_reviews = reviews.filter(
        approved=False,
        spam=False
    )

    context = {

        "business": business,

        "reviews": reviews,

        "total_reviews":
            total_reviews,

        "positive_reviews":
            positive_reviews,

        "positive_count":
            positive_reviews.count(),

        "negative_reviews":
            negative_reviews,

        "negative_count":
            negative_reviews.count(),

        "spam_reviews":
            spam_reviews,

        "spam_count":
            spam_reviews.count(),

        "approved_reviews":
            approved_reviews,

        "approved_count":
            approved_reviews.count(),

        "pending_reviews":
            pending_reviews,

        "pending_count":
            pending_reviews.count(),
    }

    return render(
        request,
        "reviews/dashboard.html",
        context
    )


# =========================================================
# SETTINGS
# =========================================================

@login_required
def settings_page(request):

    return render(
        request,
        "reviews/settings.html"
    )


# =========================================================
# APPROVE AI REPLY
# =========================================================

@login_required
def approve_reply(
    request,
    review_id
):

    business = get_object_or_404(
        Business,
        owner=request.user
    )

    review = get_object_or_404(
        Review,
        id=review_id,
        business=business
    )

    # Allow button/link request
    if request.method in ["POST", "GET"]:

        # The dashboard lets the owner tweak the AI reply in a
        # textarea right before approving it — capture that edit
        # if it was submitted, instead of silently discarding it.
        submitted_reply = request.POST.get("owner_reply", "").strip()

        if submitted_reply:
            review.owner_reply = submitted_reply

        review.approved = True

        # If owner edited the reply,
        # publish owner's version.
        if review.owner_reply:

            review.published_reply = (
                review.owner_reply
            )

        # Otherwise publish AI reply.
        elif review.ai_reply:

            review.published_reply = (
                review.ai_reply
            )

        review.save()

    return redirect(
        "review_list"
    )


# =========================================================
# REJECT AI REPLY
# =========================================================

@login_required
def reject_reply(
    request,
    review_id
):

    business = get_object_or_404(
        Business,
        owner=request.user
    )

    review = get_object_or_404(
        Review,
        id=review_id,
        business=business
    )

    if request.method in ["POST", "GET"]:

        review.approved = False

        review.published_reply = None

        review.save()

    return redirect(
        "review_list"
    )


# =========================================================
# EDIT AI REPLY
# =========================================================

@login_required
def edit_reply(
    request,
    review_id
):

    business = get_object_or_404(
        Business,
        owner=request.user
    )

    review = get_object_or_404(
        Review,
        id=review_id,
        business=business
    )

    if request.method == "POST":

        new_reply = request.POST.get(
            "ai_reply"
        )

        # Also accept owner_reply
        # if your HTML uses that name.
        if not new_reply:

            new_reply = request.POST.get(
                "owner_reply"
            )

        if new_reply:

            review.owner_reply = (
                new_reply.strip()
            )

            # Editing requires approval again
            review.approved = False

            review.published_reply = None

            review.save()

        return redirect(
            "review_list"
        )

    return render(
        request,
        "reviews/edit_reply.html",
        {
            "review": review
        }
    )


# =========================================================
# PUBLIC CUSTOMER REVIEW FORM (no login required)
# =========================================================

def public_add_review(request, slug):
    """
    Public, no-login review form for customers. Reachable via a
    business's shareable slug URL, e.g. /b/my-hotel/review/.
    """

    business = get_object_or_404(Business, slug=slug)

    error = None

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name",
            ""
        ).strip()

        rating = request.POST.get("rating")

        review_text = request.POST.get(
            "review_text",
            ""
        ).strip()

        review, error = create_review_with_ai(
            business,
            customer_name,
            rating,
            review_text,
        )

        if not error:
            return redirect(
                "business_public",
                slug=business.slug
            )

    return render(
        request,
        "reviews/public_review_form.html",
        {
            "business": business,
            "error": error,
        },
    )
