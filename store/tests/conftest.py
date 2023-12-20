import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def authendicate_admin(api_client):
    def do_authendicate_admin(is_staff=False):
        api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_authendicate_admin


# @pytest.fixture(autouse=True)
# def disable_warnings():
#     import warnings
#     warnings.filterwarnings("ignore", category=DeprecationWarning)
