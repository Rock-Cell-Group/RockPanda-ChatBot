from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

template = """問題: {question}
答案:"""

prompt = PromptTemplate(template=template, input_variables=["question"])

# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path="C://Users//kwz50//Chinese-Llama-2-7b//llama-2-13b-chat.ggmlv3.q4_0.gguf.bin",
    temperature=0.0,
    max_tokens=2000,
    top_p=1,
    callback_manager=callback_manager,
    verbose=True,  # Verbose is required to pass to the callback manager
)

prompt = """
Question: A rap battle between Stephen Colbert and John Oliver
"""
llm(prompt)

# llm_chain = LLMChain(prompt=prompt, llm=llm)
# question = "What NFL team won the Super Bowl in the year Justin Bieber was born?"
# llm_chain.run(question)


# python C:\Users\kwz50\PycharmProjects\RAG_ChatBot\langchain_modules\convert_llama_ggml_to_gguf.py --eps 1e-5 -i C://Users//kwz50//Chinese-Llama-2-7b//Chinese-Llama-2-7b-ggml-q4.bin -o C://Users//kwz50//Chinese-Llama-2-7b//llama-2-13b-chat.ggmlv3.q4_0.gguf.bin