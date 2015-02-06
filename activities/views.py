import json

from django.http import HttpResponse
from django.views.generic import View


class BaseJSONDataView(View):
    """Base view for returning JSON data.

    Additional definitions needed:
      - get_data(request): returns data to be returned by the view
    """

    def get(self, request):
        data = self.get_data(request)
        return HttpResponse(json.dumps(data),
                            content_type='application/json')
