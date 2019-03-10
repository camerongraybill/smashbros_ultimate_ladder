from django.forms import ModelForm

from .models import Profile, Game


class EditProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('school', 'profile_picture')


class GameReportForm(ModelForm):
    class Meta:
        model = Game
        fields = ('winner', 'loser', 'winner_char', 'loser_char')
