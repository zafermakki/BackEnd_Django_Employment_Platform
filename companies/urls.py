from django.urls import path
from .views import CompanyCreateView, UserCompaniesListView, CompanyDetailView, CompanyListView, CompanyDetailsView,JobAdCreateView,UserJobAdsListAdvertisementsView,UserJobAdUpdateDeleteAdvertisementsView,JobListView,InternshipListView,ApplyForJobView,UserJobApplicationsListView,UserJobApplicationDeleteView,CompanyApplicationsView, UpdateApplicationStatusView,UserMessagesView,StartWorkView, EndWorkView,UserTimeWorkSessionsView,ActiveWorkSessionsView, CompanySearchView

urlpatterns = [
    path('companies/create/', CompanyCreateView.as_view(), name='company-create'),
    path('companies/', UserCompaniesListView.as_view(), name='user-companies'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),

    path("companies/list/", CompanyListView.as_view(), name="company-list"),
    path("companies/details/<int:id>/", CompanyDetailsView.as_view(), name="company-details"),

    path("jobads/create/", JobAdCreateView.as_view(), name="jobad-create"),
    path('my-Advertisements/', UserJobAdsListAdvertisementsView.as_view(), name='user-jobads-list'),
    path('my-Advertisements/edit/delete/<int:id>/', UserJobAdUpdateDeleteAdvertisementsView.as_view(), name='user-jobads-update'),
    path('jobs/', JobListView.as_view(), name='jobs-list'),
    path('internships/', InternshipListView.as_view(), name='internships-list'),
    path('apply/', ApplyForJobView.as_view(), name='apply-job'),
    path("my-applications/", UserJobApplicationsListView.as_view(), name="my-applications"),
    path("my-applications/<int:pk>/delete/", UserJobApplicationDeleteView.as_view(), name="delete-application"),
    path("applications/", CompanyApplicationsView.as_view(), name="company-applications"),
    path("applications/<int:pk>/status/", UpdateApplicationStatusView.as_view(), name="update-application-status"),
    path("messages/", UserMessagesView.as_view(), name="user-messages"),
    path('companies/<int:company_id>/start-work/', StartWorkView.as_view(), name='start_work'),
    path('companies/<int:company_id>/end-work/', EndWorkView.as_view(), name='end_work'),
    path('companies/user/time/work-sessions/', UserTimeWorkSessionsView.as_view(), name='user-work-sessions'),
    path('companies/active-sessions/', ActiveWorkSessionsView.as_view(), name='active-sessions'),
    path('companies/search/', CompanySearchView.as_view(), name='company-search'),
]
