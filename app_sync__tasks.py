from controllers.api.sync.base.task_manager import TaskManager
from controllers.api.sync.base.drivers.drupal_driver import DrupalDriver
from controllers.api.sync.products.upload import GpProductsUpload


sync_object_dict = {
    "products_upload": {
        "sync_object": GpProductsUpload,
        "driver": DrupalDriver
    }
}

task_manager = TaskManager(sync_object_dict)


def getActivity():
    return task_manager.get_activity()


def revoke(id):
    return task_manager.revoke(id)


def products_upload(request, params={}):
    task_manager.task_executer(request, "products_upload", params)
