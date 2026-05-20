import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        """
        Initializes the in-memory vector store with mock FAQs.
        In a real production environment, you would use an external vector database
        like Pinecone, Weaviate, or a persistent ChromaDB instance.
        """
        # Ensure your OPENAI_API_KEY is set in the environment variables
        api_key = os.getenv("OPENAI_API_KEY", "dummy-key")
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        
        # Mock Knowledge Base / FAQs for the Flash Sale
        self.mock_faqs = [
            Document(page_content="Warranty: All electronics purchased during the flash sale come with a 1-year limited warranty covering manufacturing defects."),
            Document(page_content="Exchange Policy: Due to extreme discounts, all flash sale items are final sale. We do not accept returns or exchanges unless the item arrives damaged."),
            Document(page_content="Payment Methods: We accept major Credit Cards (Visa, MasterCard, Amex), PayPal, and Apple Pay. We do not accept crypto or cash on delivery for flash sales."),
            Document(page_content="Shipping: Flash sale items typically ship within 3-5 business days due to high order volume. Express shipping is not available during the event."),
            Document(page_content="Cart Expiration: Items added to your cart are reserved for exactly 10 minutes. If checkout is not completed, they are returned to public inventory."),
            Document(page_content="Support: For urgent issues during checkout, please call our 24/7 flash sale hotline at 1-800-FLASHSALE.")
        ]
        
        self.vector_store = None
        self._initialize_store()

    def _initialize_store(self):
        try:
            # We initialize FAISS as a fast, in-memory semantic search engine
            self.vector_store = FAISS.from_documents(self.mock_faqs, self.embeddings)
            logger.info("RAG Engine successfully initialized with mock FAQs.")
        except Exception as e:
            logger.warning(f"Failed to initialize FAISS VectorStore (Did you set a valid OPENAI_API_KEY?): {e}")

    async def asearch(self, query: str, top_k: int = 2) -> str:
        """
        Asynchronously searches for the most relevant context based on user query.
        Returns the concatenated text of the top K results.
        """
        if not self.vector_store:
            return "No FAQ context available. Please contact support."
        
        try:
            # Perform async similarity search to avoid blocking the event loop
            docs = await self.vector_store.asimilarity_search(query, k=top_k)
            return "\n".join([doc.page_content for doc in docs])
        except Exception as e:
            logger.error(f"Error during async similarity search: {e}")
            return ""
            
# Singleton instance to be used across the application
rag_engine = RAGEngine()
