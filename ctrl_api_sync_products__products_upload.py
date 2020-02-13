import json

from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.controllers.upload_sync import UploadSync


class GpProductsUpload(UploadSync):

    def __init__(self, driver, params=None):
        super().__init__("gpsyncproducts", driver, params)

        login_params = self.get_param_sincro('login')
        logout_params = self.get_param_sincro('logout')

        self.set_sync_params({
            "login_user": login_params['user'],
            "test_login_user": login_params['test_user'],
            "login_password": login_params['password'],
            "test_login_password": login_params['test_password'],
            "login_url": login_params['url'],
            "test_login_url": login_params['test_url'],
            "logout_url": logout_params['url'],
            "test_logout_url": logout_params['test_url']
        })
        self.set_sync_params(self.get_param_sincro('b2c'))

    def get_data(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("a.referencia, ls.id, ls.idobjeto, ls.descripcion, ls.idobjeto_web, ls.node_id, ls.tiposincro, COALESCE(atr.pvp, a.pvp) AS pvp, atr.talla")
        q.setFrom("sincro_catalogo sc INNER JOIN lineassincro_catalogo ls ON sc.codsincro = ls.codsincro LEFT OUTER JOIN articulos a ON ls.idobjeto = a.referencia LEFT OUTER JOIN atributosarticulos atr ON ls.idobjeto = atr.barcode")
        where = "(sc.tiposincro = 'Enviar productos' OR sc.tiposincro = 'Borrar productos')"
        if where != "":
            where += " AND "
        if "codsincro" in self.params and self.params["codsincro"]:
            where += "sc.ptesincro AND ls.sincronizado = false AND ls.codsincro = '{}'  ORDER BY ls.id LIMIT 10".format(self.params["codsincro"])
        else:
            where += "sc.ptesincro AND ls.sincronizado = false ORDER BY ls.id LIMIT 10"
        q.setWhere(where)
        print("Consulta__body: ", q.sql())
        q.exec_()
        body = []
        if not q.size():
            return body

        while q.next():
            idlinea = str(q.value("ls.id"))
            sku = q.value("ls.idobjeto")
            title = q.value("ls.descripcion")
            tiposincro = q.value("ls.tiposincro")
            product_id = q.value("ls.idobjeto_web")
            node_id = q.value("ls.node_id")
            talla = q.value("atr.talla")
            pvp = q.value("pvp")
            amount = 0
            referencia = q.value("a.referencia") or q.value("ls.idobjeto").split("-")[0]
            if pvp is None or pvp == 0:
                pvp = qsatype.FLUtil.sqlSelect("articulos", "pvp", "referencia ='{}'".format(referencia))
            if pvp is None:
                pvp = 0
            amount = int(pvp * 100)
            qty = str(self.dame_stock(q.value("a.referencia"), q.value("ls.idobjeto")))
            # if tiposincro == "Enviar Talla" or tiposincro == "Borrar Talla":
            #     pvp = q.value("atr.pvp") or 0
            #     amount = int(pvp * 100)
            body.append({"idlinea": idlinea, "type": "product", "product_id": product_id, "node_id": node_id, "tiposincro": tiposincro, "sku": sku, "title": title, "commerce_price": {"amount": amount, "currency_code": "EUR"}, "talla": talla, "commerce_stock": qty})

        return body

    def sync(self):
        data = self.get_data()

        if data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return self.large_sleep

        for item in data:
            # idlinea = item["idlinea"]
            product_id = item["product_id"]
            tiposincro = item["tiposincro"]
            node_id = item["node_id"]
            talla = item["talla"]
            tid = ""

            if tiposincro == "Enviar Talla":
                tid = self.dame_talla(talla)
                if not tid:
                    tid = self.crea_talla(talla)
            if product_id and product_id is not None and product_id != "":
                if tiposincro == "Borrar Talla" or tiposincro == "Borrar Producto":
                    self.elimina_producto(item)
                else:
                    self.modifica_producto(item, str(tid))
            else:
                if node_id and node_id is not None and node_id != "":
                    if tiposincro == "Borrar Nodo":
                        self.elimina_nodo(item)
                    else:
                        self.modifica_nodo(item)
                else:
                    if tiposincro == "Enviar Nodo":
                        self.crea_nodo(item)
                    else:
                        self.crea_producto(item, str(tid))

        return self.small_sleep

    def dame_stock(self, referencia, barcode):
        where = "referencia = '{}'".format(referencia)
        if referencia != barcode:
            where = "referencia = '{}' AND barcode = '{}'".format(barcode.split("-")[0], barcode)
        print("where____disponible:", where)
        disponible = qsatype.FLUtil.quickSqlSelect("stocks", "disponible", where)
        print("Disponible-____:", disponible)
        if not disponible or isNaN(disponible) or disponible < 0:
            return 0.00

        return disponible

    def dame_talla(self, talla):
        self.set_sync_params(self.get_param_sincro('tallaGet'))
        response_data = self.send_request("get")
        for item in response_data:
            if item["name"] == talla:
                return item["tid"]
        return False

    def crea_talla(self, talla):
        self.set_sync_params(self.get_param_sincro('tallaCreate'))
        data = {"vid": "4", "name": talla}
        self.send_request("post", data=json.dumps(data))

        return self.dame_talla(talla)

    def crea_producto(self, item, talla=None):
        self.set_sync_params(self.get_param_sincro('productUpload'))
        data = {
            "type": "product",
            "sku": item["sku"],
            "title": item["title"],
            "commerce_price": item["commerce_price"],
            "commerce_stock": item["commerce_stock"],
        }

        if talla and talla != "":
            data["field_talla"] = talla

        response_data = self.send_request("post", data=json.dumps(data), replace=[""])
        if "field_talla" in response_data and response_data["field_talla"] and response_data["field_talla"] != "":
            qsatype.FLSqlQuery().execSql("UPDATE atributosarticulos SET product_id = {} WHERE barcode = '{}'".format(response_data["product_id"], item["sku"]))
        else:
            qsatype.FLSqlQuery().execSql("UPDATE articulos SET product_id = {} WHERE referencia = '{}'".format(response_data["product_id"], item["sku"]))

        self.after_sync_item(item["idlinea"])

        return True

    def modifica_producto(self, item, talla=None):
        self.set_sync_params(self.get_param_sincro('productUpload'))

        product_id = item["product_id"]

        data = {
            "type": "product",
            "sku": item["sku"],
            "title": item["title"],
            "commerce_price": item["commerce_price"],
            "commerce_stock": item["commerce_stock"]
        }

        if talla:
            data["field_talla"] = talla

        self.send_request("put", data=json.dumps(data), replace=["/{}".format(product_id)])
        self.after_sync_item(item["idlinea"])

        return True

    def elimina_producto(self, item):
        self.set_sync_params(self.get_param_sincro('productUpload'))

        product_id = item["product_id"]

        self.send_request("delete", data={}, replace=["/{}".format(product_id)])

        if item["tiposincro"] == "Borrar Talla":
            qsatype.FLSqlQuery().execSql("UPDATE atributosarticulos SET product_id = NULL WHERE barcode = '{}'".format(item["sku"]))
        elif item["tiposincro"] == "Borrar Producto":
            qsatype.FLSqlQuery().execSql("UPDATE articulos SET product_id = NULL WHERE referencia = '{}'".format(item["sku"]))

        self.after_sync_item(item["idlinea"])

        return True

    def crea_nodo(self, item):
        self.set_sync_params(self.get_param_sincro('nodeUpload'))

        products = self.dame_products_nodo(item["sku"])
        data = {
            "title": "prueba",
            "type": "producto",
            "field_producto": {"und": products}
        }

        # {"title":"prueba","type":"producto","field_producto":{"und":["19"]}}
        # {'type': 'product', 'field_producto': {'und': ['138']}, 'title': 'prueba'}
        response_data = self.send_request("post", data=json.dumps(data), replace=[""])
        qsatype.FLSqlQuery().execSql("UPDATE articulos SET node_id = {} WHERE referencia = '{}'".format(response_data["nid"], item["sku"]))
        self.after_sync_item(item["idlinea"])

        return True

    def modifica_nodo(self, item):
        self.set_sync_params(self.get_param_sincro('nodeUpload'))

        node_id = item["node_id"]
        products = self.dame_products_nodo(item["sku"])

        data = {
            "title": "prueba",
            "type": "producto",
            "field_producto": {"und": products}
        }

        self.send_request("put", data=json.dumps(data), replace=["/{}".format(node_id)])
        self.after_sync_item(item["idlinea"])

        return True

    def elimina_nodo(self, item):
        self.set_sync_params(self.get_param_sincro('nodeUpload'))

        node_id = item["node_id"]

        self.send_request("delete", data={}, replace=["/{}".format(node_id)])

        qsatype.FLSqlQuery().execSql("UPDATE articulos SET node_id = NULL WHERE referencia = '{}'".format(item["sku"]))
        self.after_sync_item(item["idlinea"])

        return True

    def dame_products_nodo(self, referencia):

        adatos = []
        q = qsatype.FLSqlQuery()
        q.setSelect("COALESCE(atr.product_id, a.product_id)")
        q.setFrom("articulos a LEFT OUTER JOIN atributosarticulos atr ON a.referencia = atr.referencia")
        q.setWhere("a.referencia = '{}'".format(referencia))
        if not q.exec_():
            return False

        while q.next():
            if q.value(0) is not None:
                adatos.append(q.value(0))
        return adatos

    def after_sync(self, codsincro=None):
        qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = false, fecha = '{}', hora = '{}' WHERE codsincro =  '{}'".format(self.start_date, self.start_time, codsincro))
        self.log("Éxito", "Productos sincronizados correctamente.")

        return True

    def after_sync_item(self, idlinea):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = true WHERE id =  {}".format(idlinea))
        codsincro = qsatype.FLUtil.quickSqlSelect("lineassincro_catalogo", "codsincro", "id = '{}'".format(idlinea))
        print("CodSincro_____:", codsincro)
        idlinea = qsatype.FLUtil.quickSqlSelect("lineassincro_catalogo", "id", "sincronizado = false AND  codsincro = '{}'".format(codsincro))
        print("idlinea______:", idlinea)
        if idlinea is False or idlinea is None:
            self.after_sync(codsincro)
        return True
