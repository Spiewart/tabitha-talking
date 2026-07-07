import pytest

from tabitha_talking.users.models import User


@pytest.mark.django_db
def test_user_creation():
    """Test custom user model can be created."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.first_name is None
    assert user.last_name is None
