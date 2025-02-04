import asyncio
import json
from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer, 
    AsyncWebsocketConsumer
)
from collections.abc import Callable


HTTP_BASE_URL = "http://"
LOCALHOST_IP = "127.0.0.1"
HOST_PORT = "8000"
API_BASE_URL = f"{HTTP_BASE_URL}{LOCALHOST_IP}:{HOST_PORT}"
STATIC_DIR = 'static'
STATIC_DATASET_BASE_URL = f'{API_BASE_URL}/static/dataset'
STATIC_IMAGE_BASE_URL = f'{API_BASE_URL}/static/image'
ROOT_DATASET_DIR = 'asset/user/dataset/'

STATUS_STARTING_PROCESS_JSON = {
    "status": "Starting process..."
}

STATUS_PROCESSING_JSON = {
    "status": "Processing..."
}

STATUS_PROCESS_COMPLETE_JSON = {
    "status": "Process complete."
}

def null_function():
    return

async def websocket_connect(self, base_url=STATIC_DATASET_BASE_URL, file_url='/CS_dataset/test/images/ppe_0000_jpg.rf.c102a9a7c8dec01565a8f95ff295974c.jpg'):
    await self.accept()

    await self.send_json({
        "step": 1, 
        **STATUS_STARTING_PROCESS_JSON 
    })
    await asyncio.sleep(2)

    await self.send_json({
        "step": 2,  
        **STATUS_PROCESSING_JSON
    })
    await asyncio.sleep(2)

    DEMO_IMG_URL = f"{base_url}{file_url}"
    await self.send_json({
        "step": 3, 
        "image_url": DEMO_IMG_URL,
        **STATUS_PROCESS_COMPLETE_JSON
    })

    await self.close()

async def websocket_send_json(self, body: dict, **kwargs):
    await self.send(
        json.dumps(
            body
        ),
        kwargs
    )

async def websocket_disconnect(self, close_code):
    pass

async def websocket_receive(self, text_data):
    pass

class MultiStepWebSocketConsumer(AsyncJsonWebsocketConsumer):
    send_json = websocket_send_json
    disconnect = websocket_disconnect
    receive = websocket_receive

    async def connect(self):
        await websocket_connect(self, file_url='/CS_dataset/test/images/ppe_0000_jpg.rf.c102a9a7c8dec01565a8f95ff295974c.jpg')

class AActionResponseWebSocketConsumer(AsyncJsonWebsocketConsumer):
    send_json = websocket_send_json

    async def connect(self):
        await websocket_connect(
            self
            , base_url=STATIC_IMAGE_BASE_URL
            , file_url='/2018-07-5-Suboptimal-bar-chart-variable-1024x590-e1541666684430.jpg'
        )

class BActionResponseWebSocketConsumer(AsyncJsonWebsocketConsumer):
    send_json = websocket_send_json
    
    async def connect(self):
        await websocket_connect(
            self
            , base_url=STATIC_IMAGE_BASE_URL
            , file_url='/2018-07-9-Pie-chart.png'
        )

class CActionResponseWebSocketConsumer(AsyncJsonWebsocketConsumer):
    send_json = websocket_send_json
    
    async def connect(self):
        await websocket_connect(
            self
            , base_url=STATIC_IMAGE_BASE_URL
            , file_url='/2018-07-12-Simple-line-chart.png'
        )

class DActionResponseWebSocketConsumer(AsyncJsonWebsocketConsumer):
    send_json = websocket_send_json
    
    async def connect(self):
        await websocket_connect(
            self
            , base_url=STATIC_IMAGE_BASE_URL
            , file_url='/2018-07-14-100-Area-chart.png'
        )

class EActionResponseWebSocketConsumer(AsyncJsonWebsocketConsumer):
    send_json = websocket_send_json
    
    async def connect(self):
        await websocket_connect(
            self
            , base_url=STATIC_IMAGE_BASE_URL
            , file_url='/2018-07-25-Scatter-plot-with-correlation-2.png'
        )

