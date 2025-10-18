from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile,Messages
from .serializers import ProfileSerializer,MessageSerializer

class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if Profile.objects.filter(user=user).exists():
            raise ValueError("You already have a profile.")
        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        user = request.user
        if Profile.objects.filter(user=user).exists():
            return Response(
                {"detail": "You already have a profile. You can only update it."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

class ProfileListView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class ReceivedMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Messages.objects.filter(receiver=self.request.user).order_by('-created_at')

class SentMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Messages.objects.filter(sender=self.request.user).order_by('-created_at')

class MessageStatusUpdateView(views.APIView):
    def post(self, request, message_id, action):
        try:
            message = Messages.objects.get(id=message_id, receiver=request.user)

            if action == "accept":
                message.status = "accepted"
                message.save()
                return Response({"message": "Message accepted successfully."}, status=status.HTTP_200_OK)

            elif action == "reject":
                message.status = "rejected"
                message.save()
                return Response({"message": "Message rejected successfully."}, status=status.HTTP_200_OK)

            else:
                return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        except Messages.DoesNotExist:
            return Response({"error": "Message not found or not yours."}, status=status.HTTP_404_NOT_FOUND)