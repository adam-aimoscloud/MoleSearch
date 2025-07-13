"""
Async worker for processing background tasks
"""

import asyncio
import time
from typing import Dict, Any
from utils.async_task_manager import get_task_manager
from handlers.search_service import SearchService
from utils.logger import get_logger

logger = get_logger(__name__)


class AsyncWorker:
    """Worker for processing async tasks"""
    
    def __init__(self):
        self.task_manager = get_task_manager()
        self.search_service = None
        self.running = False
    
    async def initialize(self):
        """Initialize the worker"""
        try:
            self.search_service = SearchService()
            await self.search_service.initialize()
            logger.info("Async worker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize async worker: {e}")
            raise
    
    async def process_task(self, task_info: Dict[str, Any]):
        """Process a single task"""
        task_id = task_info['task_id']
        task_type = task_info['task_type']
        task_data = task_info['task_data']
        
        try:
            logger.info(f"Processing task {task_id}, type: {task_type}")
            
            # Update task status to processing
            self.task_manager.update_task_status(
                task_id, 
                status='processing', 
                progress=0.0, 
                message='Processing task'
            )
            
            if task_type == 'insert_data':
                await self._process_insert_data(task_id, task_data)
            elif task_type == 'batch_insert_data':
                await self._process_batch_insert_data(task_id, task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Update task status to completed
            self.task_manager.update_task_status(
                task_id,
                status='completed',
                progress=100.0,
                message='Task completed successfully'
            )
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            
            # Update task status to failed
            self.task_manager.update_task_status(
                task_id,
                status='failed',
                message=f'Task failed: {str(e)}'
            )
    
    async def _process_insert_data(self, task_id: str, task_data: Dict[str, Any]):
        """Process single data insertion task"""
        try:
            # Extract data from task
            text = task_data.get('text')
            image_url = task_data.get('image_url')
            video_url = task_data.get('video_url')
            
            # Update progress
            self.task_manager.update_task_status(
                task_id,
                status='processing',
                progress=10.0,
                message='Starting data insertion'
            )
            
            # Perform data insertion
            await self.search_service.insert_data(
                text=text,
                image_url=image_url,
                video_url=video_url
            )
            
            # Update progress
            self.task_manager.update_task_status(
                task_id,
                status='processing',
                progress=50.0,
                message='Data insertion completed'
            )
            
            # Update result
            result = {
                'inserted_count': 1,
                'processing_time': time.time(),
                'data': {
                    'text': text,
                    'image_url': image_url,
                    'video_url': video_url
                }
            }
            
            self.task_manager.update_task_status(
                task_id,
                status='completed',
                progress=100.0,
                message='Task completed',
                result=result
            )
            
        except Exception as e:
            logger.error(f"Failed to process insert_data task {task_id}: {e}")
            raise
    
    async def _process_batch_insert_data(self, task_id: str, task_data: Dict[str, Any]):
        """Process batch data insertion task"""
        try:
            data_list = task_data.get('data_list', [])
            total_items = len(data_list)
            
            if total_items == 0:
                raise ValueError("No data items to insert")
            
            # Update progress
            self.task_manager.update_task_status(
                task_id,
                status='processing',
                progress=10.0,
                message=f'Starting batch insertion of {total_items} items'
            )
            
            # Process each item
            inserted_count = 0
            for i, data_item in enumerate(data_list):
                try:
                    await self.search_service.insert_data(
                        text=data_item.get('text'),
                        image_url=data_item.get('image_url'),
                        video_url=data_item.get('video_url')
                    )
                    inserted_count += 1
                    
                    # Update progress
                    progress = 10.0 + (i + 1) / total_items * 80.0
                    self.task_manager.update_task_status(
                        task_id,
                        status='processing',
                        progress=progress,
                        message=f'Processed {i + 1}/{total_items} items'
                    )
                    
                except Exception as e:
                    logger.warning(f"Failed to insert item {i} in batch task {task_id}: {e}")
                    # Continue with next item
            
            # Update result
            result = {
                'inserted_count': inserted_count,
                'total_items': total_items,
                'processing_time': time.time(),
                'success_rate': inserted_count / total_items if total_items > 0 else 0
            }
            
            self.task_manager.update_task_status(
                task_id,
                status='completed',
                progress=100.0,
                message=f'Batch insertion completed: {inserted_count}/{total_items} items inserted',
                result=result
            )
            
        except Exception as e:
            logger.error(f"Failed to process batch_insert_data task {task_id}: {e}")
            raise
    
    async def run(self, check_interval: int = 5):
        """Run the worker loop"""
        self.running = True
        logger.info("Async worker started")
        
        try:
            while self.running:
                try:
                    # Get pending tasks
                    pending_tasks = self.task_manager.get_pending_tasks()
                    
                    if pending_tasks:
                        logger.info(f"Found {len(pending_tasks)} pending tasks")
                        
                        # Process tasks concurrently
                        tasks = []
                        for task_info in pending_tasks:
                            task = asyncio.create_task(self.process_task(task_info))
                            tasks.append(task)
                        
                        # Wait for all tasks to complete
                        if tasks:
                            await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Wait before next check
                    await asyncio.sleep(check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in worker loop: {e}")
                    await asyncio.sleep(check_interval)
                    
        except KeyboardInterrupt:
            logger.info("Async worker stopped by user")
        except Exception as e:
            logger.error(f"Async worker stopped due to error: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the worker"""
        self.running = False
        logger.info("Async worker stop requested")


# Global worker instance
worker = AsyncWorker()


async def start_worker():
    """Start the async worker"""
    await worker.initialize()
    await worker.run()


def get_worker() -> AsyncWorker:
    """Get worker instance"""
    return worker 