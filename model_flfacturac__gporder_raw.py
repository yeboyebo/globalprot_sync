from models.flsyncppal.objects.aqmodel_raw import AQModel
from YBLEGACY import qsatype


from models.flfacturac.objects.gporder_line_raw import GpOrderLine


class GpOrder(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("pedidoscli", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        cursor.setActivatedCommitActions(True)
        # if not qsatype.FactoriaModulos.get('flfactppal').iface.pub_controlDatosMod(cursor):
        #     return False

        return cursor

    def get_children_data(self):
        for item in self.data["children"]["lines"]:
            self.children.append(GpOrderLine(item))
