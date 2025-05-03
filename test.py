from langchain_text_splitters import MarkdownTextSplitter
from rag import NvidiaRAGPipeline
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import os
from rag import InputDocument

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

llm = ChatNVIDIA(
  model="meta/llama-3.1-8b-instruct",
  api_key=api_key, 
  temperature=0.2,
  top_p=0.7,
  max_tokens=1024,
)

with open("bunq_full_docs.txt", 'r', encoding="utf-8") as file:
    content = file.read()

text_splitter = MarkdownTextSplitter()
texts = text_splitter.split_text(content)

input_documents = []
for text in texts:
    input_documents.append(InputDocument(content=text, metadata={"source": None}))

# prompt = "Summarize the following text: " + texts[100]
# output  = llm.invoke(prompt)
# print(output.content)




rag_pipeline = NvidiaRAGPipeline(input_documents=input_documents, retrieve_k=20, rerank_k=5)
query1 = "Tell me the account information for service providers?"
query2 = "Which is the bunq api object directly connected to the user and why is it directly connected?"
print(f"\nUser: {query1}")
response1, sources1 = rag_pipeline.generate_response(query2)
print(f"Assistant: {response1}")
print(f"Sources Used: {sources1}")