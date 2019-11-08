from django.utils.safestring import mark_safe

from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    MultipleChoiceFilter,
    NumberFilter,
)
from django_filters.fields import DateRangeField
from django_filters.filters import RangeFilter
from django_filters.widgets import CSVWidget, RangeWidget

from data_import.models import DataFile, DataType
from private_sharing.models import DataRequestProject
from private_sharing.utilities import get_source_labels_and_names_including_dynamic

from .models import Member


class PublicDataFileFilter(FilterSet):
    """
    Filters available for the public DataFile list endpoint.
    """

    datatype_id = NumberFilter(field_name="datatypes")
    source_project_id = NumberFilter(field_name="direct_sharing_project")
    username = CharFilter(field_name="user__username")

    class Meta:  # noqa: D101
        model = DataFile
        fields = ("datatype_id", "source_project_id", "username")


class PublicDataTypeFilter(FilterSet):
    """
    Filters available for the DataType list endpoint.
    """

    source_project_id = NumberFilter(field_name="source_projects__id")
    uploadable = BooleanFilter(field_name="uploadable")

    class Meta:  # noqa: D101
        model = DataType
        fields = ["source_project_id"]


class PublicMemberFilter(FilterSet):
    """
    Filters available for the Member list endpoint.
    """

    name = CharFilter(lookup_expr="icontains")
    username = CharFilter(field_name="user__username", lookup_expr="icontains")

    class Meta:  # noqa: D101
        model = Member
        fields = ["name", "username"]


class PublicProjectFilter(FilterSet):
    """
    Filters available for the Project list endpoint.
    """

    active = BooleanFilter()
    name = CharFilter(lookup_expr="icontains")

    class Meta:  # noqa: D101
        model = DataRequestProject
        fields = ["active", "id", "name"]


#####################################################################
# LEGACY FILTERS
#
# The following filters are used by deprecated API endpoints.
#####################################################################


class StartEndRangeWidget(RangeWidget):
    """
    A range widget that uses 'start' and 'end' instead of '0' and '1'.
    """

    attr_names = ("start", "end")

    def render(self, name, value, attrs=None, renderer=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized

        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)

        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get("id")

        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None

            if id_:
                final_attrs = dict(final_attrs, id="%s_%s" % (id_, self.attr_names[i]))

            output.append(
                widget.render(
                    name + "_%s" % self.attr_names[i],
                    widget_value,
                    attrs=final_attrs,
                    renderer=renderer,
                )
            )

        return mark_safe("-".join(output))

    def value_from_datadict(self, data, files, name):
        return [
            widget.value_from_datadict(data, files, name + "_%s" % self.attr_names[i])
            for i, widget in enumerate(self.widgets)
        ]


class StartEndDateRangeField(DateRangeField):
    """
    A DateRangeField that uses 'start' and 'end'.
    """

    widget = StartEndRangeWidget


class StartEndDateFromToRangeFilter(RangeFilter):
    """
    A RangeFilter that uses 'start' and 'end'.
    """

    field_class = StartEndDateRangeField


class LegacyPublicDataFileFilter(FilterSet):
    """
    A FilterSet that maps member_id and username to less verbose names.
    """

    created = StartEndDateFromToRangeFilter()
    member_id = CharFilter(field_name="user__member__member_id")
    username = CharFilter(field_name="user__username")
    source = MultipleChoiceFilter(
        choices=get_source_labels_and_names_including_dynamic, widget=CSVWidget()
    )
    # don't filter by source if no sources are specified; this improves speed
    source.always_filter = False

    class Meta:  # noqa: D101
        """
        Metaclass
        """

        model = DataFile
        fields = ("created", "source", "username", "member_id")
