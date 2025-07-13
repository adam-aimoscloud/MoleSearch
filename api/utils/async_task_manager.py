"""
Async task manager for handling background tasks
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from utils.redis_client import get_redis_client
from utils.logger import get_logger

logger = get_logger(__name__)


class AsyncTaskManager:
    """Manager for async tasks stored in Redis"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
        self.task_prefix = "async_task:"
        self.task_list_key = "async_task_list"
    
    def create_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """Create a new async task"""
        try:
            task_id = str(uuid.uuid4())
            task_info = {
                'task_id': task_id,
                'task_type': task_type,
                'status': 'pending',
                'progress': 0.0,
                'message': 'Task created',
                'created_at': datetime.now().isoformat(),
                'started_at': None,
                'completed_at': None,
                'result': None,
                'task_data': task_data
            }
            
            # Store task in Redis
            task_key = f"{self.task_prefix}{task_id}"
            self.redis_client._redis_client.setex(
                task_key,
                86400,  # 24 hours TTL
                json.dumps(task_info)
            )
            
            # Add to task list
            self.redis_client._redis_client.sadd(self.task_list_key, task_id)
            
            logger.info(f"Created async task: {task_id}, type: {task_type}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create async task: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status by task ID"""
        try:
            task_key = f"{self.task_prefix}{task_id}"
            task_data_str = self.redis_client._redis_client.get(task_key)
            
            if not task_data_str:
                return None
            
            return json.loads(task_data_str)
            
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            return None
    
    def update_task_status(self, task_id: str, status: str, progress: float = None, 
                          message: str = None, result: Dict[str, Any] = None) -> bool:
        """Update task status"""
        try:
            task_info = self.get_task_status(task_id)
            if not task_info:
                logger.error(f"Task not found: {task_id}")
                return False
            
            # Update fields
            if status:
                task_info['status'] = status
            if progress is not None:
                task_info['progress'] = progress
            if message:
                task_info['message'] = message
            if result:
                task_info['result'] = result
            
            # Update timestamps
            if status == 'processing' and not task_info.get('started_at'):
                task_info['started_at'] = datetime.now().isoformat()
            elif status in ['completed', 'failed'] and not task_info.get('completed_at'):
                task_info['completed_at'] = datetime.now().isoformat()
            
            # Store updated task
            task_key = f"{self.task_prefix}{task_id}"
            self.redis_client._redis_client.setex(
                task_key,
                86400,  # 24 hours TTL
                json.dumps(task_info)
            )
            
            logger.info(f"Updated task {task_id}: status={status}, progress={progress}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task status for {task_id}: {e}")
            return False
    
    def get_pending_tasks(self, task_type: str = None) -> List[Dict[str, Any]]:
        """Get all pending tasks"""
        try:
            task_ids = self.redis_client._redis_client.smembers(self.task_list_key)
            pending_tasks = []
            
            for task_id in task_ids:
                task_info = self.get_task_status(task_id)
                if task_info and task_info['status'] == 'pending':
                    if task_type is None or task_info['task_type'] == task_type:
                        pending_tasks.append(task_info)
            
            return pending_tasks
            
        except Exception as e:
            logger.error(f"Failed to get pending tasks: {e}")
            return []
    
    def get_all_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all tasks with optional limit"""
        try:
            task_ids = self.redis_client._redis_client.smembers(self.task_list_key)
            all_tasks = []
            
            for task_id in task_ids:
                task_info = self.get_task_status(task_id)
                if task_info:
                    all_tasks.append(task_info)
                
                # Apply limit
                if len(all_tasks) >= limit:
                    break
            
            # Sort by created_at (newest first)
            all_tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return all_tasks
            
        except Exception as e:
            logger.error(f"Failed to get all tasks: {e}")
            return []
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """Clean up completed tasks older than specified hours"""
        try:
            task_ids = self.redis_client._redis_client.smembers(self.task_list_key)
            cleaned_count = 0
            
            for task_id in task_ids:
                task_info = self.get_task_status(task_id)
                if task_info:
                    # Check if task is completed and old enough
                    if task_info['status'] in ['completed', 'failed']:
                        completed_at = datetime.fromisoformat(task_info['completed_at'])
                        age_hours = (datetime.now() - completed_at).total_seconds() / 3600
                        
                        if age_hours > max_age_hours:
                            # Remove task
                            task_key = f"{self.task_prefix}{task_id}"
                            self.redis_client._redis_client.delete(task_key)
                            self.redis_client._redis_client.srem(self.task_list_key, task_id)
                            cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} completed tasks")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup completed tasks: {e}")
            return 0
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        try:
            task_ids = self.redis_client._redis_client.smembers(self.task_list_key)
            stats = {
                'total_tasks': len(task_ids),
                'pending': 0,
                'processing': 0,
                'completed': 0,
                'failed': 0
            }
            
            for task_id in task_ids:
                task_info = self.get_task_status(task_id)
                if task_info:
                    status = task_info['status']
                    if status in stats:
                        stats[status] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get task statistics: {e}")
            return {}


# Global task manager instance
task_manager = AsyncTaskManager()


def get_task_manager() -> AsyncTaskManager:
    """Get task manager instance"""
    return task_manager 