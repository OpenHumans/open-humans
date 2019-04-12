import datetime

import arrow

from rest_framework.filters import BaseFilterBackend


class AccessLogFilter(BaseFilterBackend):
    """
    Used for filtering data returned by the custom API for OHLOG_PROJECT_ID.
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
                # Special check if start_date and end_date is the same
                # If this is the case, assume that a 24 hour period is meant, and set end_time accordingly
                if start_date == end_date:
                    end_date = end_date + datetime.timedelta(
                        hours=23, minutes=59, seconds=59
                    )
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
