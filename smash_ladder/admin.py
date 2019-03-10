from django.contrib import admin
# Register your models here.
from .models import Profile, School, Character, Game, Set

admin.site.register(Profile)

admin.site.register(School)
admin.site.register(Character)
admin.site.register(Game)
admin.site.register(Set)
