from django.views.generic import TemplateView


class ConsentView(TemplateView):
    template_name = "public_data/consent.html"

    def post(self, request, *args, **kwargs):
        print "In post"
        if 'section' in request.POST:
            kwargs['section'] = int(request.POST['section'])
        return self.get(self, request, *args, **kwargs)

    def dispatch(self, *args, **kwargs):
        print "in dispatch"
        return super(ConsentView, self).dispatch(*args, **kwargs)
