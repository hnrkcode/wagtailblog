from django import forms
from django.db import models
from django.utils import timezone

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.models import Document
from wagtail.documents.edit_handlers import DocumentChooserPanel

from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from blog.models import BlogPost


class HomePageKeywords(TaggedItemBase):
    """HTML meta tag keywords for the homepage"""
    content_object = ParentalKey(
        'HomePage',
        related_name='keyword_items',
        on_delete=models.CASCADE
    )


class HomePage(Page):
    """Model for the websites homepage"""

    # For the header on the homepage.
    header_header = models.CharField(max_length=100, blank=False)
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    header_body = RichTextField(blank=False)

    # These will affect the whole site. See wagtailblog/context_processor.py.
    logo_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    favicon_file = models.ForeignKey(
        'wagtaildocs.Document',
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    footer = RichTextField(blank=False)
    instagram = models.URLField(blank=False)

    # HTML meta tags for the homepage.
    keywords = ClusterTaggableManager(through=HomePageKeywords, blank=True)
    description = models.CharField(max_length=160, blank=True, null=True)

    # Instagram widget on the homepage.
    show_widget = models.BooleanField(null=True)
    instagram_widget = models.TextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            HelpPanel(template='help_panel/branding_help.html'),
            ImageChooserPanel('logo_image'),
            DocumentChooserPanel('favicon_file'),
        ], heading="Branding"),
        MultiFieldPanel([
            HelpPanel(template='help_panel/metatag_help.html'),
            FieldPanel('keywords'),
            FieldPanel('description'),
        ], heading="HTML meta tags"),
        MultiFieldPanel([
            FieldPanel('header_header', classname='title'),
            FieldPanel('header_body'),
            ImageChooserPanel('header_image'),
        ], heading="Header"),
        MultiFieldPanel([
            HelpPanel(template='help_panel/widget_help.html'),
            FieldPanel('show_widget', widget=forms.CheckboxInput),
            FieldPanel('instagram_widget'),
        ], heading="Instagram widget"),
        MultiFieldPanel([
            HelpPanel(template='help_panel/footer_help.html'),
            FieldPanel('footer'),
            FieldPanel('instagram'),
        ], heading="Footer"),
    ]

    def latest_posts(self):
        """Get the six latest published posts"""

        posts = BlogPost.objects.live().filter(
            date__lte=timezone.now()).order_by('-date')[:6]

        return posts

    def get_context(self, request):
        """Context variables for the homepage template"""

        context = super().get_context(request)
        context['latest_posts'] = self.latest_posts
        context['show_widget'] = self.show_widget
        context['instagram_widget'] = self.instagram_widget
        context['homepage_header_image'] = self.header_image.file.url

        return context
