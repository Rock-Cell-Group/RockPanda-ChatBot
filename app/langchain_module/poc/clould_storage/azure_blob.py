import os
import uuid
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Create a unique name for the container
container_name = "rag-hackathon-demo"

# 只有在生成新的容器的時候才需要這行(所屬結構：storage account -> "container" -> blob)
# blob_service_client.create_container(container_name)

# 取得container的client
container_client = blob_service_client.get_container_client(container_name)


def upload_blob_file(blob_service_client: BlobServiceClient, container_name: str, local_file_path: str,
                     local_file_name: str):
    container_client = blob_service_client.get_container_client(container=container_name)
    with open(file=os.path.join(local_file_path, local_file_name), mode="rb") as data:
        blob_client = container_client.upload_blob(name=local_file_name, data=data, overwrite=True)


def download_blob_to_file(blob_service_client: BlobServiceClient, container_name: str, blob_name: str,
                          save_file_path: str):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    with open(file=os.path.join(save_file_path, blob_name), mode="wb") as sample_blob:
        download_stream = blob_client.download_blob()
        sample_blob.write(download_stream.readall())


def delete_blob(blob_service_client: BlobServiceClient, container_name: str, blob_name: str):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.delete_blob()

local_file_path = "C://Users//kwz50//PycharmProjects//RAG_ChatBot//data//Upload_Data//"
local_file_name = "8ea989e0-66c8-4479-9c9e-d33a536ec108.pdf"
save_file_path = "C://Users//kwz50//PycharmProjects//RAG_ChatBot//data//Download_Data//"

# # 上傳檔案至container
upload_blob_file(blob_service_client, container_name, local_file_path, local_file_name)

# 下載container中的檔案
download_blob_to_file(blob_service_client, container_name, local_file_name, save_file_path)

# 刪除container中的檔案
delete_blob(blob_service_client, container_name, local_file_name)
