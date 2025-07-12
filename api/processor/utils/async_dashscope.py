import asyncio
import dashscope
from typing import Any, Dict, List, Optional
from http import HTTPStatus


class AsyncDashScope:
    """Async DashScope API wrapper - use real async interface first"""
    
    @staticmethod
    async def text_embedding(
        model: str,
        input_text: str,
        api_key: str
    ) -> Dict[str, Any]:
        """Async text embedding - use thread pool to wrap sync interface"""
        def _sync_call():
            return dashscope.TextEmbedding.call(
                model=model,
                input=input_text,
                api_key=api_key,
            )
        
        rsp = await asyncio.to_thread(_sync_call)
        
        if rsp.status_code != HTTPStatus.OK:
            error_msg = getattr(rsp, 'message', str(rsp))
            raise Exception(f'Text embedding failed: {error_msg}')
        
        return rsp.output

    @staticmethod
    async def multimodal_embedding(
        model: str,
        input_data: List[Dict[str, Any]],
        api_key: str
    ) -> Dict[str, Any]:
        """Async multimodal embedding - use thread pool to wrap sync interface"""
        def _sync_call():
            return dashscope.MultiModalEmbedding.call(
                model=model,
                input=input_data,
                api_key=api_key,
            )
        
        rsp = await asyncio.to_thread(_sync_call)
        
        if rsp.status_code != HTTPStatus.OK:
            error_msg = getattr(rsp, 'message', str(rsp))
            raise Exception(f'Multimodal embedding failed: {error_msg}')
        
        return rsp.output

    @staticmethod
    async def multimodal_conversation(
        model: str,
        messages: List[Dict[str, Any]],
        api_key: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Async multimodal conversation - use thread pool to wrap sync interface"""
        def _sync_call():
            return dashscope.MultiModalConversation.call(
                api_key=api_key,
                model=model,
                messages=messages,
                stream=stream,
            )
        
        rsp = await asyncio.to_thread(_sync_call)
        
        if rsp.status_code != HTTPStatus.OK:
            error_msg = getattr(rsp, 'message', str(rsp))
            raise Exception(f'Multimodal conversation failed: {error_msg}')
        
        return rsp.output

    @staticmethod
    async def audio_recognition(
        model: str,
        audio_url: str,
        format: str = 'wav',
        sample_rate: int = 16000,
        language_hints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Async audio recognition - use thread pool to wrap sync interface"""
        from dashscope.audio.asr import Recognition
        
        def _sync_call():
            recognition = Recognition(
                model=model,
                format=format,
                sample_rate=sample_rate,
                language_hints=language_hints or ['zh', 'en'],
                callback=None
            )
            return recognition.call(audio_url)
        
        rsp = await asyncio.to_thread(_sync_call)
        
        if rsp.status_code != HTTPStatus.OK:
            error_msg = getattr(rsp, 'message', str(rsp))
            raise Exception(f'Audio recognition failed: {error_msg}')
        
        return rsp.output

    @staticmethod
    async def generation(
        model: str,
        prompt: str,
        api_key: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Async text generation - use real async interface"""
        rsp = await dashscope.AioGeneration.call(
            model=model,
            prompt=prompt,
            api_key=api_key,
            **kwargs
        )
        
        if rsp.status_code != HTTPStatus.OK:
            error_msg = getattr(rsp, 'message', str(rsp))
            raise Exception(f'Generation failed: {error_msg}')
        
        return rsp.output

    @staticmethod
    async def batch_text_embedding(
        model: str,
        input_texts: List[str],
        api_key: str
    ) -> Dict[str, Any]:
        """Async batch text embedding - use thread pool to wrap sync interface"""
        def _sync_call():
            return dashscope.BatchTextEmbedding.call(
                model=model,
                input=input_texts,
                api_key=api_key,
            )
        
        rsp = await asyncio.to_thread(_sync_call)
        
        if rsp.status_code != HTTPStatus.OK:
            error_msg = getattr(rsp, 'message', str(rsp))
            raise Exception(f'Batch text embedding failed: {error_msg}')
        
        return rsp.output 