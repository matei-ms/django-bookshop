from django.contrib import admin
from django.utils.html import format_html
import csv
from django.http import HttpResponse

from .models import Autor
from .models import Gen
from .models import Carte
from .models import Tip
from .models import Editura
from .models import Coperta
from .models import Limba
from .models import Editie
from .models import CarteAutor
from .models import CarteGen
from .models import EditieLimba

class AutorAdmin(admin.ModelAdmin):
    search_fields = ('nume', 'autor_carti__carte__titlu')  
    search_help_text = "Caută după nume sau titlul uneia dintre cărți!"
    list_per_page = 5

class GenAdmin(admin.ModelAdmin):
    fields = ['nume', 'culoare', 'descriere']
    search_fields = ('nume', 'culoare')
    search_help_text = "Caută după nume sau culoare!"
    list_filter = ('culoare',)
    list_display = ('nume', 'culoare', 'nume_colorat')
    
    @admin.display(description='Numele colorat :)')
    def nume_colorat(self, obj):
        return format_html('<i style="color: {};">{}</i>', obj.culoare, obj.nume)
    
class CarteAdmin(admin.ModelAdmin):
    search_fields = ('titlu', 'carte_autori__autor__nume')
    search_help_text = "Caută după titlu sau autor!"
    ordering = ['titlu', '-an_publicatie']
    list_filter = ('an_publicatie', 'carte_autori__autor')
    
class TipAdmin(admin.ModelAdmin):
    search_fields = ('tipul_cartii', 'editii__isbn')
    search_help_text = "Caută după tipul cărții sau ISBN!"
    
class EdituraAdmin(admin.ModelAdmin):
    search_fields = ('nume', 'descriere')
    search_help_text = "Caută după nume sau descriere!"
    
class CopertaAdmin(admin.ModelAdmin):
    search_fields = ('alt_text', 'editii__isbn')
    search_help_text = "Caută după text alternativ sau ISBN!"
    
class LimbaAdmin(admin.ModelAdmin):
    search_fields = ('limba', 'cod_limba')
    search_help_text = "Caută după limbă sau codul ei!"

class EditieAdmin(admin.ModelAdmin):
    actions = ['export_csv_editii', 'marcheaza_disponibile']
    list_display = ('isbn', 'carte', 'pret', 'editura__nume', 'disponibilitate')
    search_fields = ('isbn', 'carte__titlu') 
    list_filter = ('disponibilitate', 'data_adaugarii', 'editura')
    readonly_fields = ('data_adaugarii',)
    fieldsets = (
    ('Informații generale', {
        'fields': ('isbn', 'carte', 'pret', 'editura')
    }),
    ('Câmpuri opționale', {
        'fields': ('tip', 'disponibilitate', 'data_adaugarii'),
        'classes': ('collapse',),
    }),
)
    
    @admin.action(description="Exportă edițiile selectate în format CSV")
    def export_csv_editii(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="editii.csv"'

        writer = csv.writer(response)
        writer.writerow(['ISBN', 'Preț', 'Disponibilitate'])

        for editie in queryset:
            writer.writerow([
                f'="{editie.isbn}"',
                editie.pret,
                editie.disponibilitate
            ])
        return response
    
    @admin.action(description="Marchează edițiile selectate drept disponibile")
    def marcheaza_disponibile(self, request, queryset):
        queryset.update(disponibilitate=True)


class CarteAutorAdmin(admin.ModelAdmin):
    search_fields = ('carte__titlu', 'autor__nume') 

class CarteGenAdmin(admin.ModelAdmin):
    search_fields = ('carte__titlu', 'gen__nume') 
    
class EditieLimbaAdmin(admin.ModelAdmin):
    search_fields = ('editie__isbn', 'limba__limba')  

admin.site.register(Autor, AutorAdmin)  
admin.site.register(Gen, GenAdmin)
admin.site.register(Carte, CarteAdmin)
admin.site.register(Tip, TipAdmin)
admin.site.register(Editura, EdituraAdmin)
admin.site.register(Coperta, CopertaAdmin)
admin.site.register(Limba, LimbaAdmin)
admin.site.register(Editie, EditieAdmin)
admin.site.register(CarteAutor, CarteAutorAdmin)
admin.site.register(CarteGen, CarteGenAdmin)
admin.site.register(EditieLimba, EditieLimbaAdmin)

admin.site.site_header = "Panou de Administrare Site"
admin.site.site_title = "Admin Site"
admin.site.index_title = "Bine ai venit în panoul de administrare! :D"
admin.site.site_url = '/bookapp/'