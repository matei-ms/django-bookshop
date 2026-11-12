from django.db import models
from django.utils.timezone import now
from django.contrib.postgres.fields import ArrayField

''' ignoram acest model
class AccessareLog(models.Model):
    path = models.CharField(max_length = 255)
    timestamp = models.DateTimeField(default = now)

    def __str__(self):
        return f"{self.timestamp} - {self.path}"
'''

class Autor(models.Model):
    class Meta:
        verbose_name_plural = "Autori"
        
    nume = models.CharField(max_length = 255)
    pseudonime = ArrayField(models.CharField(max_length = 255), default = list, blank = True, help_text = "Alte nume folosite de autor (dacă există).")
    biografie = models.TextField(default = None, blank = True, null = True)
    poza = models.ImageField(default = None, blank = True, null = True)
    
    def __str__(self):
        return f"{self.nume} - {self.biografie}"
    
class Gen(models.Model):
    class Meta:
        verbose_name_plural = "Genuri"
        constraints = [
            models.CheckConstraint(
                condition = models.Q(culoare__regex = r'^[a-z]+$'), name = 'gen_culoare_format_valid',
                violation_error_message = "Culoarea trebuie să fie un nume CSS valid, scris cu litere mici (de exemplu: tomato, dimgray)!"),
        ]
        indexes = [
            models.Index(fields = ['nume'], name = 'gen_nume_idx'),
        ]
        
    nume = models.SlugField(
        max_length = 255,
        help_text = "Identificator unic al genului, folosit în URL (litere, cifre, liniuțe, underscore, fără spații).",
        error_messages = {'max_length': "Numele genului nu poate avea mai mult de 255 de caractere."}
    )
    descriere = models.TextField()
    culoare = models.TextField(help_text = "Nume culoare CSS pentru stilizare.")
    
    def __str__(self):
        return f"{self.nume} - {self.descriere}"
    
class Carte(models.Model):
    class Meta:
        verbose_name_plural = "Carti"
        ordering = ['titlu']
        constraints = [
            models.CheckConstraint(
                condition = models.Q(an_publicatie__gt = 0), name = 'carte_an_publicatie_pozitiv',
                violation_error_message = "Anul publicației trebuie să fie un număr pozitiv!"),
            models.CheckConstraint(
                condition = models.Q(nr_pagini__gte = 1), name = 'carte_nr_pagini_minim',
                violation_error_message = "O carte trebuie să aibă cel puțin o pagină!"),
        ]
        indexes = [
            models.Index(fields = ['titlu'], name = 'carte_titlu_idx'),
        ]
        
    titlu = models.CharField(max_length = 255)
    descriere = models.TextField()
    an_publicatie = models.IntegerField(
        error_messages = {'invalid': "Anul publicației trebuie să fie un număr întreg."}
    )
    nr_pagini = models.PositiveIntegerField(
        error_messages = {'invalid': "Numărul de pagini trebuie să fie un număr întreg pozitiv."}
    )
    
    def __str__(self):
        return f"{self.titlu} - {self.an_publicatie}"
    
class Tip(models.Model):
    class Meta:
        verbose_name_plural = "Tipuri"
        
    TIPURI_OPTIUNI = (
        ('HARD', 'Hardcover'),
        ('PAPER', 'Paperback'),
    )
    
    tipul_cartii = models.CharField(
        max_length = 50, choices = TIPURI_OPTIUNI,
        error_messages = {'invalid_choice': "Tipul cărții trebuie să fie paperback sau hardcover."}
    )
    
    def __str__(self):
        return f"{self.tipul_cartii}" 

class Editura(models.Model):
    class Meta:
        verbose_name_plural = "Edituri"
        
    nume = models.CharField(max_length = 255)
    descriere = models.TextField(default = None, blank = True, null = True)
    logo = models.ImageField(default = None, blank = True, null = True)
    
    def __str__(self):
        return f"{self.nume} - {self.descriere}"

