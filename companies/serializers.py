from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "user", "name", "location", "industry", "description", "logo", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]
