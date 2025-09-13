from django.urls import path
from .views import CompanyCreateView, UserCompaniesListView, CompanyDetailView, CompanyListView, CompanyDetailsView

urlpatterns = [
    path('companies/create/', CompanyCreateView.as_view(), name='company-create'),
    path('companies/', UserCompaniesListView.as_view(), name='user-companies'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),

    path("companies/list/", CompanyListView.as_view(), name="company-list"),
    path("companies/details/<int:id>/", CompanyDetailsView.as_view(), name="company-details"),
]
