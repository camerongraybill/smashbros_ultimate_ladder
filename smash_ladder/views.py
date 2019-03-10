from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django.views.generic.base import ContextMixin

from smash_ladder.forms import EditProfileForm, GameReportForm
from smash_ladder.models import Profile, School, Character
from smash_ladder.services import RatingService


class NavBarDataMixin(ContextMixin):
    active_name = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs,
                                        players=Profile.objects.all(),
                                        schools=School.objects.all(),
                                        characters=Character.objects.all(),
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

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs, rating=RatingService.get_rating_for(request.user))


@method_decorator(staff_member_required, name='dispatch')
class Report(CreateView, NavBarDataMixin):
    form_class = GameReportForm
    active_name = "Report"
    template_name = "smash_ladder/report.html"
