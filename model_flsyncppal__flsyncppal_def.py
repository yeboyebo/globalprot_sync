
# @class_declaration globalprot_sync #
class globalprot_sync(flsyncppal):

    def globalprot_sync_get_customer(self):
        return "globalprot"

    def __init__(self, context=None):
        super().__init__(context)

    def get_customer(self):
        return self.ctx.globalprot_sync_get_customer()

