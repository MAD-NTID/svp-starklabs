from django.urls import path, include

from cards.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('cards.urls')),
]
