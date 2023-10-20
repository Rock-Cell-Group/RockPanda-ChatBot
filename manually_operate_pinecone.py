# import sys
# sys.path.append('./langchain_modules')

from langchain.KnowledegeEmbedding_module import KnowledegeEmbedding

path = 'data/Raw_Data/TXTs'

KnowledegeEmbed = KnowledegeEmbedding()
docs_split = KnowledegeEmbed.txt_preprocessing(path)
print("docs_split type is: ", type(docs_split))
data_with_embedded_vector = KnowledegeEmbed.create_metadata_embeddings(docs_split, 'about_course')
print("data_with_embedded_vector type is: ", type(data_with_embedded_vector))
KnowledegeEmbed.upsert_embedding_to_db(data_with_embedded_vector)

'''
用聖凱的免費帳號embedding時會出現這個error
Retrying langchain.embeddings.openai.embed_with_retry.<locals>._embed_with_retry in 4.0 seconds as it raised RateLimitError: 
Rate limit reached for default-text-embedding-ada-002 in organization org-VrxTMiVTTkCDdOgTYNlerjTZ on requests per min. Limit: 3 / min. 
Please try again in 20s. Contact us through our help center at help.openai.com if you continue to have issues. 
Please add a payment method to your account to increase your rate limit. Visit https://platform.openai.com/account/billing to add a payment method..
'''


#KnowledegeEmbedding().pineconeInstance.update(id="id-3", set_metadata={"type": "web", "new": True})