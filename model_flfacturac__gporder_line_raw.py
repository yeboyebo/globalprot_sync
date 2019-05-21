from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal.objects.aqmodel_raw import AQModel


class GpOrderLine(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("lineaspedidoscli", init_data, params)

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idpedido", parent_cursor.valueBuffer("idpedido"))
        self.set_data_value("numlinea", self.get_numlinea())

    def get_numlinea(self):
        numlinea = parseInt(qsatype.FLUtil.quickSqlSelect("lineaspedidoscli", "count(*)", "idpedido = {}".format(self.data["idpedido"])))

        if isNaN(numlinea):
            numlinea = 0

        return numlinea + 1
