import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rareapi.models import RareUser, Post, Category


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return RareUser.objects.create_user(
        username="testuser",
        password="testpass123",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        bio="A test user",
        is_active=True,
    )


@pytest.fixture
def auth_client(api_client, user):
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def category(db):
    return Category.objects.create(label="General")


def make_post(user, category, approved):
    return Post.objects.create(
        user=user,
        category=category,
        title="Test Post",
        publication_date="2026-01-01",
        image_url="",
        content="Some content.",
        approved=approved,
    )


@pytest.mark.django_db
class TestApprovedPostCount:
    def test_zero_posts(self, auth_client, user):
        """User with no posts at all should show 0."""
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.status_code == 200
        assert response.data["approved_post_count"] == 0

    def test_only_unapproved_posts(self, auth_client, user, category):
        """Unapproved posts must not be counted."""
        make_post(user, category, approved=False)
        make_post(user, category, approved=False)
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.status_code == 200
        assert response.data["approved_post_count"] == 0

    def test_only_approved_posts(self, auth_client, user, category):
        """All approved posts should be counted."""
        make_post(user, category, approved=True)
        make_post(user, category, approved=True)
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.status_code == 200
        assert response.data["approved_post_count"] == 2

    def test_mixed_posts_counts_only_approved(self, auth_client, user, category):
        """Only posts with approved=True count; unapproved are excluded."""
        make_post(user, category, approved=True)
        make_post(user, category, approved=False)
        make_post(user, category, approved=True)
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.status_code == 200
        assert response.data["approved_post_count"] == 2

    def test_other_users_posts_not_counted(self, auth_client, user, category, db):
        """Approved posts from other users must not appear in this user's count."""
        other = RareUser.objects.create_user(
            username="other", password="pass", email="other@example.com", is_active=True
        )
        make_post(other, category, approved=True)
        make_post(other, category, approved=True)
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.status_code == 200
        assert response.data["approved_post_count"] == 0