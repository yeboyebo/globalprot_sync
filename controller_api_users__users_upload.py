import json

from YBLEGACY import qsatype

from controllers.api.sync.base.controllers.aqsync_upload import AQSyncUpload
from models.flsyncppal import flsyncppal_def as syncppal


class GpUsersUpload(AQSyncUpload):

    def __init__(self, driver, params=None):
        super().__init__("gpsyncusers", driver, params)

        self.set_sync_params({
            "login_user": "global",
            "test_login_user": "global",
            "login_password": "123456789",
            "test_login_password": "123456789",
            "auth": "Basic Z2xvYmFscHJvdGVjY2lvbjoxMjM0NTY3ODk=",
            "test_auth": "Basic Z2xvYmFscHJvdGVjY2lvbjoxMjM0NTY3ODk=",
            "login_url": "http://dev9.yeclaweb.com/erpglobal/user/login",
            "test_login_url": "http://dev9.yeclaweb.com/erpglobal/user/login",
            "logout_url": "http://dev9.yeclaweb.com/erpglobal/user/logout",
            "test_logout_url": "http://dev9.yeclaweb.com/erpglobal/user/logout"
        })

    def get_data(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("id, idobjeto, descripcion, idobjeto_web, tiposincro")
        q.setFrom("lineassincro_catalogo")
        where = "(tiposincro = 'Enviar Usuario' OR tiposincro = 'Borrar Usuario')"
        if where != "":
            where += " AND "
        if "codsincro" in self.params and self.params["codsincro"]:
            where += "codsincro = '{}' AND sincronizado = false".format(self.params["codsincro"])
        else:
            where += "sincronizado = false ORDER BY id LIMIT 10"
        q.setWhere(where)
        q.exec_()
        body = []
        if not q.size():
            return body

        while q.next():
            idlinea = str(q.value("id"))
            email = q.value("idobjeto")
            nombre = q.value("descripcion")
            tiposincro = q.value("tiposincro")
            uid = q.value("idobjeto_web")
            # body.append({"idlinea": idlinea, "mail": email, "uid": uid, "tiposincro": tiposincro, "status": "1", "roles": ["4"], "pass": "123456789", "name": nombre})
            body.append({"idlinea": idlinea, "mail": email, "uid": uid, "tiposincro": tiposincro, "status": "1", "roles": ["4"], "name": nombre})
        return body

    def sync(self):
        data = self.get_data()

        if data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return self.large_sleep

        for item in data:
            user_id = item["uid"]
            tiposincro = item["tiposincro"]
            if user_id and user_id is not None and user_id != "":
                if tiposincro == "Borrar Usuario":
                    self.elimina_usuario(item)
                else:
                    self.modifica_usuario(item)
            else:
                    self.crea_usuario(item)

        return self.small_sleep

    def crea_usuario(self, item):
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/user{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/user{}"
        })
        # Alta
        # {"mail":"hola@yeclaweb.com", "status":"1", "roles":["4"], "pass": "123456789"}
        data = {
            "mail": item["mail"],
            "status": "1",
            "roles": ["4"],
            "pass": "123456789"
        }

        response_data = self.send_request("post", data=json.dumps(data), replace=[""])
        qsatype.FLSqlQuery().execSql("UPDATE gp_usutiendaonline SET uid = {} WHERE email = '{}'".format(response_data["uid"], item["mail"]))

        self.after_sync_item(item["idlinea"])

        return True

    def modifica_usuario(self, item):
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/user{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/user{}"
        })
        # Modificación
        # {"mail":"hola22@yeclaweb.com","pass":"123456789", "name": "nuevonombre"}
        data = {
            "mail": item["mail"],
            # "pass": "123456789",
            "name": item["name"]
        }

        self.send_request("put", data=json.dumps(data), replace=["/{}".format(item["uid"])])
        self.after_sync_item(item["idlinea"])

        return True

    def elimina_usuario(self, item):
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/user{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/user{}"
        })

        user_id = item["uid"]

        self.send_request("delete", data={}, replace=["/{}".format(user_id)])

        qsatype.FLSqlQuery().execSql("UPDATE gp_usutiendaonline SET uid = NULL WHERE email = '{}'".format(item["mail"]))

        self.after_sync_item(item["idlinea"])

        return True

    def after_sync(self, codsincro=None):
        qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = false, fecha = '{}', hora = '{}' WHERE codsincro =  '{}'".format(self.start_date, self.start_time, codsincro))
        self.log("Éxito", "Usuario sincronizado correctamente.")

        return True

    def after_sync_item(self, idlinea):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = true WHERE id =  {}".format(idlinea))
        codsincro = qsatype.FLUtil.quickSqlSelect("lineassincro_catalogo", "codsincro", "id = '{}'".format(idlinea))
        idlinea = qsatype.FLUtil.quickSqlSelect("lineassincro_catalogo", "id", "sincronizado = false AND  codsincro = '{}'".format(codsincro))
        if idlinea is False or idlinea is None:
            self.after_sync(codsincro)
        return True
