import json

from django.http import HttpResponse


# @class_declaration interna_info #
class interna_info():
    pass


# @class_declaration globalprot_sync_info #
class globalprot_sync_info(interna_info):

    @staticmethod
    def start(pk, data):
        result = {
            "pvp": 10,
            "descripcion": "Articulo no se cuantos"
        }

        return HttpResponse(json.dumps(result), status=200, content_type="application/json")


# @class_declaration info #
class info(globalprot_sync_info):
    pass
