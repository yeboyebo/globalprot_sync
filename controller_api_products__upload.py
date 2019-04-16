import json

from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.sync.base.aqsync_upload import AQSyncUpload


class GpProductsUpload(AQSyncUpload):

    def __init__(self, driver, params=None):
        super().__init__("gpsyncproducts", driver, params)

        self.set_sync_params({
            "login_user": "global",
            "test_login_user": "global",
            "login_password": "123456789",
            "test_login_password": "123456789",
            "auth": "Basic Z2xvYmFscHJvdGVjY2lvbjoxMjM0NTY3ODk=",
            "test_auth": "Basic Z2xvYmFscHJvdGVjY2lvbjoxMjM0NTY3ODk=",
            "url": "http://dev9.yeclaweb.com/erpglobal/product{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/product{}",
            "login_url": "http://dev9.yeclaweb.com/erpglobal/user/login",
            "test_login_url": "http://dev9.yeclaweb.com/erpglobal/user/login",
            "logout_url": "http://dev9.yeclaweb.com/erpglobal/user/logout",
            "test_logout_url": "http://dev9.yeclaweb.com/erpglobal/user/logout"
        })

    def get_data(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("a.referencia, a.descripcion, a.pvp, a.product_id, s.disponible, sc.tiposincro")
        q.setFrom("sincro_catalogo sc INNER JOIN lineassincro_catalogo ls ON sc.codsincro = ls.codsincro INNER JOIN articulos a ON ls.idobjeto = a.referencia LEFT OUTER JOIN stocks s ON a.referencia = s.referencia")
        q.setWhere("sc.codsincro = '{}' AND sc.ptesincro ORDER BY a.referencia".format(self.params["codsincro"]))

        q.exec_()

        body = []
        if not q.size():
            return body

        while q.next():
            sku = q.value("a.referencia")
            title = q.value("a.descripcion")
            tiposincro = q.value("sc.tiposincro")
            product_id = q.value("a.product_id")
            amount = str(int(q.value("a.pvp") * 100))
            qty = str(self.dame_stock(q.value("s.disponible")))
            body.append({"type": "product", "product_id": product_id, "tiposincro": tiposincro, "sku": sku, "title": title, "commerce_price": {"amount": amount, "currency_code": "EUR"}, "commerce_stock": qty})

        return body

    def sync(self):
        data = self.get_data()

        if data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return self.large_sleep

        for item in data:
            product_id = item["product_id"]
            tiposincro = item["tiposincro"]
            sku = item["sku"]
            del item["tiposincro"]
            del item["product_id"]

            if product_id:
                if tiposincro == "Borrar productos":
                    response_data = self.send_request("delete", data=json.dumps(item), replace=["/{}".format(product_id)])
                else:
                    response_data = self.send_request("put", data=json.dumps(item), replace=["/{}".format(product_id)])
            else:
                response_data = self.send_request("post", data=json.dumps(item), replace=[""])

            if not response_data:
                response_data = {}

            response_data.update({
                "previous_product_id": product_id,
                "tiposincro": tiposincro,
                "sku": sku
            })
            self.after_sync_item(response_data)

        return self.after_sync()

    def dame_stock(self, disponible):
        if not disponible or isNaN(disponible) or disponible < 0:
            return 0.00

        return disponible

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = false, fecha = '{}', hora = '{}' WHERE codsincro =  '{}'".format(self.start_date, self.start_time, self.params["codsincro"]))
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = true WHERE codsincro =  '{}'".format(self.params["codsincro"]))
        self.log("Éxito", "Productos sincronizados correctamente (codsincro: {})".format(self.params["codsincro"]))

        return self.small_sleep

    def after_sync_item(self, response_data=None):
        if not response_data["previous_product_id"]:
            qsatype.FLSqlQuery().execSql("UPDATE articulos SET product_id = '{}' WHERE referencia = '{}'".format(response_data["product_id"], response_data["sku"]))
        elif response_data["tiposincro"] == "Borrar productos":
            qsatype.FLSqlQuery().execSql("UPDATE articulos SET product_id = NULL WHERE referencia = '{}'".format(response_data["sku"]))
