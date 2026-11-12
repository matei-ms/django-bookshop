from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from datetime import datetime
from .accesari import Accesare
from collections import Counter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Editie, Gen
from .forms import FiltruProduse
import time
import json
import os
import re
from django.conf import settings
from .forms import ContactForm, EditieForm
from datetime import date

def index(request): # LAB 1
    return render(request, "bookapp/simplu.html", {
        "param": "valoare param something!!"
})

def info(request): # test: /info?data=timp&nume=harrowhark&joc="riichi mahjong"
    parametru = request.GET.get("data")

    if parametru == "timp":
        miau = request.acces.data("%H:%M:%S")
    else:
        miau = request.acces.data()
        
    parametri = request.GET.keys()
    lista_parametri = "<ul>"
    for p in parametri:
        lista_parametri += f"<li>{p}</li>"
    lista_parametri += "</ul>"

    return render(request, "bookapp/info.html", {
        "data": miau,
        "nr_parametri": len(parametri),
        "lista_parametri": lista_parametri
    })
    
def log(request): # de adaugat favicon # LAB 2 (50-171)
    ultimele = request.GET.get("ultimele")
    acc = request.GET.get("accesari")
    iduri = request.GET.getlist("iduri")
    dubluri = request.GET.get("dubluri", "false").lower() # implicit val false
    tabel = request.GET.get("tabel")
    
    logs = Accesare.logs()
    accesari = logs
    eroare = ""
    sectiune_nr = ""
    sectiune_detalii = ""
    
    if acc == "nr": # test: /log?accesari=nr
        sectiune_nr = f"<p> nr total de accesări???? {len(logs)}!!!</p>"
    elif acc == "detalii":  # test: /log?accesari=detalii
        sectiune_detalii = "<h2>detalii</h2><ul>"
        
        for acc in logs:
            sectiune_detalii += f"<li>{acc.data('%d.%m.%Y %H:%M:%S')}</li>"
        sectiune_detalii += "</ul>"
        
    if iduri: # test: /log?iduri=2,3&iduri=5&iduri=4,2,1 /log?iduri=2,3&iduri=5&iduri=4,2,1&dubluri=true
        iduri_str = ",".join(iduri) # conversie lista -> string
        iduri_list = [int(x) for x in iduri_str.split(",") if x.strip().isdigit()] # conversie string -> lista de int
        seen = set() # pt dubluri
        filtered = []
        
        for id_val in iduri_list:
            if dubluri == "true" or id_val not in seen:  # ce iduri am mai vazut
                match = next((log for log in logs if log.id == id_val), None) 
                
                if match:
                    filtered.append(match) 
                
                seen.add(id_val)
        accesari = filtered
    
    if ultimele is not None: # test: /log?ultimele=8
        if ultimele.isdigit():
            n = int(ultimele)
            
            if n > 0:
                accesari = logs[-n:]
                
                if n > len(logs):
                    eroare = f"exista doar {len(logs)} accesari fata de {n} accesari cerute."
            else:
                accesari = []
                eroare = "nr trebuie sa fie pozitiv... :("
        else:
            accesari = []
            eroare = f"'{ultimele}' nu e un numar valid... :("
    
    lista_html = "<ul>"
    
    for acc in accesari:
        lista_html += f"<li>ID: {acc.id} — {acc.data('%d.%m.%Y %H:%M:%S')} - {acc.pagina()} - IP: {acc.ip_client}</li>"

    lista_html += "</ul>"

    tabel_html = ""
    
    if tabel is not None: # maybe throw erori mai cu sens la prop
        if tabel == "tot":
            coloane = ["id", "data_accesare", "url_accesat", "ip_client"]
        else:
            coloane = [prop.strip() for prop in tabel.split(",")] # ia prop separat

        proprietati_valide = ["id", "data_accesare", "data", "url_accesat", "url", "ip_client", "ip"]
        coloane_valide = [col for col in coloane if col in proprietati_valide]
        
        tabel_html = "<h1>un tabel...</h1>"
        tabel_html += "<table border='1' style='border-collapse: collapse;'>"
        
        tabel_html += "<tr>"
        
        for col in coloane_valide:
            tabel_html += f"<th style='padding: 8px; background-color: #f0f0f0;'>{col}</th>"
            
        tabel_html += "</tr>"
            
        for acc in accesari:
            tabel_html += "<tr>"
            
            for col in coloane_valide:
                if col == "id":
                    value = acc.id
                elif col == "data_accesare" or col == "data":
                    value = acc.data('%d.%m.%Y %H:%M:%S')
                elif col == "url_accesat" or col == "url":
                    value = acc.url_accesat
                elif col == "ip_client" or col == "ip":
                    value = acc.ip_client
                tabel_html += f"<td style='padding: 8px;'>{value}</td>"
                
            tabel_html += "</tr>"
            
        tabel_html += "</table>"

    pagini = [acc.pagina() for acc in accesari]

    frecventa = Counter(pagini)

    if frecventa:
        putin = min(frecventa, key=frecventa.get)
        mult = max(frecventa, key=frecventa.get)
        statistici = f"""
            <p>△ pagina cea mai extraordinară: <strong>{mult}</strong> ({frecventa[mult]} accesări)</p>
            <p>▽ pagina cea mai putin accesată: <strong>{putin}</strong> ({frecventa[putin]} accesări)</p>
        """
    else:
        statistici = "<p>nu există accesări pentru statistici.</p>"

    return render(request, "bookapp/log.html", {
        "sectiune_nr": sectiune_nr,
        "sectiune_detalii": sectiune_detalii,
        "lista_html": lista_html,
        "tabel_html": tabel_html,
        "statistici": statistici,
        "eroare": eroare
})

