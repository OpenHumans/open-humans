from ..views import UserDataDetailView

from .models import UserData
from .serializers import UserDataSerializer


class UserDataDetail(UserDataDetailView):
    """
    Detail view for Wildlife of Our Homes user data.
    """

    def get_queryset(self):
        return self.get_user_data_queryset()

    user_data_model = UserData
    serializer_class = UserDataSerializer
