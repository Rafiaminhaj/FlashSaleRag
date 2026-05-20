import os
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.ai.rag_engine import rag_engine

logger = logging.getLogger(__name__)

# System Prompt explicitly framing the AI's persona and constraints
PROMPT_TEMPLATE = """
You are a helpful, polite, and fast customer support AI for our Flash Sale event.
Use the following pieces of retrieved context to answer the user's question. 
If you don't know the answer based on the context, politely inform the user that you don't have that information.
Keep your answers concise, accurate, and directly related to the flash sale.

Context:
{context}

User Question: {question}
Answer:
"""

def build_rag_chain():
    """
    Builds the LangChain Expression Language (LCEL) chain.
    """
    api_key = os.getenv("OPENAI_API_KEY", "dummy-key")
    
    # Initialize the LLM with a low temperature for predictable, factual responses
    llm = ChatOpenAI(
        model="gpt-3.5-turbo", 
        api_key=api_key,
        temperature=0.2,
        max_tokens=150
    )
    
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
    # LCEL pipeline
    chain = prompt | llm | StrOutputParser()
    return chain

# Initialize the chain globally so it can be reused
rag_chain = build_rag_chain()

async def get_ai_response(user_query: str) -> str:
    """
    Asynchronously generates an AI response based on the user's query and our RAG context.
    
    Args:
        user_query (str): The question from the user.
        
    Returns:
        str: The AI-generated response.
    """
    try:
        # 1. Retrieve semantic context asynchronously
        context = await rag_engine.asearch(user_query, top_k=2)
        
        # 2. Invoke the LLM asynchronously to avoid blocking FastAPI
        response = await rag_chain.ainvoke({
            "context": context,
            "question": user_query
        })
        
        return response
    except Exception as e:
        logger.warning(f"Error generating AI response (fallback triggered): {e}")
        
        # Local mock fallback matching if OpenAI Authentication Error happens
        query_lower = user_query.lower()
        if "warranty" in query_lower:
            return "Warranty: All electronics purchased during the flash sale come with a 1-year limited warranty covering manufacturing defects."
        elif "return" in query_lower or "exchange" in query_lower:
            return "Exchange Policy: Due to extreme discounts, all flash sale items are final sale. We do not accept returns or exchanges unless the item arrives damaged."
        elif "cart" in query_lower or "expiration" in query_lower:
            return "Cart Expiration: Items added to your cart are reserved for exactly 10 minutes. If checkout is not completed, they are returned to public inventory."
        elif "shipping" in query_lower:
            return "Shipping: Flash sale items typically ship within 3-5 business days due to high order volume."
        elif "payment" in query_lower:
            return "Payment Methods: We accept major Credit Cards, PayPal, and Apple Pay."
            
        return "I apologize, but our AI assistant is currently unavailable. Please refer to our FAQ page."