def simplu(request):
    return render(request, "bookapp/simplu.html", {
        "param": "valoare param something!!"
    })
    
def despre(request):
    return render(request, "bookapp/despre.html", {
    })

def in_lucru(request):
    return render(request, "bookapp/in_lucru.html", {
    })
    
def produse(request):
    sort = request.GET.get("sort") 
    nrPagina = request.GET.get("pagina", 1)
    previous_items_per_page = request.session.get('items_per_page', 8)
    pagination_changed = False
    
    if request.method == "POST":
        form = FiltruProduse(request.POST)
    else:
        form = FiltruProduse(initial={
            'items_pe_pagina': 8,
        })
        form = FiltruProduse()
    
    editii = Editie.objects.select_related('carte', 'editura', 'coperta').all()
    
    if form.is_valid():
        data = form.cleaned_data
        if data.get('titlu'):
            editii = editii.filter(carte__titlu__icontains=data['titlu'])
        if data.get('autor'):
            editii = editii.filter(carte__carte_autori__autor__nume__icontains=data['autor'])
        if data.get('gen'):
            editii = editii.filter(carte__carte_genuri__gen=data['gen']).distinct()
        if data.get('pret_min'):
            editii = editii.filter(pret__gte=data['pret_min'])
        if data.get('pret_max'):
            editii = editii.filter(pret__lte=data['pret_max'])
        if data.get('editura'):
            editii = editii.filter(editura=data['editura'])
        if data.get('tip'):
            editii = editii.filter(tip=data['tip'])
        if data.get('isbn'):
            editii = editii.filter(isbn__icontains=data['isbn'])
        if data.get('data_adaugare_dupa'):
            editii = editii.filter(data_adaugarii__gte=data['data_adaugare_dupa']) 
        if data.get('disponibilitate') == '1':
            editii = editii.filter(disponibilitate=True)
        elif data.get('disponibilitate') == '0':
            editii = editii.filter(disponibilitate=False)
        
        items_per_page = data.get('items_pe_pagina') or 8
        
        if items_per_page != previous_items_per_page:
            pagination_changed = True
            request.session['items_per_page'] = items_per_page
    else:
        items_per_page = 8
        
    if sort == 'a': 
        editii = editii.order_by('pret')
    elif sort == 'd':  
        editii = editii.order_by('-pret')
    
    paginator = Paginator(editii, items_per_page)
    mesajEroare = None
    
    try:
        obPagina = paginator.page(nrPagina)
    except EmptyPage:
        obPagina = None
        mesajEroare = "Nu sunt produse la această pagină. :("
    except PageNotAnInteger:
        obPagina = None
        mesajEroare = "Parametrul trebuie să fie numeric. :("
    
    return render(request, 'bookapp/produse.html', {
        'pagina': obPagina,
        'eroare': mesajEroare,
        'form': form,
        'sort_actual': sort,
        'pagination_changed': pagination_changed
    })
    
def produs_detaliu(request, isbn):
    editie = get_object_or_404(Editie, isbn=isbn)
    
    return render(request, 'bookapp/produs_detaliu.html', {
        'editie': editie
    })
    
