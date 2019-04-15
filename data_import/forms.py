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

    def clean_parent(self):
        """
        Verify that the parent is not the object itself nor a descendent.
        """
        parent = self.cleaned_data.get("parent")
        if not parent:
            return parent
        if self.instance.id == parent.id:
            raise forms.ValidationError(
                "A DataType cannot be assigned to be its own parent."
            )
        elif self.instance in parent.all_parents:
            raise forms.ValidationError(
                "{0} is not an allowed parent, as it is a descendent of {1}.".format(
                    parent.name, self.instance.name
                )
            )
        return parent

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
