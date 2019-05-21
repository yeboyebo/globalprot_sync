# @class_declaration interna_lineassincro_catalogo #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_lineassincro_catalogo(modelos.mtd_lineassincro_catalogo, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration globalprot_sync_lineassincro_catalogo #
class globalprot_sync_lineassincro_catalogo(interna_lineassincro_catalogo, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration lineassincro_catalogo #
class lineassincro_catalogo(globalprot_sync_lineassincro_catalogo, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.lineassincro_catalogo_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
