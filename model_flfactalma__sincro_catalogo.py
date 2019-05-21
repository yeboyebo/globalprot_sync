# @class_declaration interna_sincro_catalogo #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_sincro_catalogo(modelos.mtd_sincro_catalogo, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration globalprot_sync_sincro_catalogo #
class globalprot_sync_sincro_catalogo(interna_sincro_catalogo, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration sincro_catalogo #
class sincro_catalogo(globalprot_sync_sincro_catalogo, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.sincro_catalogo_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