async def progress_consumer_connect(self):
    await self.accept()

async def progress_consumer_disconnect(self, close_code):
    pass

async def progress_consumer_recieve(self, text_data, result_url=''):
    result_url = result_url or self.result_url
    data_json = json.loads(text_data)
    if data_json.get('type') == 'start_task':
        total_steps = data_json.get('total_steps', 100)
        await self.start_task(total_steps, result_url)

async def progress_consumer_send_progress(self, progress):
    await self.send(text_data=json.dumps(progress))

async def progress_consumer_start_task(self, total_steps, result_url, task_function: Callable = null_function):
    for i in range(total_steps):
        await asyncio.sleep(1)
        try:
            result_url = task_function() or result_url
        except Exception as e:
            await self.send_progress({'current': i + 1, 'total': total_steps, 'finished': False, 'failed': True})

        await self.send_progress({'current': i + 1, 'total': total_steps}) 

    await self.send_progress({'current': total_steps, 'total': total_steps, 'finished': True, 'result_url': result_url}) 

class ProgressConsumer(AsyncWebsocketConsumer):
    result_url = f"{STATIC_DATASET_BASE_URL}/CS_dataset/test/labels/ppe_0000_jpg.rf.c102a9a7c8dec01565a8f95ff295974c.txt"
    send_progress = progress_consumer_send_progress
    start_task = progress_consumer_start_task
    receive = progress_consumer_recieve
    connect = progress_consumer_connect
    disconnect = progress_consumer_disconnect

class ProgressConsumerActionA(AsyncWebsocketConsumer):
    result_url = f"{STATIC_IMAGE_BASE_URL}/2018-07-5-Suboptimal-bar-chart-variable-1024x590-e1541666684430.jpg"
    receive = progress_consumer_recieve
    send_progress = progress_consumer_send_progress
    start_task = progress_consumer_start_task
    connect = progress_consumer_connect
    disconnect = progress_consumer_disconnect

class ProgressConsumerActionB(AsyncWebsocketConsumer):
    result_url = f"{STATIC_IMAGE_BASE_URL}/2018-07-9-Pie-chart.png"
    receive = progress_consumer_recieve
    send_progress = progress_consumer_send_progress
    start_task = progress_consumer_start_task
    connect = progress_consumer_connect
    disconnect = progress_consumer_disconnect

class ProgressConsumerActionC(AsyncWebsocketConsumer):
    result_url = f"{STATIC_IMAGE_BASE_URL}/2018-07-12-Simple-line-chart.png"
    receive = progress_consumer_recieve
    send_progress = progress_consumer_send_progress
    start_task = progress_consumer_start_task
    connect = progress_consumer_connect
    disconnect = progress_consumer_disconnect

class ProgressConsumerActionD(AsyncWebsocketConsumer):
    result_url = f"{STATIC_IMAGE_BASE_URL}/2018-07-14-100-Area-chart.png"
    receive = progress_consumer_recieve
    send_progress = progress_consumer_send_progress
    start_task = progress_consumer_start_task
    connect = progress_consumer_connect
    disconnect = progress_consumer_disconnect

class ProgressConsumerActionE(AsyncWebsocketConsumer):
    result_url = f"{STATIC_IMAGE_BASE_URL}/2018-07-25-Scatter-plot-with-correlation-2.png"
    receive = progress_consumer_recieve
    send_progress = progress_consumer_send_progress
    start_task = progress_consumer_start_task
    connect = progress_consumer_connect
    disconnect = progress_consumer_disconnect

class ProgressConsumerCsv(AsyncWebsocketConsumer):
    result_url = f"{ROOT_DATASET_DIR}1-20241107_192036-CS_dataset/.csv"
    receive = progress_consumer_recieve
    send_progress = progress_consumer_send_progress
    start_task = progress_consumer_start_task
    connect = progress_consumer_connect
    disconnect = progress_consumer_disconnect