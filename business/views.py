from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BusinessForm
from .models import Business


@login_required
def register_business(request):

    if request.method == "POST":

        form = BusinessForm(request.POST)

        if form.is_valid():

            business = form.save(commit=False)
            business.owner = request.user
            business.save()

            return redirect("dashboard")

    else:
        form = BusinessForm()

    return render(request, "business/register_business.html", {"form": form})


# =========================================================
# PUBLIC CUSTOMER-FACING BUSINESS PAGE
# =========================================================

def public_business_page(request, slug):
    """
    Public profile page for a business, reachable by anyone via its
    shareable slug URL (e.g. /b/my-hotel/). Shows the approved reviews
    and a button for customers to leave their own review.
    """

    business = get_object_or_404(Business, slug=slug)

    reviews = business.review_set.filter(
        approved=True
    ).order_by("-created_at")

    total = business.review_set.count()

    avg_rating = None
    if total:
        ratings = business.review_set.values_list("rating", flat=True)
        avg_rating = round(sum(ratings) / total, 1)

    return render(
        request,
        "business/public_page.html",
        {
            "business": business,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "total": total,
        },
    )