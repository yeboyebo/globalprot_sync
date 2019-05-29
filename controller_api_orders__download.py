import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_upload #
class interna_download():
    pass


# @class_declaration globalprot_sync_upload #
class globalprot_sync_download(interna_download):

    @staticmethod
    def start(pk, data):
        result = None
        status = None

        response = task_manager.task_executer("orders_download", data)
        result = response["data"]
        status = response["status"]
        # éxito
        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration download #
class download(globalprot_sync_download):
    pass
