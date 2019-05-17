import re
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from wagtail.core.models import Page

from .models import BlogPage, BlogPost
from home.models import HomePage


class BlogPageView(ListView):
    model = BlogPost
    template_name = 'blog/blog_page.html'
    paginate_by = 12

    def get_queryset(self):
        return BlogPost.objects.live().filter(
            date__lte=timezone.now()).order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keywords'] = BlogPage.objects.first().keywords.all()
        context['description'] = BlogPage.objects.first().description
        context['title'] = BlogPage.objects.first().title
        context['header_image'] = BlogPage.objects.first().header_image.file.url
        context['header_text'] = BlogPage.objects.first().header_text
        context['object'] = Page.objects.get(slug='blog')
        return context


class BlogPostView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_post.html'

    def get_queryset(self):
        return BlogPost.objects.live().filter(
            date__lte=timezone.now()).order_by("-date")


class TagPageView(ListView):
    model = BlogPost
    template_name = 'blog/tag_page.html'
    paginate_by = 12

    def get_queryset(self):
        return BlogPost.objects.live().filter(
            tags__name__iexact=self.kwargs['tag'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_tag'] = self.unslugify(self.kwargs['tag'])
        context['all_tags'] = BlogPost.tags.all()
        return context

    def unslugify(self, slug):
        """Convert slug to string."""
        return re.sub('-', ' ', slug)
