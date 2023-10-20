import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from langchain.document_loaders.pdf import DocumentIntelligenceLoader

load_dotenv()
document_analysis_client = DocumentAnalysisClient(
    endpoint=f"{os.getenv('AZURE_OCR_ENDPOINT')}",
    credential=AzureKeyCredential(f"{os.getenv('AZURE_OCR_CREDENTIAL_KEY')}")
)

loader = DocumentIntelligenceLoader(
    "C://Users//kwz50//PycharmProjects//RAG_ChatBot//data//Raw_Data//JPG//09110_B1__final_1.jpg",
    client=document_analysis_client,
    model="prebuilt-document")  # e.g. prebuilt-document

documents = loader.load()

print(documents[0].page_content)
print(documents[0].metadata)
