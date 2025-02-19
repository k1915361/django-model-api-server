import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ku_djangoo.settings')
import django
django.setup()

import asyncio
import json
from channels.db import database_sync_to_async, sync_to_async
from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer, 
    AsyncWebsocketConsumer
)
from collections.abc import Callable
from polls.models import DatasetActionSet, DatasetAction, Dataset, Task, DatasetTaskAction
from polls.api import identify_user_from_jwt_access_token, identify_user_from_jwt_access_token_and_refresh_token

HTTP_BASE_URL = "https://"
LOCALHOST = "localhost"
HOST_PORT = "8000"
API_BASE_URL = f"{HTTP_BASE_URL}{LOCALHOST}:{HOST_PORT}"
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

async def websocket_connect(self, base_url=STATIC_DATASET_BASE_URL, file_url='/CS_dataset/test/images/ppe_0000_jpg.rf.c102a9a7c8dec01565a8f95ff295974c.jpg', text_data=None):
    print(' - websocket connect ')
    
    await self.accept()

    await self.send_json({
        "step": 1, 
        **STATUS_STARTING_PROCESS_JSON 
    })
    await asyncio.sleep(0.5)

    await self.send_json({
        "step": 2,  
        **STATUS_PROCESSING_JSON
    })
    await asyncio.sleep(0.5)

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
    print( ' - websocket_disconnect ' )
    # await self.close()

async def websocket_receive(self, text_data):
    message = tryExceptJsonLoads(text_data)
    
    print(' - websocket receive . message: {message}')
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
    # await self.close() 
    pass

@database_sync_to_async
def get_dataset_action_sets_from_db():
    return list(DatasetActionSet.objects.all())

@database_sync_to_async
def get_dataset_action_type_from_db(**kwargs):
    return DatasetActionSet.objects.get(**kwargs)

@database_sync_to_async
def get_dataset_from_db(**kwargs):
    return Dataset.objects.get(**kwargs)

@database_sync_to_async
def create_task(**kwargs):
    return Task(**kwargs)

@database_sync_to_async
def get_task(**kwargs):
    return Task.objects.get(**kwargs)

@database_sync_to_async
def create_dataset_action(**kwargs):
    return DatasetAction(**kwargs)

@database_sync_to_async
def create_dataset_task_action(**kwargs):
    return DatasetTaskAction(**kwargs)

@database_sync_to_async
def create_dataset(**kwargs):
    return Dataset(**kwargs)

def tryExceptJsonLoads(text_data):
    try:
        message = json.loads(text_data)
        return message
    except json.JSONDecodeError:
        print("Invalid JSON data received")
    except Exception as e:
        print(f"Error processing message: {e}")    
    return None

async def progress_consumer_recieve(self, text_data, result_url=''):
    result_url = result_url or self.result_url    
    message = tryExceptJsonLoads(text_data)

    if message.get('type') == 'start_task':
        total_steps = message.get('payload', {}).get('total_steps', 10)
        await self.start_task(total_steps, result_url, text_data=text_data)
    else:
        total_steps = message.get('payload', {}).get('total_steps', 10)
        await self.start_task(total_steps, result_url, text_data=text_data)    

async def progress_consumer_send_progress(self, progress):
    await self.send(text_data=json.dumps(progress))

async def handle_save_dataset_action_task(text_data):
    print(f""" - handle_save_dataset_action_task: text_data: {text_data}: """)
    if not text_data:
        return None
    
    action_type = None
    dataset_id = None
    task_id = None
    parameters = None
    message = {}
    access_token = None
    try:
        message = json.loads(text_data)
    except json.JSONDecodeError:
        print("Invalid JSON data received")
        return None
    
    if not message:
        return None
    
    try:
        action_type = message.get("type")
        payload = message.get("payload", {})
        dataset_id = payload.get("id")
        task_id = payload.get("task_id")
        access_token = payload.get("access_token")
        parameters = payload.get("parameters")
        if not (payload and dataset_id and task_id and access_token and parameters):
            return None
        print(f""" - handle_save_dataset_action_task. 
              action_type:{action_type}. 
              dataset_id:{dataset_id}.
              task_id:{task_id}.
              parameters:{parameters}.
        """)
        if access_token:
            print(f"access_token: {access_token[:3]}...{access_token[-3:]} ")
        
    except KeyError as e:
        print(f"KeyError processing message: getting value by key from a dictionary: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")
    

    user = await sync_to_async(identify_user_from_jwt_access_token)(access_token)

    if not user:
        print('Invalid user JWT tokens. Cannot process action task.')
        
    if action_type and dataset_id and task_id and parameters and user:
        print('dataset id:', dataset_id,
            '. task id:', task_id,
        )
        try:
            datasetActionType = await get_dataset_action_type_from_db(action_type=action_type.lower())
            print(' - datasetAction id action_type: ',
                datasetActionType.id, datasetActionType.action_type)            
            dataset = await get_dataset_from_db(id=dataset_id)
            print(' - dataset: ', dataset)
            
            # TODO: user must be identified come from token from cookie. but web socket cannot contain cookies, and the cookie is only server-accessible: 
            # 1. Send a HTTP request from client and get JSON data of the token and setState for temporary store for security. Must check that this state will be removed when directing to other web page.
            # 2. Send a web socket message including this token 
            # 3. identify user from this token 
            
            dataset_directory = 'None'
            new_dataset = create_dataset(
                name = dataset.name, 
                user = user, 
                original_dataset = dataset, 
                dataset_directory = dataset_directory,
                is_public = dataset.is_public,
                description = dataset.description,                
            )
            # new_dataset.save()

            task = await get_task(id=task_id)
            datasetAction = await create_dataset_action(parameters=parameters, action=datasetActionType, dataset=dataset)
            print(' - datasetAction id parameters dataset: ')
            # datasetAction.save()
            print(datasetAction.parameters)
            dataset_task_action = await create_dataset_task_action(task=task, 
            action=datasetActionType)
            
            # Error: Cannot assign "<DatasetActionSet: DatasetActionSet object (5)>": "DatasetTaskAction.action" must be a "DatasetAction" instance.

            print(' - dataset_task_action: ')
            print(dataset_task_action.task )
            # dataset_task_action.save()

        except Exception as e: 
            print(f'Error: {e}')

async def progress_consumer_start_task(self, total_steps, result_url, 
task_function: Callable = None, text_data=None):
    """
    task_function: a task of action, returns URL of the result data/file/folder.
    """
    print(' - progress_consumer_start_task ')

    if text_data:
        await handle_save_dataset_action_task(text_data)    

    for i in range(total_steps):
        
        await asyncio.sleep(1) # Will be removed when actual task_function is implemented.
        print(f' - progress_consumer_start_task. i: {i}')
        try:
            if task_function:
                result_url, progress_percentage = task_function()

        except Exception as e:
            await self.send_progress({'current': i + 1, 'total': total_steps, 'finished': False, 'success': False})

        await self.send_progress({'current': i + 1, 'total': total_steps}) 

    await self.send_progress({'current': total_steps, 'total': total_steps, 'finished': True, 'result_url': result_url, 'success': True}) 

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