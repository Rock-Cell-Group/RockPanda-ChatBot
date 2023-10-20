import sys
sys.path.append('./langchain_modules')

from langchain.Chat_module import ChatBOT

result = ChatBOT().main("吳亦烜大三開學時加入哪個老師的實驗")
print(result)
