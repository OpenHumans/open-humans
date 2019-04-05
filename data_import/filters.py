import arrow
from rest_framework.filters import BaseFilterBackend


class AccessLogFilter(BaseFilterBackend):
    """
    For filtering access logs by datafile_id or by date.
    """

    def filter_queryset(self, request, queryset, view):

        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        if start_date:
            try:
                start_date = arrow.get(start_date).datetime
            except (TypeError, ValueError):
                start_date = None
        if end_date:
            try:
                end_date = arrow.get(end_date).datetime
            except (TypeError, ValueError):
                end_date = None
        if queryset.model.__name__ == "AWSDataFileAccessLog":
            # AWS uses 'time' for the timestamp rather than 'date'
            if start_date:
                queryset = queryset.filter(time__gte=start_date)
            if end_date:
                queryset = queryset.filter(time__lte=end_date)
        else:
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)

        datafile_id = request.query_params.get("datafile_id", None)
        if datafile_id:
            try:
                datafile_id = int(datafile_id)
                queryset = queryset.filter(serialized_data_file__id=datafile_id)
            except ValueError:
                pass

        return queryset
