from django.contrib import admin

from .models import Centre, Formation


class FormationInline(admin.TabularInline):
    model = Formation
    extra = 0


@admin.register(Centre)
class CentreAdmin(admin.ModelAdmin):
    list_display = ("nom", "adresse")
    search_fields = ("nom", "adresse")
    inlines = [FormationInline]


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ("titre", "centre", "duree_heures", "prix")
    list_filter = ("centre",)
    search_fields = ("titre", "description")
