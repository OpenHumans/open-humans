from rest_framework import generics

from .models import Barcode, UserData
from .serializers import BarcodeSerializer, UserDataSerializer


class BarcodeList(generics.ListCreateAPIView):
    queryset = Barcode.objects.all()
    serializer_class = BarcodeSerializer
