import os
import logging
import pickle
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import openai
from openai import AuthenticationError, RateLimitError, OpenAIError
# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

class RAGChain:
    def __init__(self):
        """Initialize the RAG chain with OpenAI components"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Configure OpenAI components using the API key
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key,
            model="text-embedding-ada-002"
        )

        self.llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.1,
            max_tokens=1000
        )

        self.prompt_template = PromptTemplate(
            template="""Use the following pieces of context to answer the question at the end. 
If you don't know the answer based on the context provided, just say that you don't know, 
don't try to make up an answer.

Context:
{context}

Question: {question}

Answer: """,
            input_variables=["context", "question"]
        )

        logger.info("RAG Chain initialized successfully")

    async def create_vectorstore(self, text_chunks: List[str], vectorstore_path: str) -> bool:
        try:
            logger.info(f"Creating vector store with {len(text_chunks)} chunks")
            documents = [Document(page_content=chunk) for chunk in text_chunks]
            
            # Wrap OpenAI embedding call with error handling
            try:
                vectorstore = FAISS.from_documents(documents=documents, embedding=self.embeddings)
            except AuthenticationError as e:
                logger.error(f"OpenAI Authentication Error: {str(e)}")
                raise ValueError("OpenAI authentication failed. Please check your API key.")
            except RateLimitError as e:
                logger.error(f"OpenAI Rate Limit Error: {str(e)}")
                raise ValueError("OpenAI quota exceeded. Please try again later.")
            except OpenAIError as e:
                logger.error(f"OpenAI Error: {str(e)}")
                raise ValueError("OpenAI service error. Please try again later.")

            with open(vectorstore_path, 'wb') as f:
                pickle.dump(vectorstore, f)

            logger.info(f"Vector store created and saved to: {vectorstore_path}")
            return True

        except ValueError as e:
            # Re-raise ValueError (our custom OpenAI errors) as-is
            raise e
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            return False

    async def query(self, question: str, vectorstore_path: str) -> Dict[str, Any]:
        try:
            with open(vectorstore_path, 'rb') as f:
                vectorstore = pickle.load(f)

            logger.info(f"Loaded vector store from: {vectorstore_path}")

            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 4}
                ),
                chain_type_kwargs={"prompt": self.prompt_template},
                return_source_documents=True
            )

            # Wrap OpenAI LLM call with error handling
            try:
                result = qa_chain({"query": question})
            except AuthenticationError as e:
                logger.error(f"OpenAI Authentication Error: {str(e)}")
                raise ValueError("OpenAI authentication failed. Please check your API key.")
            except RateLimitError as e:
                logger.error(f"OpenAI Rate Limit Error: {str(e)}")
                raise ValueError("OpenAI quota exceeded. Please try again later.")
            except OpenAIError as e:
                logger.error(f"OpenAI Error: {str(e)}")
                raise ValueError("OpenAI service error. Please try again later.")

            sources = []
            for doc in result.get("source_documents", []):
                sources.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                })

            response = {
                "answer": result["result"],
                "sources": sources,
                "question": question
            }

            logger.info(f"Successfully generated answer for question: {question}")
            return response

        except Exception as e:
            logger.error(f"Error querying vector store: {str(e)}")
            raise e

    def test_connection(self) -> bool:
        try:
            self.embeddings.embed_query("test")
            self.llm.predict("Say 'Hello World'")
            logger.info("OpenAI API connection test successful")
            return True
        except Exception as e:
            logger.error(f"OpenAI API connection test failed: {str(e)}")
            return False

    async def get_similar_chunks(self, question: str, vectorstore_path: str, k: int = 4) -> List[Dict]:
        try:
            with open(vectorstore_path, 'rb') as f:
                vectorstore = pickle.load(f)

            similar_docs = vectorstore.similarity_search(question, k=k)

            chunks = []
            for doc in similar_docs:
                chunks.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": None
                })

            return chunks

        except Exception as e:
            logger.error(f"Error getting similar chunks: {str(e)}")
            return []
