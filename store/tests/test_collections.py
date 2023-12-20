from django.contrib.auth.models import User
from rest_framework import status
import pytest
from model_bakery import baker
from store.models import Collection


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post("/store/collections/", collection)
    return do_create_collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_return_401(self, create_collection):
        response = create_collection({"title": "a"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_return_403(self, create_collection, authendicate_admin):
        authendicate_admin()

        response = create_collection({"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_and_invalid_request_return_400(self, create_collection, authendicate_admin):
        authendicate_admin(True)

        response = create_collection({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_if_user_is_admin_and_valid_request_return_201(self, create_collection, authendicate_admin):
        authendicate_admin(True)

        response = create_collection({"title": "a"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetriveCollection:

    def test_if_collection_exists_return_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f"/store/collections/{collection.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collection.id,
            "title": collection.title,
            "products_count": 0
        }

# @pytest.mark.django_db
# class TestCreateCollection:
#     def test_if_user_is_anonymous_return_401(self):
#         # Arrange

#         # Act
#         client = APIClient()
#         response = client.post("/store/collections/", {"title": "a"})

#         # Assert
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_if_user_is_not_admin_return_403(self):
#         client = APIClient()
#         client.force_authenticate(user={})
#         response = client.post("/store/collections/", {"title": "a"})

#         assert response.status_code == status.HTTP_403_FORBIDDEN

#     def test_if_user_is_admin_and_invalid_request_return_400(self):
#         client = APIClient()
#         client.force_authenticate(user=User(is_staff=True))
#         response = client.post("/store/collections/", {"title": ""})

#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert response.data["title"] is not None

#     def test_if_user_is_admin_and_valid_request_return_201(self):
#         client = APIClient()
#         client.force_authenticate(user=User(is_staff=True))
#         response = client.post("/store/collections/", {"title": "a"})

#         assert response.status_code == status.HTTP_201_CREATED
#         assert response.data["id"] > 0
