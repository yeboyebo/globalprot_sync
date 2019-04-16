
# @class_declaration globalprot_sync #
from sync import tasks


class globalprot_sync(flfactppal):

    def globalprot_sync_products_upload(self, params):
        tasks.products_upload(params['fakeRequest'], params)

        return True

    def __init__(self, context=None):
        super().__init__(context)

    def products_upload(self, params):
        return self.ctx.globalprot_sync_products_upload(params)

