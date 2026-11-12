from .models import Gen

def categorii_menu(request): # LAB 4
    return {
        'categorii_toate': Gen.objects.all().order_by('nume')
    }
    
def ip_client(request): # LAB 2
    return {
        'ip_client': request.META.get('REMOTE_ADDR')
    }
