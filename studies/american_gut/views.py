from ..viewsets import NestedStudyViewset, StudyViewset

from .models import Barcode, UserData
from .serializers import BarcodeSerializer, UserDataSerializer


class BarcodeViewSet(NestedStudyViewset):
    model = Barcode
    parent_attribute = 'user_data'
    serializer_class = BarcodeSerializer


class UserDataViewSet(StudyViewset):
    queryset = UserData.objects.all()
    serializer_class = UserDataSerializer
