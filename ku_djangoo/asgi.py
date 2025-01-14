"""
ASGI config for ku_djangoo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import asyncio
import json

from django.core.asgi import get_asgi_application
from django.http import StreamingHttpResponse, JsonResponse
import base64

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from ku_djangoo.consumers import (
    MultiStepWebSocketConsumer
    , AActionResponseWebSocketConsumer
    , BActionResponseWebSocketConsumer
    , CActionResponseWebSocketConsumer
    , DActionResponseWebSocketConsumer
    , EActionResponseWebSocketConsumer
    , ProgressConsumer
)
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ku_djangoo.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('api/dataset/image/test-async-file-stream-json/', MultiStepWebSocketConsumer.as_asgi()),
            path('api/dataset/image/test-async-file-stream-json/action-a', AActionResponseWebSocketConsumer.as_asgi()),
            path('api/dataset/image/test-async-file-stream-json/action-b', BActionResponseWebSocketConsumer.as_asgi()),
            path('api/dataset/image/test-async-file-stream-json/action-c', CActionResponseWebSocketConsumer.as_asgi()),
            path('api/dataset/image/test-async-file-stream-json/action-d', DActionResponseWebSocketConsumer.as_asgi()),
            path('api/dataset/image/test-async-file-stream-json/action-e', EActionResponseWebSocketConsumer.as_asgi()),
            path('api/dataset/image/test-async-file-stream-json/action-progress', ProgressConsumer.as_asgi()),
            
        ])
    ),
})

async def test_async_stream_view(request):
    async def event_stream():
        yield 'data: {"step": 1, "status": "Processing dataset"}\n\n'
        await asyncio.sleep(2)
       
        dataset_image_url = "static/dataset/CS_dataset/test/images/ppe_0000_jpg.rf.c102a9a7c8dec01565a8f95ff295974c.jpg"
        yield f'data: {{"step": 2, "status": "Dataset generated", "file_url": "{dataset_image_url}"}}\n\n'

        await asyncio.sleep(2)
        yield 'data: {"step": 3, "status": "Completed", "last_response": true }\n\n'

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response

async def test_async_file_streaming(request):
    async def file_stream():
        try:
            yield f'data: {{"step": 1, "status": "Preparing file data"}}\n\n'
            await asyncio.sleep(2)
            
            file_path = "static/dataset/CS_dataset/test/images/ppe_0000_jpg.rf.c102a9a7c8dec01565a8f95ff295974c.jpg"
            with open(file_path, 'rb') as f:
                file_data = f.read()
                base64_encoded_file = base64.b64encode(file_data).decode('utf-8') 

            yield f'data: {{"step": 2, "status": "Sending file data", "file_data": "{base64_encoded_file}"}}\n\n'
            await asyncio.sleep(2)
            
            yield f'data: {{"step": 3, "status": "File streaming complete!", "last_response": true}}\n\n'
        finally:
            return

    response = StreamingHttpResponse(file_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    return response

# Large file streaming - If processing the data stream as binary data, one chunk at a time: octet-stream

