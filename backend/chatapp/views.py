from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FriendRequest, Conversation, Message
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    FriendRequestSerializer,
    MessageSerializer,
)


# ==========================================================
# HOME
# ==========================================================

@api_view(["GET"])
def home(request):
    return Response({
        "app": "Chatlonic",
        "status": "Backend is running!"
    })


# ==========================================================
# REGISTER
# ==========================================================

@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response(
            {"message": "User registered successfully!"},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================
# USERS
# ==========================================================

class UserListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()


# ==========================================================
# SEND FRIEND REQUEST
# ==========================================================

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get("receiver_id")

        if not receiver_id:
            return Response(
                {"error": "receiver_id is required."},
                status=400,
            )

        try:
            receiver = User.objects.get(id=receiver_id)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=404,
            )

        if receiver == request.user:
            return Response(
                {"error": "You can't add yourself."},
                status=400,
            )

        if FriendRequest.objects.filter(
            sender=request.user,
            receiver=receiver,
            status="pending",
        ).exists():

            return Response(
                {"error": "Friend request already sent."},
                status=400,
            )

        FriendRequest.objects.create(
            sender=request.user,
            receiver=receiver,
            status="pending",
        )

        return Response(
            {"message": "Friend request sent."},
            status=201,
        )


# ==========================================================
# LIST FRIEND REQUESTS
# ==========================================================

class FriendRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        requests = FriendRequest.objects.filter(
            receiver=request.user,
            status="pending",
        )

        serializer = FriendRequestSerializer(
            requests,
            many=True,
        )

        return Response(serializer.data)


# ==========================================================
# FRIEND REQUEST COUNT
# ==========================================================

class FriendRequestCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        count = FriendRequest.objects.filter(
            receiver=request.user,
            status="pending",
        ).count()

        return Response({
            "count": count,
        })


# ==========================================================
# ACCEPT FRIEND REQUEST
# ==========================================================

class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):

        try:

            friend_request = FriendRequest.objects.get(
                id=request_id,
                receiver=request.user,
                status="pending",
            )

        except FriendRequest.DoesNotExist:

            return Response(
                {"error": "Friend request not found."},
                status=404,
            )

        friend_request.status = "accepted"
        friend_request.save()

        conversation = Conversation.objects.create()

        conversation.participants.add(
            friend_request.sender,
            friend_request.receiver,
        )

        return Response({
            "message": "Friend request accepted."
        })


# ==========================================================
# FRIEND LIST
# ==========================================================

class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        conversations = Conversation.objects.filter(
            participants=request.user,
        )

        friends = []

        for conversation in conversations:

            friend = conversation.participants.exclude(
                id=request.user.id
            ).first()

            if friend:

                friends.append({

                    "id": friend.id,
                    "username": friend.username,
                    "conversation_id": conversation.id,

                })

        return Response(friends)


# ==========================================================
# SEND MESSAGE
# ==========================================================

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        conversation_id = request.data.get("conversation_id")
        text = request.data.get("text")

        if not text:

            return Response(
                {"error": "Message cannot be empty."},
                status=400,
            )

        try:

            conversation = Conversation.objects.get(
                id=conversation_id
            )

        except Conversation.DoesNotExist:

            return Response(
                {"error": "Conversation not found."},
                status=404,
            )

        if request.user not in conversation.participants.all():

            return Response(
                {"error": "Unauthorized."},
                status=403,
            )

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=text,
        )

        serializer = MessageSerializer(message)

        return Response(serializer.data)


# ==========================================================
# GET CONVERSATION MESSAGES
# ==========================================================

class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        try:

            conversation = Conversation.objects.get(
                id=conversation_id
            )

        except Conversation.DoesNotExist:

            return Response(
                {"error": "Conversation not found."},
                status=404,
            )

        if request.user not in conversation.participants.all():

            return Response(
                {"error": "Access denied."},
                status=403,
            )

        serializer = MessageSerializer(
            conversation.messages.all().order_by("created_at"),
            many=True,
        )

        return Response(serializer.data)





class EditMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, message_id):
        try:
            message = Message.objects.get(
                id=message_id,
                sender=request.user,
            )
        except Message.DoesNotExist:
            return Response(
                {"error": "Message not found."},
                status=404,
            )

        text = request.data.get("text")

        if not text:
            return Response(
                {"error": "Message cannot be empty."},
                status=400,
            )

        message.text = text
        message.save()

        return Response({
            "message": "Message updated.",
            "text": message.text,
        })



class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, message_id):
        try:
            message = Message.objects.get(
                id=message_id,
                sender=request.user,
            )
        except Message.DoesNotExist:
            return Response(
                {"error": "Message not found."},
                status=404,
            )

        message.delete()

        return Response({
            "message": "Message deleted."
        })