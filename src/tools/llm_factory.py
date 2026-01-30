"""
LLM factory for creating LangChain chat models.
Supports OpenAI, Anthropic, and Deepseek with fallback.
"""
import logging
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating LLM instances with fallback support."""
    
    @staticmethod
    def create_chat_model(
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        Create a chat model instance.
        
        Args:
            model_name: Model identifier (e.g., 'gpt-4-turbo-preview', 'claude-3-opus-20240229')
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            
        Returns:
            LangChain chat model instance
        """
        # Use environment variable if not specified
        if model_name is None:
            model_name = os.getenv('LLM_MODEL', 'gpt-4-turbo-preview')
        
        logger.info(f"Creating LLM: {model_name} (temp={temperature})")
        
        # OpenAI models
        if model_name.startswith('gpt-'):
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key
            )
        
        # Anthropic models
        elif model_name.startswith('claude-'):
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key
            )
        
        # Deepseek (OpenAI-compatible API)
        elif model_name.startswith('deepseek-'):
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not set in environment")
            
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )
        
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    @staticmethod
    def create_with_fallback(
        primary_model: str = 'gpt-4-turbo-preview',
        fallback_model: str = 'gpt-3.5-turbo',
        **kwargs
    ):
        """
        Create LLM with fallback.
        
        Args:
            primary_model: Primary model to try
            fallback_model: Fallback if primary fails
            **kwargs: Additional arguments for create_chat_model
            
        Returns:
            Chat model with fallback configured
        """
        try:
            return LLMFactory.create_chat_model(primary_model, **kwargs)
        except Exception as e:
            logger.warning(f"Failed to create {primary_model}, falling back to {fallback_model}: {e}")
            return LLMFactory.create_chat_model(fallback_model, **kwargs)
