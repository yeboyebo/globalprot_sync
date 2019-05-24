import json

from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.sync.base.controllers.aqsync_upload import AQSyncUpload


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
            "login_url": "http://dev9.yeclaweb.com/erpglobal/user/login",
            "test_login_url": "http://dev9.yeclaweb.com/erpglobal/user/login",
            "logout_url": "http://dev9.yeclaweb.com/erpglobal/user/logout",
            "test_logout_url": "http://dev9.yeclaweb.com/erpglobal/user/logout"
        })

    def get_data(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("a.referencia, ls.id, ls.idobjeto, ls.descripcion, ls.idobjeto_web, ls.node_id, ls.tiposincro, COALESCE(atr.pvp, a.pvp) AS pvp, atr.talla,s.disponible")
        q.setFrom("lineassincro_catalogo ls LEFT OUTER JOIN articulos a ON ls.idobjeto = a.referencia LEFT OUTER JOIN atributosarticulos atr ON ls.idobjeto = atr.barcode  LEFT OUTER JOIN stocks s ON (ls.idobjeto = s.referencia OR ls.idobjeto = s.barcode)")
        q.setWhere("ls.codsincro = '{}' AND ls.sincronizado = false ORDER BY ls.tiposincro DESC".format(self.params["codsincro"]))

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
            print("referencia:", referencia)
            print("pvp___11111:", pvp)
            if pvp is None or pvp == 0:
                pvp = qsatype.FLUtil.sqlSelect("articulos", "pvp", "referencia ='{}'".format(referencia))
                print("pvp___222222:", pvp)
            amount = int(pvp * 100)
            print("amount_________:", amount)
            qty = str(self.dame_stock(q.value("s.disponible")))
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
                    response_data = self.elimina_producto(item)
                else:
                    response_data = self.modifica_producto(item, str(tid))
            else:
                if node_id and node_id is not None and node_id != "":
                    if tiposincro == "Borrar Nodo":
                        response_data = self.elimina_nodo(item)
                    else:
                        response_data = self.modifica_nodo(item)
                else:
                    if tiposincro == "Enviar Nodo":
                        response_data = self.crea_nodo(item)
                    else:
                        response_data = self.crea_producto(item, str(tid))

        return self.after_sync()

    def dame_stock(self, disponible):
        if not disponible or isNaN(disponible) or disponible < 0:
            return 0.00

        return disponible

    def dame_talla(self, talla):
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/taxonomy_term?parameters[vid]=4",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/taxonomy_term?parameters[vid]=4"
        })
        response_data = self.send_request("get")
        for item in response_data:
            if item["name"] == talla:
                return item["tid"]
        return False

    def crea_talla(self, talla):
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/taxonomy_term",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/taxonomy_term"
        })
        data = {"vid": "4", "name": talla}
        self.send_request("post", data=json.dumps(data))

        return self.dame_talla(talla)

    def crea_producto(self, item, talla=None):
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/product{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/product{}"
        })
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
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/product{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/product{}"
        })

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
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/product{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/product{}"
        })

        product_id = item["product_id"]

        self.send_request("delete", data={}, replace=["/{}".format(product_id)])

        if item["tiposincro"] == "Borrar Talla":
            qsatype.FLSqlQuery().execSql("UPDATE atributosarticulos SET product_id = NULL WHERE barcode = '{}'".format(item["sku"]))
        elif item["tiposincro"] == "Borrar Producto":
            qsatype.FLSqlQuery().execSql("UPDATE articulos SET product_id = NULL WHERE referencia = '{}'".format(item["sku"]))

        self.after_sync_item(item["idlinea"])

        return True

    def crea_nodo(self, item):
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/node{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/node{}"
        })
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
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/node{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/node{}"
        })
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
        self.set_sync_params({
            "url": "http://dev9.yeclaweb.com/erpglobal/node{}",
            "test_url": "http://dev9.yeclaweb.com/erpglobal/node{}"
        })

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

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = false, fecha = '{}', hora = '{}' WHERE codsincro =  '{}'".format(self.start_date, self.start_time, self.params["codsincro"]))
        self.log("Éxito", "Productos sincronizados correctamente (codsincro: {})".format(self.params["codsincro"]))

        return self.small_sleep

    def after_sync_item(self, idlinea):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = true WHERE id =  {}".format(idlinea))
