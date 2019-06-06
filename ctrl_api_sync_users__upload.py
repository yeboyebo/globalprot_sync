import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_upload #
class interna_upload():
    pass


# @class_declaration globalprot_sync_upload #
class globalprot_sync_upload(interna_upload):

    @staticmethod
    def start(pk, data):
        result = None
        status = None

        response = task_manager.task_executer("users_upload", data)
        result = response["data"]
        status = response["status"]
        # éxito
        return HttpResponse(json.dumps(result), status=status, content_type="application/json")


# @class_declaration upload #
class upload(globalprot_sync_upload):
    pass
