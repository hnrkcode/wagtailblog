import re

from django import forms
from django.db import models
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from wagtail.search import index
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page, Orderable
from wagtail.snippets.models import register_snippet
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, HelpPanel

from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager


class BlogPostTag(TaggedItemBase):
    """Tags for blog posts"""
    content_object = ParentalKey(
        'BlogPost',
        related_name='blog_post_tag',
        on_delete=models.CASCADE
    )


class BlogPostKeyword(TaggedItemBase):
    """Meta keywords for posts"""
    content_object = ParentalKey(
        'BlogPost',
        related_name='blog_post_keyword',
        on_delete=models.CASCADE
    )


class BlogPageKeyword(TaggedItemBase):
    """Meta keywords for the blog index page"""
    content_object = ParentalKey(
        'BlogPage',
        related_name='blog_page_keyword',
        on_delete=models.CASCADE
    )


class BlogPage(Page):
    """Model for the blog index page"""

    # For the header on the blogpage.
    header_text = RichTextField(blank=True, null=True)
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # HTML meta tags for the blogpage.
    description = models.CharField(max_length=160, blank=True, null=True)
    keywords = ClusterTaggableManager(
        through=BlogPageKeyword,
        related_name='blog_page_keyword',
        blank=True
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('header_text', classname="full"),
            ImageChooserPanel('header_image'),
        ], heading="Header"),
        MultiFieldPanel([
            HelpPanel(template='help_panel/metatag_help.html'),
            FieldPanel('keywords', classname="full"),
            FieldPanel('description', classname="full"),
        ], heading="HTML meta tags"),
    ]


class BlogPost(Page):
    """Model for blog posts"""

    # Main blog post content and information.
    intro = models.CharField(max_length=150, blank=True, null=True)
    date = models.DateTimeField("Post date")
    text = RichTextField(blank=True)
    tags = ClusterTaggableManager(
        through=BlogPostTag,
        related_name='blog_post_tag',
        blank=True
    )

    # Show or hide the gallery.
    show = models.BooleanField(null=True)

    # HTML meta tags for the specific blog post.
    description = models.CharField(max_length=160, blank=True, null=True)
    keywords = ClusterTaggableManager(
        through=BlogPostKeyword,
        related_name='blog_post_keyword',
        blank=True
    )

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('text'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            HelpPanel(template='help_panel/content_help.html'),
            FieldPanel('intro'),
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('text'),
        ], heading="Content"),
        MultiFieldPanel([
            HelpPanel(template='help_panel/gallery_help.html'),
            FieldPanel('show', widget=forms.CheckboxInput),
            InlinePanel('gallery_images', label="Gallery images"),
        ], heading="Gallery"),
        MultiFieldPanel([
            HelpPanel(template='help_panel/metatag_help.html'),
            FieldPanel('keywords', classname="full"),
            FieldPanel('description', classname="full"),
        ], heading="HTML meta tags"),
    ]

    def intro_text(self):
        """Return intro text for the tiles"""
        if self.intro:
            return self.intro + "..."
        else:
            # If no intro, remove HTML and return the 150 first character
            # of the posts text as intro instead.
            return re.sub("<[^>]*>", "", self.text[:300])[:150] + "..."

    def featured_image(self):
        """Give posts a feature image."""
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    def next_post(self):
        """Return the next blog post."""
        posts = self.get_siblings().live().filter(
            blogpost__date__lte=timezone.now()).order_by('-blogpost__date')
        next = None
        for post in posts:
            if post.title == self.title:
                return next
            next = post
        return None

    def previous_post(self):
        """Return the previous blog post."""
        posts = self.get_siblings().live().filter(
            blogpost__date__lte=timezone.now()).order_by('blogpost__date')
        previous = None
        for post in posts:
            if post.title == self.title:
                return previous
            previous = post
        return None


class BlogPostGalleryImage(Orderable):
    """Image gallery feature for posts"""
    page = ParentalKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


class TagPage(Page):
    """Model for the tag index page"""

    def get_tags(self):
        # BUG: also shows tags from posts that aren't live.
        tags = BlogPost.tags.all()
        return tags

    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        blogposts = BlogPost.objects.live().filter(tags__name=tag)
        # Update template context
        context = super().get_context(request)
        context['blogposts'] = blogposts
        context['all_tags'] = BlogPost.tags.all()

        return context
