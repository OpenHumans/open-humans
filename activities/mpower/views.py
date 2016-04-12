from django.core.urlresolvers import reverse_lazy

from data_import.views import DataRetrievalView

from ..views import BaseUploadView
from . import label
from .models import UserData


class UploadView(BaseUploadView, DataRetrievalView):
    """
    Allow the user to upload a 23andMe file.
    """

    fields = ['data_file']
    in_development = True
    model = UserData
    source = label
    success_url = reverse_lazy('my-member-research-data')
    template_name = 'mpower/upload.html'

    def form_valid(self, form):
        """
        Save updated model, then trigger retrieval task and redirect.
        """
        user_data = UserData.objects.get(user=self.request.user)

        user_data.data_file = form.cleaned_data.get('key_name')
        user_data.save()

        self.trigger_retrieval_task(self.request)

        return super(UploadView, self).form_valid(form)
