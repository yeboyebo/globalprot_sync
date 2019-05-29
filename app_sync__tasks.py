from controllers.api.sync.base.controllers.task_manager import TaskManager
from controllers.api.sync.products.controllers.products_upload import GpProductsUpload
from controllers.api.sync.users.controllers.users_upload import GpUsersUpload
from controllers.api.sync.orders.controllers.gporders_download import GpOrdersDownload
from controllers.api.sync.base.drivers.drupal_driver import DrupalDriver


sync_object_dict = {
    "products_upload": {
        "sync_object": GpProductsUpload,
        "driver": DrupalDriver
    },
    "users_upload": {
        "sync_object": GpUsersUpload,
        "driver": DrupalDriver
    },
    "orders_download": {
        "sync_object": GpOrdersDownload
    }
}

task_manager = TaskManager(sync_object_dict)
