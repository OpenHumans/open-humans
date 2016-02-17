from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView

from common.mixins import PrivateMixin

from studies.models import StudyGrant


class MemberStudyGrantDeleteView(PrivateMixin, TemplateView):
    """
    Let the user delete a study grant.
    """

    template_name = 'member/my-member-study-grants-delete.html'

    @staticmethod
    def get_study_grant(request, **kwargs):
        try:
            study_grant_pk = kwargs.get('study_grant')
            study_grant = StudyGrant.objects.get(pk=study_grant_pk,
                                                 member=request.user.member)
        except StudyGrant.DoesNotExist:
            return None

        return study_grant

    def get_context_data(self, **kwargs):
        context = super(MemberStudyGrantDeleteView, self).get_context_data(
            **kwargs)

        study_grant = self.get_study_grant(self.request, **kwargs)

        if study_grant:
            context.update({
                'study_title': study_grant.study.title,
            })

        return context

    def post(self, request, **kwargs):
        study_grant = self.get_study_grant(request, **kwargs)

        if not study_grant:
            return

        study_grant.delete()

        return HttpResponseRedirect(reverse('my-member-connections'))
