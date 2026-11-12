from .accesari import Accesare

class MiddlewareNou:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url = request.build_absolute_uri()
        ip = request.META.get('REMOTE_ADDR', '?')
        
        acc = Accesare(url, ip, request.GET.dict())
        request.acces = acc
        print(acc)
        
        response = self.get_response(request)      

        response['header_nou'] = 'valoare'
        
        return response