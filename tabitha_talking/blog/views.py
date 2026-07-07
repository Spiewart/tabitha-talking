from django.shortcuts import render

from .models import BlogPage
from .search_forms import BlogSearchForm


def search_blog(request):
    """Search blog posts by title, intro, body, or tag."""
    form = BlogSearchForm()
    results = []
    query_string = ""
    tag_string = ""

    tag = request.GET.get("tag", "").strip()
    if request.method == "GET" and tag:
        tag_string = tag
        results = BlogPage.objects.live().public().filter(tags__slug=tag_string)
        if not results.exists():
            results = (
                BlogPage.objects.live()
                .public()
                .filter(
                    tags__name__iexact=tag_string,
                )
            )
    elif request.method == "GET" and request.GET.get("query"):
        form = BlogSearchForm(request.GET)
        if form.is_valid():
            query_string = form.cleaned_data["query"]
            results = BlogPage.objects.live().public().search(query_string)

    context = {
        "form": form,
        "results": results,
        "query_string": query_string,
        "tag_string": tag_string,
        "result_count": len(results),
    }
    return render(request, "blog/search_results.html", context)
