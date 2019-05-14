import os
from home.models import HomePage
from wagtailblog.settings.base import STATIC_URL

def globals(request):
    """Defines global context variables for all templates."""

    try:
        context = {
            'website_name': HomePage.objects.first().title,
            'website_instagram': HomePage.objects.first().instagram,
            'website_footer': HomePage.objects.first().footer,
            'website_favicon': HomePage.objects.first().favicon_file.file.url,
            'website_logo': HomePage.objects.first().logo_image,
        }
    except AttributeError:
        context = {
            'website_name': 'Default name',
            'website_instagram': '#',
            'website_footer': 'Default footer',
            'website_favicon': '',
            'website_logo': '',
        }

    return context

def default_images(request):
    """Default images for preview and feature images"""

    context = {
        'default_preview': os.path.join(STATIC_URL, 'images/default_feature_preview_image.jpg'),
        'default_feature': os.path.join(STATIC_URL, 'images/default_feature_image.jpg'),
    }

    return context
