import os
from typing import Optional, List, Union
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from app.langchain_module.KnowledegeEmbedding_module import KnowledegeEmbedding
from app.langchain_module.execution_time_decorator import calculate_execution_time

load_dotenv()


class ChatBOT:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        os.environ['OPENAI_API_KEY'] = self.OPENAI_API_KEY
        self.setup_openai()
        # self.setup_memory()
        # self.setup_chat_history_from_memory()

    @calculate_execution_time
    def setup_openai(self):
        # You can use local model here, for instance, llama2
        # self.llm = ChatOpenAI(temperature=0.3)
        self.llm = OpenAI(model_name="gpt-3.5-turbo-instruct", temperature=0.3, max_tokens=-1) #不要用chat快多了。


    # TODO prompt跟model要再試，現在這個prompt用text-davinci-003還不錯但就貴貴而且再兩個月停止服務
    @calculate_execution_time
    def generate_similar_question(self, question):
        prompt_template = """Given the question: {Original_question},  please provide a related question (with same question type, \
            i.e., multiple choice, short answer, fill in the gaps, matching, etc.)that assesses the same concept or topic."""
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["Original_question"])
        llm = OpenAI(model_name="gpt-3.5-turbo-instruct", temperature=0, max_tokens=-1)
        chain = LLMChain(llm=llm, prompt=PROMPT)

        similar_question = chain.apply([{"Original_question":question}])[0]['text']
        similar_question_stripped = similar_question.strip()
        return similar_question_stripped
    
    @calculate_execution_time
    def answer_to_this_question(self, question):
        # prompt_template = """Please provide an answer to the question: {question_tobe_explain}, and provide explanation for your answer,both in Mandarin with Traditional Chinese:
        # Explanation: In your response, offer a well-reasoned answer, and provide a brief explanation of the reasoning behind your response."""
        prompt_template = """請提供這個問題的答案與解釋，請用繁體中文，回答請少於300字
        問題:{question_tobe_explain}"""
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["question_tobe_explain"])
        llm = OpenAI(model_name="gpt-3.5-turbo-instruct", temperature=0, max_tokens=-1)
        chain = LLMChain(llm=llm, prompt=PROMPT)

        question_explanation = chain.apply([{"question_tobe_explain":question}])[0]['text']
        question_explanation_stripped = question_explanation.strip()
        return question_explanation_stripped

    # def setup_memory(self):
    #     self.memory = ConversationBufferWindowMemory(
    #         input_key="question",
    #         return_messages=True,
    #         memory_key="chat_history",
    #         k=3
    #     )

    # def setup_chat_history_from_memory(self):
    #     memory_variables = self.memory.load_memory_variables({})
    #     self.chat_history = memory_variables['history']

    @calculate_execution_time
    def retrieval_answer(self, query: str, metadata_key: Optional[str] = None,
                         metadata_value: Optional[Union[str, float, bool, List[str]]] = None):
        '''
        可傳入metadata_key跟metadata_value來過濾篩選條件, 加速搜尋
        '''
        filter_dict = {}  # 創建一個空的字典，用於存儲過濾條件
        search_kwargs = None

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
            search_kwargs = {'filter': filter_dict}
        elif metadata_key is None and metadata_value is not None:
            raise ValueError("Missing metadata_key")
        elif metadata_key is not None and metadata_value is None:
            raise ValueError("Missing metadata_value")
        search_kwargs = {'filter': filter_dict}
        # pineconedb = KnowledegeEmbedding().pineconeInstance
        pineconedb = KnowledegeEmbedding().get_embedding_from_db()
        '''
        # Below is memory-version
        qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=pineconedb.as_retriever(search_kwargs=search_kwargs),
            chain_type="stuff",
            verbose=False,
            memory=self.memory,
        )
        chat_history = []
        result = qa.run({"question": query, "chat_history": chat_history})
        '''

        # TODO 如果method拆開，是否可以先用fuzzy-wuzzy做字串比對，底對是否在熱門詢問的範圍內，如果是的話就直接回答，不用再跑retrievalQA
        qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type='stuff',
                                         retriever=pineconedb.as_retriever(search_kwargs=search_kwargs))
        result = qa.run(query)
        result_stripped = result.strip()

        return result_stripped
