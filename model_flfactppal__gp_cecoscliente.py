# @class_declaration interna_gp_cecoscliente #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactppal import models as modelos


class interna_gp_cecoscliente(modelos.mtd_gp_cecoscliente, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration globalprot_sync_gp_cecoscliente #
class globalprot_sync_gp_cecoscliente(interna_gp_cecoscliente, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration gp_cecoscliente #
class gp_cecoscliente(globalprot_sync_gp_cecoscliente, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactppal.gp_cecoscliente_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
