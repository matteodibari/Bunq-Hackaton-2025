import os
from typing import List, Tuple, Union, Optional, Dict, Any
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field # Keep for potential external data structures

# Langchain Imports
from langchain_core.documents import Document as LangchainDocument
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, NVIDIARerank, ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from utils import InputDocument 

# --- Configuration ---
# Ensure your NVIDIA API key is set as an environment variable
if "NVIDIA_API_KEY" not in os.environ:
    raise ValueError("NVIDIA_API_KEY environment variable not set.")

# Replace with the specific NVIDIA model names you have access to
# Check NVIDIA AI Endpoints documentation for available models
NVIDIA_EMBED_MODEL = "nvidia/nv-embed-v1"  # Example embedding model
NVIDIA_RERANK_MODEL = "nv-rerank-qa-mistral-4b:1" # Example rerank model
NVIDIA_CHAT_MODEL = "meta/llama-3.1-8b-instruct" # Example chat model

EMBED_BATCH_SIZE = 100 # Keep batch size concept for embedding efficiency

# --- Pydantic Model (Optional - Use if needed for input/output) ---
# You might still use Pydantic for structuring input data before converting to Langchain Documents

# --- RAG Pipeline Class ---
class NvidiaRAGPipeline:
    """
    Implements a RAG pipeline using NVIDIA models via Langchain.
    Note: This is a standard Vector RAG, not yet Graph RAG.
    """
    def __init__(self, input_documents: List[InputDocument] = None, retrieve_k: int = 10, rerank_k: int = 3):
        """
        Initialize the RAG pipeline with NVIDIA components.

        Args:
            input_documents: List of InputDocument objects to process.
        """
        print("Initializing NVIDIA RAG Pipeline...")

        self.retrieve_k = retrieve_k
        self.rerank_k = rerank_k


        # --- Initialize NVIDIA Clients ---
        self.embedder = NVIDIAEmbeddings(model=NVIDIA_EMBED_MODEL)
        # Reranker requires the model name during initialization
        self.reranker = NVIDIARerank(model=NVIDIA_RERANK_MODEL, top_n=self.rerank_k) # Set top_n here
        self.llm = ChatNVIDIA(model=NVIDIA_CHAT_MODEL)

        # --- Process and Store Documents ---
        self.documents: List[LangchainDocument] = [] # Store as Langchain Documents
        self.embeddings: List[List[float]] = [] # Store embeddings separately

        
        if input_documents:
            self.documents = [
                LangchainDocument(page_content=doc.content, metadata=doc.metadata)
                for doc in input_documents
            ]
            print(f"Processing {len(self.documents)} documents...")

            if os.path.exists("embeddings.npy"):
                # Load existing embeddings if available
                self.embeddings = np.load("embeddings.npy", allow_pickle=True).tolist()
                print("Loaded existing embeddings from 'embeddings.npy'.")
            else:
                self._ensure_embeddings()
                # Save embeddings to a file for later use (optional)
                np.save("embeddings.npy", self.embeddings)
                print("Embeddings saved to 'embeddings.npy'.")
        else:
            print("Warning: No initial documents provided.")

        print("NVIDIA RAG Pipeline Initialized.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Gets embeddings for a batch of texts using NVIDIAEmbeddings."""
        try:
            print(f"Requesting embeddings for batch of {len(texts)}...")
            embeddings = self.embedder.embed_documents(texts)
            print("Embeddings received.")
            return embeddings
        except Exception as e:
            print(f"NVIDIA Embedding error: {str(e)}")
            raise

    def _ensure_embeddings(self):
        """Ensure all documents have embeddings, using batched requests."""
        if not self.documents:
            return

        print("Ensuring all documents have embeddings...")
        docs_to_embed_indices = [i for i, emb in enumerate(self.embeddings) if not emb] # Assuming initial empty list or placeholder

        # Adjust if embeddings list isn't pre-populated
        if len(self.embeddings) < len(self.documents):
             self.embeddings.extend([[] for _ in range(len(self.documents) - len(self.embeddings))])
             docs_to_embed_indices = list(range(len(self.documents))) # Embed all if list was empty


        texts_to_embed = [self.documents[i].page_content for i in docs_to_embed_indices]
        doc_map = {i: original_index for i, original_index in enumerate(docs_to_embed_indices)}

        if not texts_to_embed:
            print("All documents already have embeddings.")
            return

        for i in range(0, len(texts_to_embed), EMBED_BATCH_SIZE):
            batch_texts = texts_to_embed[i:i + EMBED_BATCH_SIZE]
            batch_indices = [doc_map[idx + i] for idx in range(len(batch_texts))]

            if not batch_texts:
                continue

            batch_embeddings = self._get_embeddings_batch(batch_texts)

            # Assign embeddings back
            for original_index, embedding in zip(batch_indices, batch_embeddings):
                 if original_index < len(self.embeddings):
                    self.embeddings[original_index] = embedding
                 else:
                     print(f"Warning: Index {original_index} out of bounds for embeddings list.")


        # Verify
        missing_count = sum(1 for emb in self.embeddings if not emb)
        if missing_count == 0:
            print("All documents successfully embedded.")
        else:
             print(f"Warning: {missing_count} documents still lack embeddings after processing.")


    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec_a = np.array(a)
        vec_b = np.array(b)
        # Handle potential zero vectors
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return np.dot(vec_a, vec_b) / (norm_a * norm_b)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _rerank(self, query: str, documents: List[LangchainDocument]) -> List[LangchainDocument]:
        """Rerank documents using NVIDIARerank."""
        if not documents:
            return []
        print(f"Reranking {len(documents)} documents for query: '{query[:50]}...'")
        try:
            # NVIDIARerank expects Langchain Documents directly
            reranked_docs = self.reranker.compress_documents(query=query, documents=documents)
            print(f"Reranked, returning {len(reranked_docs)} documents.")
            return reranked_docs
        except Exception as e:
            print(f"NVIDIA Rerank error: {str(e)}")
            # Fallback: return original documents up to top_n if rerank fails
            return documents[:self.reranker.top_n] # Use top_n configured in reranker

    def retrieve(self, query: str) -> List[LangchainDocument]:
        """
        Retrieve relevant documents for a query using vector search and reranking.
        This is where you would add Graph Traversal logic for Graph RAG.

        Args:
            query: User query.
            retrieve_k: Number of documents to retrieve initially via vector similarity.
            rerank_k: Number of documents to return after reranking (should match reranker's top_n).

        Returns:
            List of relevant Langchain Documents after reranking.
        """
        if not self.documents or not self.embeddings or len(self.documents) != len(self.embeddings):
             print("Warning: Documents or embeddings are not properly initialized for retrieval.")
             return []

        print(f"Retrieving documents for query: '{query[:50]}...'")
        # 1. Embed the query
        try:
            query_embedding = self.embedder.embed_query(query)
        except Exception as e:
            print(f"Failed to embed query: {e}")
            return []

        # 2. Calculate similarities (Simple Cosine Similarity - Replace with Vector DB for scale)
        # Note: This linear scan is inefficient for large datasets. Use a vector store (FAISS, Chroma, etc.) in production.
        similarities = []
        for i, doc_emb in enumerate(self.embeddings):
            if doc_emb: # Check if embedding exists
                 sim = self._cosine_similarity(query_embedding, doc_emb)
                 similarities.append((self.documents[i], sim))
            else:
                 print(f"Warning: Missing embedding for document index {i}.")


        # 3. Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # 4. Get top N candidates for reranking
        top_candidates = [doc for doc, _ in similarities[:self.retrieve_k]]
        print(f"Initial retrieval found {len(top_candidates)} candidates.")


        # *** Graph RAG Enhancement Point ***
        # Here you would:
        # a. Identify the nodes in your graph corresponding to `top_candidates`.
        # b. Perform graph traversal (e.g., find neighbors, paths) starting from these nodes.
        # c. Add relevant nodes found via traversal to the `top_candidates` list (or replace it).
        # d. Ensure you have LangchainDocument representations for these graph nodes.
        # Example conceptual steps:
        # graph_nodes = self.graph_db.find_related_nodes([doc.metadata.get('graph_id') for doc in top_candidates])
        # graph_docs = [self.convert_graph_node_to_document(node) for node in graph_nodes]
        # combined_candidates = top_candidates + graph_docs # Add logic for deduplication/ranking

        # 5. Rerank the candidates
        # Ensure rerank_k matches the NVIDIARerank top_n setting
        if self.reranker.top_n != self.rerank_k:
             print(f"Warning: rerank_k ({self.rerank_k}) differs from NVIDIARerank top_n ({self.reranker.top_n}). Using reranker's top_n.")
        # Pass the potentially expanded candidate list (if Graph RAG was added)
        reranked_docs = self._rerank(query, top_candidates) # Pass top_candidates or combined_candidates

        return reranked_docs

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Creates the Langchain ChatPromptTemplate."""
        # Define the system message
        system_template = """You are a helpful AI assistant for answering questions based on provided documentation context. Follow these rules strictly:
1. Use ONLY the information from the 'Context Documents' section to answer the 'Current Question'.
2. Analyze the 'Previous Conversation' for context, but base your answer *only* on the 'Context Documents'.
3. If the context documents contain the answer, synthesize it clearly.
4. If the context documents do NOT contain enough information to answer, state that clearly (e.g., "Based on the provided documents, I cannot answer this question."). Do NOT make up information.
5. If you quote or paraphrase, indicate the source document if possible (e.g., "According to Document 1...").
6. Be concise and directly answer the question.

Context Documents:
{context}"""

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{query}")
        ])
        return prompt

    def generate_response(self, query: str, chat_history: List[Dict[str, str]] = None) -> Tuple[str, List[str]]:
        """
        Generate a response using the RAG pipeline with NVIDIA LLM.

        Args:
            query: User query.
            chat_history: List of previous messages (dicts with 'role' and 'content').
                          Example: [{'role': 'user', 'content': 'Hi'}, {'role': 'assistant', 'content': 'Hello!'}]

        Returns:
            Tuple of (generated response string, list of source document identifiers).
        """
        print(f"Generating response for query: '{query[:50]}...'")
        chat_history = chat_history or []

        # 1. Retrieve relevant documents
        # Using retrieve_k=10, rerank_k=3 as an example
        relevant_docs = self.retrieve(query)

        # Extract source identifiers (customize based on your metadata)
        sources = [doc.metadata.get("source", f"doc_idx_{i}") for i, doc in enumerate(relevant_docs)] # Example: use 'source' key or index

        # 2. Format context for the prompt
        context_sections = []
        if relevant_docs:
            for i, doc in enumerate(relevant_docs, 1):
                source_id = doc.metadata.get("source", f"Document {i}") # Use metadata if available
                context_sections.append(f"[{source_id}]:\n{doc.page_content}")
            context_str = "\n\n".join(context_sections)
            print(f"Using {len(relevant_docs)} documents as context.")
        else:
            context_str = "No relevant documents found."
            print("No relevant documents found to provide context.")


        # 3. Format chat history for Langchain
        lc_chat_history: List[BaseMessage] = []
        for msg in chat_history:
            if msg.get("role") == "user":
                lc_chat_history.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant" or msg.get("role") == "chatbot": # Accept 'assistant' or 'chatbot'
                lc_chat_history.append(AIMessage(content=msg.get("content", "")))
            # Add handling for system messages if needed

        # 4. Create the prompt
        prompt_template = self._create_prompt_template()

        # 5. Create the generation chain
        chain = prompt_template | self.llm | StrOutputParser()

        # 6. Invoke the chain
        try:
            print("Invoking LLM chain...")
            response = chain.invoke({
                "context": context_str,
                "chat_history": lc_chat_history,
                "query": query
            })
            print("LLM response received.")
            return response, sources
        except Exception as e:
            print(f"NVIDIA LLM generation error: {str(e)}")
            # Provide a fallback error message
            return "Sorry, I encountered an error while generating the response.", []
