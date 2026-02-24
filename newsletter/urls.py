from django.urls import path, include

from newsletter import views
from newsletter.apps import NewsletterConfig
from newsletter.views import NewsletterListView, NewsletterCreateView, NewsletterDetailView, NewsletterDeleteView, \
    NewsletterUpdateView, MessageCreateView, MessageDeleteView, MessageDetailView, MessageUpdateView

app_name = NewsletterConfig.name

urlpatterns = [
    path('', NewsletterListView.as_view(), name='newsletter_list'),
    path('create/', NewsletterCreateView.as_view(), name='newsletter_form'),
    path('<int:pk>/delete/', NewsletterDeleteView.as_view(), name='newsletter_delete'),
    path('<int:pk>/details/', NewsletterDetailView.as_view(), name='newsletter_details'),
    path('<int:pk>/update/', NewsletterUpdateView.as_view(), name='newsletter_update'),
    # path('message/', MessageListView.as_view(), name='newsletter_list'),
    path('message/create/', MessageCreateView.as_view(), name='message_form'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('message/<int:pk>/details/', MessageDetailView.as_view(), name='message_details'),
    path('message/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('<int:pk>/send/', views.send_newsletter_view, name='send_newsletter'),
]
