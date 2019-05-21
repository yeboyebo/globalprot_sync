# @class_declaration interna_gp_usutiendaonline #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactppal import models as modelos


class interna_gp_usutiendaonline(modelos.mtd_gp_usutiendaonline, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration globalprot_sync_gp_usutiendaonline #
class globalprot_sync_gp_usutiendaonline(interna_gp_usutiendaonline, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration gp_usutiendaonline #
class gp_usutiendaonline(globalprot_sync_gp_usutiendaonline, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactppal.gp_usutiendaonline_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