def categorie(request, nume_gen):
    gen = get_object_or_404(Gen, nume=nume_gen)
    
    nrPagina = request.GET.get("pagina")
    sort = request.GET.get("sort")
    previous_items_per_page = request.session.get('items_per_page', 8)

    pagination_changed = False 
    
    if request.method == "POST":
        form = FiltruProduse(request.POST)
        if form.is_valid():
            submitted_gen = form.cleaned_data.get('gen')
            if submitted_gen and submitted_gen != gen:
                form.add_error('gen', f'Categoria nu poate fi modificată! Trebuie să fie "{gen.nume}".')
    else:
        form = FiltruProduse(initial={
            'items_pe_pagina': 8,
        })
    
    editii = Editie.objects.filter(
        carte__carte_genuri__gen=gen
    ).select_related('carte', 'editura', 'coperta').distinct()

    pagination_changed = False
    
    if form.is_valid():
        data = form.cleaned_data
        if data.get('titlu'):
            editii = editii.filter(carte__titlu__icontains=data['titlu'])
        if data.get('autor'):
            editii = editii.filter(carte__carte_autori__autor__nume__icontains=data['autor'])
        if data.get('editura'):
            editii = editii.filter(editura=data['editura'])
        if data.get('tip'):
            editii = editii.filter(tip=data['tip'])
        if data.get('pret_min'):
            editii = editii.filter(pret__gte=data['pret_min'])
        if data.get('pret_max'):
            editii = editii.filter(pret__lte=data['pret_max'])
        if data.get('isbn'):
            editii = editii.filter(isbn__icontains=data['isbn'])
        if data.get('data_adaugare_dupa'):
            editii = editii.filter(data_adaugarii__gte=data['data_adaugare_dupa'])
        if data.get('disponibilitate') == '1':
            editii = editii.filter(disponibilitate=True)
        elif data.get('disponibilitate') == '0':
            editii = editii.filter(disponibilitate=False)
        
        items_per_page = data.get('items_pe_pagina') or 8
        
        if items_per_page != previous_items_per_page:
            pagination_changed = True
            request.session['items_per_page'] = items_per_page
    else:
        items_per_page = 8
    
    if sort == 'a':
        editii = editii.order_by('pret')
    elif sort == 'd':
        editii = editii.order_by('-pret')
    
    paginator = Paginator(editii, items_per_page)
    mesajEroare = None
    
    try:
        obPagina = paginator.page(nrPagina)
    except EmptyPage:
        obPagina = None
        mesajEroare = "Nu mai sunt produse în această categorie. :("
    #except PageNotAnInteger:
    #    obPagina = paginator.page(1)
    
    return render(request, 'bookapp/produse.html', { 
        'pagina': obPagina,
        'eroare': mesajEroare,
        'sort_actual': sort,
        'gen': gen, 
        'pagination_changed': pagination_changed,
        'form': form
    })
    
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            today = date.today()
            birth_date = data['data_nasterii']
            years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            months = today.month - birth_date.month
            if months < 0:
                months += 12
                years -= 1
            data['varsta'] = f"{years} ani și {months} luni"
            
            mesaj = data['mesaj']
            mesaj = mesaj.replace('\n', ' ').replace('\r', ' ')
            mesaj = re.sub(r'\s+', ' ', mesaj)

            mesaj = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), mesaj)
            data['mesaj'] = mesaj
            
            urgent = False
            min_required = {'review': 4, 'cerere': 4, 'intrebare': 2, 'programare': 2}
            if data['tip_mesaj'] in min_required and data['minim_zile_asteptare'] == min_required[data['tip_mesaj']]:
                urgent = True
                data['urgent'] = True
            
            data['ip_client'] = request.META.get('REMOTE_ADDR')
            data['data_ora'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            data.pop('confirmare_email', None)
            data.pop('data_nasterii', None) 
            
            mesaje_dir = os.path.join(settings.BASE_DIR, 'bookapp', 'Mesaje')
            os.makedirs(mesaje_dir, exist_ok=True)
            
            timestamp = int(time.time())
            filename = f"mesaj_{timestamp}{'_urgent' if urgent else ''}.json"
            filepath = os.path.join(mesaje_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4, default=str)
            
            return render(request, 'bookapp/contact_succes.html')
    else:
        form = ContactForm()
    
    return render(request, 'bookapp/contact.html', {'form': form})

def adauga_editie(request):
    if request.method == 'POST':
        form = EditieForm(request.POST)
        if form.is_valid():
            editie = form.save(commit=False)
            pret_achizitie = form.cleaned_data['pret_achizitie']
            procent_adaos = form.cleaned_data['procent_adaos']
            editie.pret = pret_achizitie * (1 + procent_adaos / 100)
            
            editie.save()
            
            return redirect('produs_detaliu', isbn=editie.isbn)
    else:
        form = EditieForm()

    return render(request, 'bookapp/adauga_editie.html', {'form': form})

def render_403(request, titlu='', mesaj=''):
    request.session['erori_403'] = request.session.get('erori_403', 0) + 1
    
    context = {
        'titlu': titlu,
        'mesaj_personalizat': mesaj,
        'nr_accesari_403': request.session['erori_403'],
        'n_max_403': settings.N_MAX_403,
    }
    
    return HttpResponseForbidden(render(request, 'bookapp/403.html', context))

def interzis(request):
    return render_403(request, mesaj='Eroare 403 :)')
