from django import forms
from .models import Editura, Tip, Gen, Editie
from datetime import date, datetime
import re
import json
import os
from django.conf import settings

def validate_adult(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise forms.ValidationError('Trebuie să fiți major (peste 18 ani).')
    
def validate_word_count(value):
    words = re.findall(r'\w+', value)
    if len(words) < 5 or len(words) > 100:
        raise forms.ValidationError('Mesajul trebuie să conțină între 5 și 100 de cuvinte.')

def validate_word_length(value):
    words = re.findall(r'\w+', value)
    for word in words:
        if len(word) > 15:
            raise forms.ValidationError('Niciun cuvânt din mesaj nu poate depăși 15 caractere.')

def validate_no_links(value):
    if 'http://' in value.lower() or 'https://' in value.lower():
        raise forms.ValidationError('Textul nu poate conține linkuri.')

def validate_cnp_digits(value):
    if value and not value.isdigit():
        raise forms.ValidationError('CNP-ul trebuie să conțină doar cifre.')

def validate_cnp_format(value):
    if not value:
        return
    if len(value) != 13:
        raise forms.ValidationError('CNP-ul trebuie să aibă exact 13 caractere.')
    if value[0] not in ['1', '2', '5', '6']:
        raise forms.ValidationError('CNP-ul trebuie să înceapă cu 1, 2, 5 sau 6.')
    
    year = int(value[1:3])
    month = int(value[3:5])
    day = int(value[5:7])
    
    if value[0] in ['1', '2']:
        year += 1900
    elif value[0] in ['5', '6']:
        year += 2000
    try:
        date(year, month, day)
    except ValueError:
        raise forms.ValidationError('Datele din CNP nu formează o dată validă.')

def validate_email_domain(value):
    if value.endswith('@guerillamail.com') or value.endswith('@yopmail.com'):
        raise forms.ValidationError('E-mailul nu poate fi de la un furnizor temporar.')

def validate_capitalized_text(value):
    if not value:
        return
    if not value[0].isupper():
        raise forms.ValidationError('Textul trebuie să înceapă cu literă mare.')
    if not re.match(r'^[A-ZĂÂÎȘȚ][a-zA-ZăâîșțĂÂÎȘȚ\s\-]*$', value):
        raise forms.ValidationError('Textul poate conține doar litere, spații și cratimă.')

def validate_capital_after_separator(value):
    if not value:
        return
    parts = re.split(r'[\s\-]', value)
    for part in parts:
        if part and not part[0].isupper():
            raise forms.ValidationError('După spațiu sau cratimă trebuie să fie literă mare.')

def validate_isbn_format(value):
    if not (value.isdigit() and len(value) == 13):
        raise forms.ValidationError('ISBN-ul trebuie să conțină exact 13 cifre.')

def validate_pozitiv(value):
    if value is not None and value <= 0:
        raise forms.ValidationError('Valoarea trebuie să fie un număr pozitiv.')

def validate_maxim_doua_zecimale(value):
    if value is not None and value.as_tuple().exponent < -2:
        raise forms.ValidationError('Valoarea nu poate avea mai mult de două zecimale.')

class ContactForm(forms.Form):
    TIPURI_MESAJ = [
        ('', 'neselectat'),
        ('reclamatie', 'Reclamație'),
        ('intrebare', 'Întrebare'),
        ('review', 'Review'),
        ('cerere', 'Cerere'),
        ('programare', 'Programare'),
    ]
    
    nume = forms.CharField(
        max_length=10,
        required=True,
        label='Nume',
        validators=[validate_capitalized_text, validate_capital_after_separator]
    )
    prenume = forms.CharField(
        max_length=10,
        required=False,
        label='Prenume',
        validators=[validate_capital_after_separator]
    )
    cnp = forms.CharField(
        max_length=13,
        min_length=13,
        required=False,
        label='CNP',
        validators=[validate_cnp_digits, validate_cnp_format]
    )
    data_nasterii = forms.DateField(
        required=True,
        label='Data nașterii',
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[validate_adult]
    )
    email = forms.EmailField(
        required=True,
        label='E-mail',
        validators=[validate_email_domain]
    )
    confirmare_email = forms.EmailField(
        required=True,
        label='Confirmare e-mail'
    )
    tip_mesaj = forms.ChoiceField(
        choices=TIPURI_MESAJ,
        required=True,
        label='Tip mesaj',
        initial=''
    )
    subiect = forms.CharField(
        max_length=100,
        required=True,
        label='Subiect',
        validators=[validate_no_links, validate_capitalized_text, validate_capital_after_separator]
    )
    minim_zile_asteptare = forms.IntegerField(
        required=True,
        min_value=0,
        max_value=30,
        label='Minim zile așteptare',
        help_text='Pentru review-uri/cereri minimul de zile de așteptare trebuie setat de la 4 încolo iar pentru întrebări/programări de la 2 încolo. Maximul e 30.'
    )
    mesaj = forms.CharField(
        required=True,
        label='Mesaj (vă rugăm să vă semnați la final)',
        widget=forms.Textarea,
        validators=[validate_word_count, validate_word_length, validate_no_links]
    )
    
    def clean_prenume(self):
        prenume = self.cleaned_data.get('prenume')
        if prenume:
            validate_capitalized_text(prenume)
        return prenume

    def clean_tip_mesaj(self):
        tip = self.cleaned_data.get('tip_mesaj')
        if tip == '':
            raise forms.ValidationError('Trebuie să selectați un tip de mesaj.')
        return tip

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirmare_email = cleaned_data.get('confirmare_email')
        nume = cleaned_data.get('nume')
        mesaj = cleaned_data.get('mesaj')
        tip_mesaj = cleaned_data.get('tip_mesaj')
        minim_zile = cleaned_data.get('minim_zile_asteptare')
        cnp = cleaned_data.get('cnp')
        data_nasterii = cleaned_data.get('data_nasterii')
        
        if email and confirmare_email and email != confirmare_email:
            self.add_error('confirmare_email', 'E-mailurile nu coincid.')

        if mesaj and nume:
            words = re.findall(r'\w+', mesaj)
            if not words or words[-1].lower() != nume.lower():
                self.add_error('mesaj', 'Mesajul trebuie să se termine cu numele dumneavoastră ca semnătură.')

        if tip_mesaj and minim_zile is not None:
            if tip_mesaj in ['review', 'cerere'] and minim_zile < 4:
                self.add_error('minim_zile_asteptare', 'Pentru review-uri/cereri minimul este 4 zile.')
            if tip_mesaj in ['intrebare', 'programare'] and minim_zile < 2:
                self.add_error('minim_zile_asteptare', 'Pentru întrebări/programări minimul este 2 zile.')

        if cnp and data_nasterii:
            year = int(cnp[1:3])
            month = int(cnp[3:5])
            day = int(cnp[5:7])
            if cnp[0] in ['1', '2']:
                year += 1900
            elif cnp[0] in ['5', '6']:
                year += 2000
            cnp_date = date(year, month, day)
            if cnp_date != data_nasterii:
                self.add_error('cnp', 'CNP-ul nu corespunde cu data nașterii.')

        return cleaned_data

class FiltruProduse(forms.Form):
    titlu = forms.CharField(required=False, label='Titlu carte')
    isbn = forms.CharField(required=False, max_length=13, label='ISBN')
    autor = forms.CharField(required=False, label='Autor')
    gen = forms.ModelChoiceField(
        queryset=Gen.objects.all(),
        required=False,
        label='Gen',
        empty_label='Toate genurile'
    )
    pret_min = forms.DecimalField(required=False, label='Preț minim', min_value=0)
    pret_max = forms.DecimalField(required=False, label='Preț maxim', min_value=0)
    editura = forms.ModelChoiceField(queryset=Editura.objects.all(), required=False, label='Editura')
    tip = forms.ModelChoiceField(queryset=Tip.objects.all(), required=False, label='Tip')
    disponibilitate = forms.ChoiceField(
        choices=[('', 'Toate'), ('1', 'În stoc'), ('0', 'Indisponibil')],
        required=False,
        label='Disponibilitate'
    )
    data_adaugare_dupa = forms.DateField(
        required=False,
        label='Adăugat după data',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    items_pe_pagina = forms.IntegerField(required=False, label='Produse pe pagină', initial=8)
    
    def clean_autor(self):
        autor = self.cleaned_data.get('autor')
        if autor and not autor.replace(' ', '').isalnum():
            raise forms.ValidationError('Autorul poate conține doar litere, cifre și spații!')
        return autor

    def clean_items_pe_pagina(self):
        items = self.cleaned_data.get('items_pe_pagina')
        if items and (items < 1 or items > 50):
            raise forms.ValidationError('Numărul de produse pe pagină trebuie să fie între 1 și 50!')
        return items
    
    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn and not isbn.isdigit():
            raise forms.ValidationError('ISBN-ul poate conține doar cifre.')
        return isbn

    def clean(self):
        cleaned_data = super().clean()
        pret_min = cleaned_data.get('pret_min')
        pret_max = cleaned_data.get('pret_max')
        if pret_min and pret_max and pret_min > pret_max:
            self.add_error('pret_max', 'Prețul maxim trebuie să fie mai mare sau egal cu prețul minim!')
        return cleaned_data
    
class EditieForm(forms.ModelForm):
    pret_achizitie = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label='Preț de achiziție (RON)',
        help_text='Prețul la care ediția a fost achiziționată de la furnizor.',
        validators=[validate_pozitiv, validate_maxim_doua_zecimale],
    )
    procent_adaos = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        label='Procent adaos comercial (%)',
        help_text='Cât la sută se adaugă peste prețul de achiziție pentru a obține prețul final de vânzare.',
        validators=[validate_pozitiv],
    )

    class Meta:
        model = Editie
        fields = ['isbn', 'carte', 'editura', 'tip', 'disponibilitate']
        labels = {
            'isbn': 'Cod ISBN (13 cifre)',
            'disponibilitate': 'Disponibil pentru vânzare',
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        validate_isbn_format(isbn)
        return isbn

    def clean(self):
        cleaned_data = super().clean()
        disponibilitate = cleaned_data.get('disponibilitate')
        pret_achizitie = cleaned_data.get('pret_achizitie')
        if disponibilitate and pret_achizitie is None:
            self.add_error('pret_achizitie', 'Pentru o ediție disponibilă la vânzare, prețul de achiziție este obligatoriu.')
        return cleaned_data