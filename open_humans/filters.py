from django.utils.safestring import mark_safe

from django_filters import CharFilter, FilterSet, MultipleChoiceFilter
from django_filters.fields import DateRangeField
from django_filters.filters import RangeFilter
from django_filters.widgets import CSVWidget, RangeWidget

from data_import.models import DataFile
from private_sharing.utilities import (
     get_source_labels_and_names_including_dynamic)


class StartEndRangeWidget(RangeWidget):
    """
    A range widget that uses 'start' and 'end' instead of '0' and '1'.
    """

    attr_names = ('start', 'end')

    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized

        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)

        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id')

        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None

            if id_:
                final_attrs = dict(final_attrs,
                                   id='%s_%s' % (id_, self.attr_names[i]))

            output.append(widget.render(name + '_%s' % self.attr_names[i],
                                        widget_value, final_attrs))

        return mark_safe('-'.join(output))

    def value_from_datadict(self, data, files, name):
        return [widget.value_from_datadict(data, files,
                                           name + '_%s' % self.attr_names[i])
                for i, widget in enumerate(self.widgets)]


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
