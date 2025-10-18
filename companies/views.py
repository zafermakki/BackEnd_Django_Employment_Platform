from rest_framework import generics, permissions, views
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from .models import Company, JobAd, JobApplication, Message,WorkSession
from .serializers import CompanySerializer, JobAdSerializer, JobApplicationSerializer,AllJobApplicationSerializer,ApplyJobApplicationSerializer,MessageSerializer,WorkSessionSerializer,WorkSessionTimeSerializer
from rest_framework.exceptions import ValidationError

class CompanyCreateView(generics.CreateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserCompaniesListView(generics.ListAPIView):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Company.objects.filter(user=self.request.user)


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Company.objects.filter(user=self.request.user)

# all companies
class CompanyListView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

# the detail of one company
class CompanyDetailsView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_field = "id"  

# for Advertisements

class JobAdCreateView(generics.CreateAPIView):
    serializer_class = JobAdSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        company_id = self.request.data.get("company_id")
        if not company_id:
            raise ValidationError({"company_id": "You must select a company to publish this advertisement."})

        try:
            company = Company.objects.get(id=company_id, user=self.request.user)
        except Company.DoesNotExist:
            raise ValidationError({"company_id": "Invalid company or you don't own this company."})

        serializer.save(company=company)

class UserJobAdsListAdvertisementsView(generics.ListCreateAPIView):
    serializer_class = JobAdSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return JobAd.objects.filter(company__user=self.request.user)

class UserJobAdUpdateDeleteAdvertisementsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobAdSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    def get_queryset(self):
        return JobAd.objects.filter(company__user=self.request.user)

class JobListView(generics.ListAPIView):
    serializer_class = JobAdSerializer
    def get_queryset(self):
        return JobAd.objects.filter(job_type='job')

class InternshipListView(generics.ListAPIView):
    serializer_class = JobAdSerializer
    def get_queryset(self):
        return JobAd.objects.filter(job_type='internship')

class ApplyForJobView(generics.CreateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = ApplyJobApplicationSerializer 

class UserJobApplicationsListView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    def get_queryset(self):
        return JobApplication.objects.filter(applicant=self.request.user)

class UserJobApplicationDeleteView(generics.DestroyAPIView):
    serializer_class = JobApplicationSerializer
    def get_queryset(self):
        return JobApplication.objects.filter(applicant=self.request.user)

class CompanyApplicationsView(generics.ListAPIView):
    serializer_class = AllJobApplicationSerializer

    def get_queryset(self):
        return JobApplication.objects.filter(
            job_ad__company__user=self.request.user
        ).order_by("-applied_at")


class UpdateApplicationStatusView(APIView):

    def post(self, request, pk):
        try:
            application = JobApplication.objects.get(
                id=pk,
                job_ad__company__user=request.user
            )
        except JobApplication.DoesNotExist:
            return Response(
                {"detail": "Application not found or unauthorized."},
                status=status.HTTP_404_NOT_FOUND
            )

        status_choice = request.data.get("status")
        if status_choice not in dict(JobApplication.STATUS_CHOICES):
            return Response(
                {"detail": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = status_choice
        application.save()

        applicant_name = application.full_name
        applicant_email = application.email
        job_title = application.job_ad.title
        company_name = application.job_ad.company.name    

        # ==== send email =====
        subject = "Your Job Application Status Update"

        if status_choice == "accepted":
            message = (
                f"Dear {applicant_name},\n\n"
                f"Congratulations! Your application for the position '{job_title}' "
                f"at {company_name} has been accepted.\n\n"
                f"Our team will contact you soon with further details.\n\n"
                f"Best regards,\n"
                f"{company_name} Recruitment Team"
            )
        elif status_choice == "rejected":
            message = (
                f"Dear {applicant_name},\n\n"
                f"Thank you for applying for the position '{job_title}' "
                f"at {company_name}.\n\n"
                f"After careful consideration, we regret to inform you that your application "
                f"was not selected for further process.\n\n"
                f"We wish you the best in your future endeavors.\n\n"
                f"Sincerely,\n"
                f"{company_name} Recruitment Team"
            )
        else:
            message = (
                f"Dear {applicant_name},\n\n"
                f"Your application for the position '{job_title}' "
                f"at {company_name} is currently under review.\n\n"
                f"We will get back to you soon with an update.\n\n"
                f"Kind regards,\n"
                f"{company_name} Recruitment Team"
            )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [applicant_email],
                fail_silently=False,
            )
        except Exception as e:
            print("❌ Email sending failed:", e)
        
        Message.objects.create(
            user=application.applicant,
            job_application=application,
            subject=subject,
            content=message
        )
 
        return Response(
            AllJobApplicationSerializer(application).data,
            status=status.HTTP_200_OK
        )

class UserMessagesView(APIView):

    def get(self, request):
        messages = Message.objects.filter(user=request.user).order_by('-created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StartWorkView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, company_id):
        company = Company.objects.get(id=company_id)
        existing_session = WorkSession.objects.filter(employee=request.user, company=company, end_time__isnull=True).first()
        if existing_session:
            return Response({"error": "You already have an active session."}, status=status.HTTP_400_BAD_REQUEST)
        
        session = WorkSession.objects.create(employee=request.user, company=company)
        serializer = WorkSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class EndWorkView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, company_id):
        company = Company.objects.get(id=company_id)
        session = WorkSession.objects.filter(employee=request.user, company=company, end_time__isnull=True).first()
        if not session:
            return Response({"error": "No active session found."}, status=status.HTTP_400_BAD_REQUEST)
        
        session.end_time = timezone.now()
        session.save()
        serializer = WorkSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserTimeWorkSessionsView(generics.ListAPIView):
    serializer_class = WorkSessionTimeSerializer

    def get_queryset(self):
        user = self.request.user
        return WorkSession.objects.filter(employee=user).select_related('company').order_by('-start_time')