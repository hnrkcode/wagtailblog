from django.db import models
from django.utils import timezone
from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from wagtail.core.models import Page
from wagtail.search.models import Query

from blog.models import BlogPost
from home.models import HomePage


def search(request):
    search_query = request.GET.get('q', None)
    search_hits = None
    page = request.GET.get('page', 1)

    # Search through posts title, intro, body & tags and order by newest first.
    if search_query:
        search_results = BlogPost.objects.live().filter(
            date__lte=timezone.now()).filter(
            models.Q(title__icontains=search_query) |
            models.Q(intro__icontains=search_query) |
            models.Q(text__icontains=search_query) |
            models.Q(tags__name__icontains=search_query)
            ).order_by('-date').distinct()  # Prevent dublicate results.
        search_hits = len(search_results)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = BlogPost.objects.none()

    # Pagination
    paginator = Paginator(search_results, 9)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
        'search_hits': search_hits,
    })
