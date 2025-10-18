from django.urls import path
from .views import ProfileCreateView, ProfileUpdateView, ProfileListView,SendMessageView,ReceivedMessagesView,SentMessagesView, MessageStatusUpdateView

urlpatterns = [
    path('create/', ProfileCreateView.as_view(), name='create-profile'),
    path('update/', ProfileUpdateView.as_view(), name='update-profile'),
    path('list/', ProfileListView.as_view(), name='list-profile'),
    path('messages/send/', SendMessageView.as_view(), name='send-message'),
    path('messages/received/', ReceivedMessagesView.as_view(), name='received-messages'),
    path('messages/sent/', SentMessagesView.as_view(), name='sent-messages'),
    path('messages/<int:message_id>/<str:action>/', MessageStatusUpdateView.as_view(), name='message-status'),
]
