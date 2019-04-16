
# @class_declaration globalprot_sync_empresa #
class globalprot_sync_empresa(flfactppal_empresa, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def getactivity(params):
        return form.iface.getActivity(params)

    @helpers.decoradores.csr()
    def revoke(params):
        return form.iface.revoke(params)

    @helpers.decoradores.csr()
    def products_upload(params):
        return form.iface.products_upload(params)