class Coperta(models.Model):
    class Meta:
        verbose_name_plural = "Coperti"
        
    editie = models.OneToOneField('Editie', on_delete = models.CASCADE, related_name = 'coperta')
    imagine = models.ImageField()
    alt_text = models.TextField(default = None, blank = True, null = True, help_text = "Descrierea imaginii. Pentru utilizatorii cu screen reader.")
    
    def __str__(self):
        return f"{self.alt_text}"

class Limba(models.Model):
    class Meta:
        verbose_name_plural = "Limbi"
        constraints = [
            models.CheckConstraint(
                condition = models.Q(cod_limba__regex = r'^[a-z]{2,3}$'), name = 'limba_cod_format_valid',
                violation_error_message = "Codul limbii trebuie să aibă 2 sau 3 litere mici (ISO 639)!"),
        ]
    
    limba = models.CharField(max_length = 100, default = "engleză")
    cod_limba = models.CharField(max_length = 5, default = "en", help_text = "Codul limbii ISO 639.")
    steag = models.ImageField(default = None, blank = True, null = True, help_text = "Imaginea steagului pentru limba respectivă.")
    
    def __str__(self):
        return f"{self.limba} ({self.cod_limba})"

class Editie(models.Model):
    class Meta:
        verbose_name_plural = "Editii"
        ordering = ['-data_adaugarii']
        constraints = [
            models.CheckConstraint(
                condition = models.Q(pret__gt = 0), name = 'editie_pret_pozitiv',
                violation_error_message = "Prețul trebuie să fie strict pozitiv!"),
        ]
        indexes = [
            models.Index(fields = ['pret'], name = 'editie_pret_idx'),
            models.Index(fields = ['disponibilitate'], name = 'editie_disponibilitate_idx'),
        ]
        
    isbn = models.CharField(
        max_length = 13, unique = True,
        error_messages = {
        'unique': "Există deja o ediție cu acest ISBN.",
        'max_length': "ISBN-ul trebuie să aibă exact 13 caractere.",
        }
    )
    pret = models.DecimalField(max_digits=8, decimal_places=2)
    disponibilitate = models.BooleanField(default = False)
    data_adaugarii = models.DateTimeField(auto_now_add = True)
    
    carte = models.ForeignKey(Carte, on_delete = models.CASCADE, related_name = 'editii')
    tip = models.ForeignKey(Tip, on_delete = models.SET_NULL, null = True, blank = True,related_name = 'editii')
    editura = models.ForeignKey(Editura, on_delete = models.CASCADE, related_name = 'editii')
    
    def __str__(self):
        return f"{self.isbn} - disponibilitate: {'da' if self.disponibilitate else 'nu'}"
    
class CarteAutor(models.Model):
    class Meta:
        verbose_name_plural = "Carti-Autori"
        
    carte = models.ForeignKey(Carte, on_delete = models.CASCADE, related_name = 'carte_autori')
    autor = models.ForeignKey(Autor, on_delete = models.CASCADE, related_name = 'autor_carti')
    data_adaugarii = models.DateTimeField(auto_now_add = True) 
    
    def __str__(self):
        return f"{self.carte.titlu} - {self.autor.nume}"

class CarteGen(models.Model):
    class Meta:
        verbose_name_plural = "Carti-Genuri"
        
    carte = models.ForeignKey(Carte, on_delete = models.CASCADE, related_name = 'carte_genuri')
    gen = models.ForeignKey(Gen, on_delete = models.CASCADE, related_name = 'gen_carti') 
    
    def __str__(self):
        return f"{self.carte.titlu} - {self.gen.nume}"

class EditieLimba(models.Model):
    class Meta:
        verbose_name_plural = "Editii-Limbi"
        
    editie = models.ForeignKey(Editie, on_delete = models.CASCADE, related_name = 'editie_limbi')
    limba = models.ForeignKey(Limba, on_delete = models.CASCADE, related_name = 'limba_editii')
    
    def __str__(self):
        return f"{self.editie.isbn} - {self.limba.limba}"
