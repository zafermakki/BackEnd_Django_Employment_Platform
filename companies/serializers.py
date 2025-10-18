from rest_framework import serializers
from .models import Company, JobAd, JobApplication,Message,WorkSession

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "user", "name", "location", "industry", "description", "logo", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]

class JobAdSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = JobAd
        fields = "__all__"
        read_only_fields = ["company", "created_at", "updated_at"] 

class ApplyJobApplicationSerializer(serializers.ModelSerializer):
    job_ad = serializers.PrimaryKeyRelatedField(
        queryset=JobAd.objects.all()
    )

    class Meta:
        model = JobApplication
        fields = ['id', 'job_ad', 'full_name', 'email', 'cv', 'cover_letter', 'status', 'applied_at']
        read_only_fields = ['status', 'applied_at']

    def create(self, validated_data):
        user = self.context['request'].user
        job_ad = validated_data['job_ad']

        if JobApplication.objects.filter(applicant=user, job_ad=job_ad).exists():
            raise serializers.ValidationError("You have already applied for this job.")

        validated_data['applicant'] = user
        return super().create(validated_data)


class JobApplicationSerializer(serializers.ModelSerializer):
    job_ad = JobAdSerializer(read_only=True)
    class Meta:
        model = JobApplication
        fields = ['id', 'job_ad', 'full_name', 'email', 'cv', 'cover_letter', 'status', 'applied_at']
        read_only_fields = ['status', 'applied_at']

    def create(self, validated_data):
        user = self.context['request'].user
        job_ad = validated_data['job_ad']

        if JobApplication.objects.filter(applicant=user, job_ad=job_ad).exists():
            raise serializers.ValidationError("you have made a request !!.")

        validated_data['applicant'] = user
        return super().create(validated_data)

class AllJobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job_ad.title", read_only=True)
    company_name = serializers.CharField(source="job_ad.company.name", read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "id", "job_ad", "job_title", "company_name",
            "full_name", "email", "cv", "cover_letter",
            "status", "applied_at"
        ]
        read_only_fields = ["job_ad", "full_name", "email", "cv", "cover_letter", "applied_at"]

class MessageSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job_application.job_ad.title", read_only=True)
    company_name = serializers.CharField(source="job_application.job_ad.company.name", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "subject", "content", "created_at", "job_title", "company_name"]

class WorkSessionSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = WorkSession
        fields = ['id', 'employee', 'company', 'start_time', 'end_time', 'duration']

    def get_duration(self, obj):
        return str(obj.duration())

class WorkSessionTimeSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    duration_days = serializers.SerializerMethodField()

    class Meta:
        model = WorkSession
        fields = ['id', 'company_name', 'start_time', 'end_time', 'duration_days']

    def get_duration_days(self, obj):
        duration = obj.duration()
        return duration.days