from rest_framework.generics import ListAPIView

from private_sharing.models import id_label_to_project

from .models import DataType
from .serializers import DataTypeSerializer


class DataTypesListAPIView(ListAPIView):
    """
    Lists the datatypes available and which projects use them.
    """

    serializer_class = DataTypeSerializer

    def get_queryset(self):
        """
        Get the queryset and filter on project if provided.
        """
        source_project_label = self.request.GET.get("source_project", None)
        if source_project_label:
            source_project = id_label_to_project(source_project_label)
            queryset = source_project.registered_datatypes.all()
        else:
            queryset = DataType.objects.all()
        return queryset
