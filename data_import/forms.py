from django import forms

from .models import DataType


class DataTypeForm(forms.ModelForm):
    """
    A form for creating and editing DataTypes.
    """

    class Meta:  # noqa: D101
        model = DataType
        fields = ["name", "parent", "description"]

    def __init__(self, *args, **kwargs):
        self.editor = kwargs.pop("editor")
        return super().__init__(*args, **kwargs)

    def clean_name(self):
        """
        Verify that the name is case insensitive unique.
        """
        name = self.cleaned_data.get("name")
        try:
            dt = DataType.objects.get(name__iexact=name)
        except DataType.DoesNotExist:
            dt = self.instance
        if not dt == self.instance:
            raise forms.ValidationError(
                "Please provide a unique name for this datatype"
            )
        return name

    def clean(self, *args, **kwargs):
        if self.instance:
            if not self.instance.editable:
                raise forms.ValidationError(
                    "Not editable: in use by one or more approved projects."
                )
        self.instance.editor = self.editor
        return super().clean(*args, **kwargs)
