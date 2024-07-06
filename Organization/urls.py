from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserRegistration, UserLogin, UserDetail, OrganisationList, OrganisationDetail, CreateOrganisation, AddUserToOrganisation

urlpatterns = [
    path('auth/register/', UserRegistration.as_view(), name='register'),
    path('auth/login/', UserLogin.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/<str:id>/', UserDetail.as_view(), name='user_detail'),
    path('api/organisations/', OrganisationList.as_view(), name='organisation_list'),
    path('api/organisations/<str:orgId>/', OrganisationDetail.as_view(), name='organisation_detail'),
    path('api/createorganisations/', CreateOrganisation.as_view(), name='create_organisation'),
    path('api/organisations/<str:orgId>/users/', AddUserToOrganisation.as_view(), name='add_user_to_organisation'),
]