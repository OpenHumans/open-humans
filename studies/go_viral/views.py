from ..viewsets import NestedStudyViewset, StudyViewset

from .models import GoViralId, UserData
from .serializers import GoViralIdSerializer, UserDataSerializer


class GoViralIdViewSet(NestedStudyViewset):
    model = GoViralId
    parent_attribute = 'user_data'
    serializer_class = GoViralIdSerializer


class UserDataViewSet(StudyViewset):
    queryset = UserData.objects.all()
    serializer_class = UserDataSerializer
