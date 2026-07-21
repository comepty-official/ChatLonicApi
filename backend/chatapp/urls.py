from django.urls import path

from .views import (
    UserListView,
    FriendsListView,
    SendFriendRequestView,
    FriendRequestListView,
    AcceptFriendRequestView,
    FriendRequestCountView,
    ConversationMessagesView,
    SendMessageView,
    EditMessageView,
    DeleteMessageView,
)

urlpatterns = [
    # Users
    path(
        "users/",
        UserListView.as_view(),
        name="users",
    ),

    # Friends
    path(
        "friends/",
        FriendsListView.as_view(),
        name="friends",
    ),

    # Friend Requests
    path(
        "friend-request/",
        SendFriendRequestView.as_view(),
        name="send_friend_request",
    ),


    path(
        "message/<int:message_id>/edit/",
        EditMessageView.as_view(),
    ),

    path(
        "message/<int:message_id>/delete/",
        DeleteMessageView.as_view(),
    ),


    path(
        "friend-requests/",
        FriendRequestListView.as_view(),
        name="friend_requests",
    ),

    path(
        "friend-request/<int:request_id>/accept/",
        AcceptFriendRequestView.as_view(),
        name="accept_friend_request",
    ),

    path(
        "friend-request-count/",
        FriendRequestCountView.as_view(),
        name="friend_request_count",
    ),

    # Messages
    path(
        "conversation/<int:conversation_id>/messages/",
        ConversationMessagesView.as_view(),
        name="conversation_messages",
    ),

    path(
        "messages/",
        SendMessageView.as_view(),
        name="send_message",
    ),
]