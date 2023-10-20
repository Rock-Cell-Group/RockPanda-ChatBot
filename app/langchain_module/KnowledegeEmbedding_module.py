import os
import pinecone
from typing import Optional, List, Union, Dict
from uuid import uuid4
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from app.langchain_module.execution_time_decorator import calculate_execution_time

load_dotenv()


class KnowledegeEmbedding:
    def __init__(self):
        self.PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        self.PINECONE_ENV = os.getenv('PINECONE_ENV')
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        # os.environ['OPENAI_API_KEY'] = self.OPENAI_API_KEY
        self.index_name = 'langchain-demo'
        pinecone.init(api_key=self.PINECONE_API_KEY, environment=self.PINECONE_ENV)
        self.pineconeInstance = pinecone.Index(self.index_name)  # 建立pinecone client instance，可直接對pinecone操作
        print("pineconeInstance information", self.pineconeInstance.describe_index_stats())

    def pdf_preprocessing(self, Directory: str):
        loader = DirectoryLoader(path=Directory, glob='**/*.pdf', show_progress=True, use_multithreading=True)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs_split = text_splitter.split_documents(docs)

        return docs_split

    def txt_preprocessing(self, Directory: str):
        loader = DirectoryLoader(path=Directory, glob='**/*.txt', show_progress=True, use_multithreading=True)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs_split = text_splitter.split_documents(docs)

        return docs_split

    @calculate_execution_time
    # TODO uuid4改我們自定義的id這樣之後pineconeInstance.fetch()或是update,delete的功能才比較好直接針對特定vector操作(知道id)
    def create_metadata_withembeddings(self, docs_split: List, metadata_pairs: Optional[
        Dict[str, Union[str, float, bool, List[str]]]] = None) -> List[dict]:
        '''
        #usage example like below
        metadata_pairs = {"namespace":'about_course', "upsert_date":'20231007'}
        data_objs = create_metadata_withembeddings(docs_split, metadata_pairs)
        '''
        data_objs = []
        embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')

        for split_doc in docs_split:
            eachdoc = {
                "id": str(uuid4()),
                "values": embeddings.embed_documents([split_doc.page_content])[0],
                "metadata": {
                    "source": split_doc.metadata['source'],
                    "text": split_doc.page_content
                }
            }

            if metadata_pairs:
                for key, value in metadata_pairs.items():
                    if not isinstance(key, str):
                        raise ValueError(f"Unsupported key type: {type(key)}")
                    if not isinstance(value, (str, float, bool, list)):
                        raise ValueError(f"Unsupported type for key {key}: {type(value)}")
                    eachdoc["metadata"][key] = value

            data_objs.append(eachdoc)

        # Return list of dictionaries, each containing our id, embedding value(vector), metadata per split_doc.
        return data_objs

    # 不支援啦幹Projects in the gcp-starter region do not support upsert embedding to namespace.
    def upsert_embedding_to_db_namespace(self, data: List[dict], namespace: str):
        '''
        把data_objs, 透過pineconeInstance進行upsert, namespace是選課相關
        example: upsert_embedding_to_db(data_objs, "aboutCourse")
        '''
        self.pineconeInstance.upsert(vectors=data, namespace=namespace)
        # TODO 不知道為啥try的寫法都不會正常return，之後再看看
        # try:
        #     self.pineconeInstance.upsert(vectors=data, namespace=namespace)
        #     return "upsert successfully"
        # except:
        #     return "Error"

    @calculate_execution_time
    # (modele名稱可以看出，小寫p是pinecone官方的，大寫P是langchain包起來的)
    # TODO 目前沒有idempotent
    def upsert_embedding_to_db(self, data: List[dict]):
        '''
        把data_objs, 透過pineconeInstance進行upsert, 不放到namespace
        example: upsert_embedding_to_db(data_objs)
        '''
        self.pineconeInstance.upsert(vectors=data)
        # try:
        #     self.pineconeInstance.upsert(vectors=data)
        #     return "upsert successfully"
        # except:
        #     return "Error"

    @calculate_execution_time
    def delete_embedding_ids(self, ids: List[str]):
        # TODO mysql table with id + metadata tag, delete by id
        try:
            self.pineconeInstance.delete(ids=ids)
            return "delete successfully"
        except:
            return "Error"

    # 暫時不會用到所以也還沒測試，因為vector query包在retrivialQA裡面，不用自己call。
    def query_embedding_metadatafilter(self, k: int, query_vector: List[float], metadata_key: Optional[str] = None,
                                       metadata_value: Optional[Union[str, float, bool, List[str]]] = None):
        '''
        k是要傳回前幾相近的比對結果
        query_vector是要比對的vector, 以我們的用法是初始問句經過embedding後的1536維(ada2)向量
        metadata_key(optional)是pinecone裡面, 各筆資料中存的metadata鍵值的鍵
        metadata_value(optional)是pinecone裡面, 各筆資料中存的metadata鍵值的值
        '''
        filter_dict = {}  # 創建一個空的字典，用於存儲過濾條件

        if metadata_key is not None and metadata_value is not None:
            # 根據 metadata_value 的實際類型添加到過濾條件中
            if isinstance(metadata_value, str):
                filter_dict[metadata_key] = metadata_value
            elif isinstance(metadata_value, (int, float)):
                filter_dict[metadata_key] = float(metadata_value)  # 將整數轉換為浮點數
            elif isinstance(metadata_value, bool):
                filter_dict[metadata_key] = metadata_value
            elif isinstance(metadata_value, list) and all(isinstance(item, str) for item in metadata_value):
                filter_dict[metadata_key] = metadata_value
            else:
                raise ValueError("metadata_value 的類型不受支持")
        elif metadata_key is None and metadata_value is not None:
            raise ValueError("Missing metadata_key")
        elif metadata_key is not None and metadata_value is None:
            raise ValueError("Missing metadata_value")

        query_response = self.pineconeInstance.query(
            vector=query_vector,
            top_k=k,
            include_values=False,
            include_metadata=True,
            filter=filter_dict  # 使用創建的過濾條件字典
        )

        return query_response

    # 不支援啦幹Projects in the gcp-starter region do not support upsert embedding to namespace.
    # @calculate_execution_time
    # def delete_all_embedding_namespace(self, namespace: str):
    #     try:
    #         self.pineconeInstance.delete(delete_all=True, namespace=namespace)
    #         return "upsert successfully"
    #     except:
    #         return "Error"

    # 不支援啦幹Projects in the gcp-starter region do not support deleting by metadata.
    # def delete_all_embedding_metadatafilter(self, metadatafilter: dict):
    #     try:
    #         self.pineconeInstance.delete(filter=metadatafilter)
    #         return "upsert successfully"
    #     except:
    #         return "Error"
    # 知識庫中的向量不能用metadata刪的話只能先找到id再刪了

    @calculate_execution_time
    def deprecated_upsert_embedding_to_db(self):

        embeddings = OpenAIEmbeddings()
        # pinecone.init(api_key=self.PINECONE_API_KEY, environment=self.PINECONE_ENV)
        docs_split = self.pdf_preprocessing()
        doc_db = Pinecone.from_documents(docs_split, embeddings, index_name=self.index_name)

        return doc_db

    @calculate_execution_time
    def get_embedding_from_db(self):

        # get old index db
        embeddings = OpenAIEmbeddings()
        # pinecone.init(api_key=self.PINECONE_API_KEY, environment=self.PINECONE_ENV)
        doc_db = Pinecone.from_existing_index(index_name=self.index_name, embedding=embeddings)

        return doc_db

    # langchain包起來的upsert功能，功能上應該完全跟我寫的upsert_embedding_to_db_namespace(create_metadata_embeddings(docs_split))一樣。
    # (modele名稱可以看出，小寫p是pinecone官方的，大寫P是langchain包起來的)
    def upsert_embedding_to_db_using_langchain(self, docs_split: list, namespace: str):
        docs_split = docs_split
        embeddings = OpenAIEmbeddings()
        vectorstore = Pinecone.from_documents(
            docs_split,
            embeddings,
            metadata_fields=["namespace", namespace]
        )

        return vectorstore

    # 如何query by metadata-filtering參見https://docs.pinecone.io/docs/metadata-filtering
