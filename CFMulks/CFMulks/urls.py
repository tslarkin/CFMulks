"""
URL configuration for CFMulks project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from Notebooks import views
from Notebooks.views import TagAutocomplete

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    #path('block/<int:notebook_id>/', views.BlockView.as_view(), name='block'),
    path("", views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('editfield/', views.editfield, name='editfield'),
    path('showfield/', views.showfield, name='showfield'),
    path('savefield/', views.savefield, name='savefield'),
    path('search/', views.search, name='search'),
    path('resources/', views.resources, name='resources'),
    path('biosketch/', views.biosketch, name='biosketch'),
    path('search/searchresults/', views.searchresults, name='searchresults'),
    #path('show_page/<int:pageid>', views.show_page, name='show_page'),
    path('partial_page/', views.partial_page, name='partial_page'),
    path('show_page_set/', views.show_page_set, name='show_page_set'),
    path('select2/', include('django_select2.urls', namespace='django_select2')),
    #path('edittags/<int:scan_id>', views.editTags, name='edittags'),
    #path('swipe-action', views.swipe_action, name='swipe-action'),
    path(
        'tag-autocomplete/',
        views.TagAutocomplete.as_view(),
        name='tag-autocomplete',
    ),
    path('tag_post', views.TagPost, name="tag_post"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
