from datetime import datetime # LAB 1
import locale

class Accesare:
    _autoid = 0
    _lista_accesari = [] 
    
    def __init__(self, url = None, ip = None, parametri = None):
        Accesare._autoid += 1 
        
        self.id = Accesare._autoid 
        self.data_accesare = datetime.now()
        self.url_accesat = url
        self.ip_client = ip
        self.parametri = parametri or {}
        
        Accesare._lista_accesari.append(self) 
        
    def lista_parametri(self):
        return [(nume, valoare) for nume, valoare in self.parametri.items()]
        
    def url(self):
        return self.url_accesat
    
    def data(self, fstring="%A, %#d %B %Y"):
        locale.setlocale(locale.LC_TIME, "ro_RO.UTF-8")
        return self.data_accesare.strftime(fstring)

    def pagina(self):
        url: str = self.url_accesat
        if url.startswith("http://") or url.startswith("https://"):
            url = url.split("//", maxsplit = 1)[1]
        return "/" + url.split("/", maxsplit = 1)[1].split("?", maxsplit = 1)[0]
    
    def __str__(self):
        campuri = [
            ("id", self.id),
            ("ip_client", self.ip_client),
            ("url", self.url()),
            ("pagina", self.pagina()),
            ("data", self.data()),
            ("lista_parametri", self.lista_parametri()),
        ]
        return "\n".join(f"{nume}: {valoare}" for nume, valoare in campuri)
        
    @classmethod
    def logs(cls):
        return cls._lista_accesari