from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django.views.generic.base import ContextMixin

from smash_ladder.forms import EditProfileForm, SetReportForm, GameFormSet
from smash_ladder.models import Profile, School, Character, Set, Game
from smash_ladder.services import RatingService


def get_default_context_data():
    return {
        'players': Profile.objects.all(),
        'schools': School.objects.all(),
        'characters': Character.objects.all()
    }


class NavBarDataMixin(ContextMixin):
    active_name = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, **get_default_context_data(),
                                        active=self.active_name)


class PlayerDetail(DetailView, NavBarDataMixin):
    model = Profile
    context_object_name = 'player'
    template_name = "smash_ladder/player_detail.html"
    active_name = "Players"


class SchoolDetail(DetailView, NavBarDataMixin):
    model = School
    context_object_name = 'school'
    template_name = "smash_ladder/school_detail.html"
    active_name = "Schools"


class CharacterDetail(DetailView, NavBarDataMixin):
    model = Character
    context_object_name = 'character'
    template_name = "smash_ladder/character_detail.html"
    active_name = "Characters"


class LeaderBoard(TemplateView, NavBarDataMixin):
    active_name = "Leader Board"
    template_name = "smash_ladder/leader_board.html"

    def get_context_data(self, **kwargs):
        players = Profile.objects.all()
        players = sorted(players, key=lambda x: x.rating, reverse=True)
        return super().get_context_data(**kwargs, leaderboard_players=players)


class Stats(TemplateView, NavBarDataMixin):
    active_name = "Stats"
    template_name = "smash_ladder/stats.html"


Index = LeaderBoard


class SignUp(CreateView, NavBarDataMixin):
    active_name = "Sign Up"
    form_class = UserCreationForm
    success_url = reverse_lazy('profile')
    template_name = 'registration/signup.html'


class EditProfile(LoginRequiredMixin, UpdateView, NavBarDataMixin):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    active_name = "Profile"
    form_class = EditProfileForm
    success_url = reverse_lazy('profile')
    template_name = 'smash_ladder/profile/edit.html'

    def get_object(self, queryset=None):
        prof, _ = Profile.objects.get_or_create(user=self.request.user)
        return prof


class ViewProfile(TemplateView, NavBarDataMixin):
    active_name = "Profile"
    template_name = 'smash_ladder/profile/view.html'


@staff_member_required
def report(request):
    if request.method == 'GET':
        setform = SetReportForm()
        formset = GameFormSet()
        return render(request, 'smash_ladder/report.html',
                      {'setform': setform, 'formset': formset, 'active': 'Report', **get_default_context_data()})

    else:
        setform = SetReportForm(request.POST)
        formset = GameFormSet(request.POST)
        if setform.is_valid() and formset.is_valid():
            s = Set(happened_at=setform.cleaned_data['when'])
            s.save()
            p1, p2 = setform.cleaned_data['player_one'], setform.cleaned_data['player_two']
            for game_form in formset:
                if game_form.cleaned_data['winner'] == 'Player One':
                    g = Game(set=s,
                             winner=p1,
                             loser=p2,
                             winner_char=game_form.cleaned_data['player_one_character'],
                             loser_char=game_form.cleaned_data['player_two_character']
                             )
                else:
                    g = Game(set=s,
                             winner=p2,
                             loser=p1,
                             winner_char=game_form.cleaned_data['player_two_character'],
                             loser_char=game_form.cleaned_data['player_one_character']
                             )
                g.save()
            RatingService.add_set(s)
            return redirect('report')
