from django.forms import ModelForm, ModelChoiceField, DateTimeField, TextInput, Form, formset_factory, \
    ChoiceField
from django.utils.datetime_safe import datetime

from .models import Profile, Character


class EditProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)


class GameReportForm(Form):
    CHOICES = ((1, 'Player One'), (2, 'Player Two'))
    winner = ChoiceField(choices=CHOICES, initial=None)
    player_one_character = ModelChoiceField(queryset=Character.objects.all())
    player_two_character = ModelChoiceField(queryset=Character.objects.all())


class SetReportForm(Form):
    when = DateTimeField(initial=datetime.now,
                         widget=TextInput(
                             attrs={'type': 'datetime-local'}
                         ))
    player_one = ModelChoiceField(
        queryset=Profile.objects.all()
    )
    player_two = ModelChoiceField(
        queryset=Profile.objects.all()
    )


GameFormSet = formset_factory(GameReportForm, extra=3)
