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
        q.setWhere("codsincro = '{}' AND sincronizado = false".format(self.params["codsincro"]))
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

        return self.after_sync()

    def log(self, msg_type, msg):
        if self.driver.in_production:
            qsatype.debug("{} {}. {}.".format(msg_type, self.process_name, str(msg).replace("'", "\"")).encode("ascii"))
        else:
            qsatype.debug("{} {}. {}.".format(msg_type, self.process_name, str(msg).replace("'", "\"")))

        self.logs.append({
            "msg_type": msg_type,
            "msg": msg,
            "process_name": self.process_name,
            "customer_name": syncppal.iface.get_customer()
        })

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

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = false, fecha = '{}', hora = '{}' WHERE codsincro =  '{}'".format(self.start_date, self.start_time, self.params["codsincro"]))
        self.log("Éxito", "Usuario sincronizado correctamente (codsincro: {})".format(self.params["codsincro"]))

        return self.small_sleep

    def after_sync_item(self, idlinea):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = true WHERE id =  {}".format(idlinea))
