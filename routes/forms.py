from django import forms
from .models import Route

class LastDirectionalNodeForm(forms.Form):
    route = forms.ModelChoiceField(queryset=Route.objects.all())
    position = forms.IntegerField(
        min_value=0,
        help_text="Reference node position (starting point)"
    )
    direction = forms.ChoiceField(
        choices=(("left", "Left"), ("right", "Right"))
    )
