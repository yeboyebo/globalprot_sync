from controllers.api.sync.base.controllers.aqsync_download import AQSyncDownload
from controllers.api.sync.orders.serializers.gporder_serializer import GpOrderSerializer
from YBLEGACY import qsatype

from models.flfacturac.objects.gporder_raw import GpOrder


class GpOrdersDownload(AQSyncDownload):

    def __init__(self, driver, params=None):
        super().__init__("gpsyncorders", driver, params)

    def start(self):
        try:
            data = self.params
            if "idpedidoweb" not in data or data["idpedidoweb"] is None or data["idpedidoweb"] == "":
                self.log("Error", "El objeto no tiene idpedidoweb")
                return {"countdown": self.large_sleep, "data": {"log": self.logs}, "status": 500}

            codigo = qsatype.FLUtil.quickSqlSelect("pedidoscli", "codigo", "idpedidoweb = '{}'".format(data["idpedidoweb"]))
            if codigo:
                self.log("Error", "El pedidoweb {} con codigo {} ya esta cargado en la Erp".format(data["idpedidoweb"], codigo))
                return {"countdown": self.large_sleep, "data": {"log": self.logs}, "status": 500}

            order_data = GpOrderSerializer().serialize(data)
            if not order_data:
                self.log("Error", "Error con cargar el pedido.")
                return {"countdown": self.large_sleep, "data": {"log": self.logs}, "status": 500}
            order = GpOrder(order_data)
            order.save()
            return {"countdown": self.small_sleep, "data": {"log": self.logs}, "status": 200}

        except Exception as e:
            self.log("Error", e)
            return {"countdown": self.large_sleep, "data": {"log": self.logs}, "status": 500}

    def after_sync(self):
        return True

    def process_data(self, data):
        return True
