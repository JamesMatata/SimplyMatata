from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from works.models import Project


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['index', 'about', 'contact', 'works']

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Project.objects.filter(is_published=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at


SITEMAPS = {
    'static': StaticViewSitemap,
    'projects': ProjectSitemap,
}
