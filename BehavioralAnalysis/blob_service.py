from azure.storage.blob import BlockBlobService
from azure.storage.common import CloudStorageAccount

class BlobService:

    def __init__(self, account_name, account_key, container_name):
        account = CloudStorageAccount(account_name, account_key)
        self.blob_service_ref = account.create_block_blob_service()
        self.container_name = container_name

    def store_blob(self, source_path, destination_path):
        self.blob_service_ref.create_blob_from_path(
            self.container_name,
            destination_path,
            source_path
        )

    def get_blob(self, source_path, destination_path):
        self.blob_service_ref.get_blob_to_path(
            self.container_name,
            source_path,
            destination_path
        )