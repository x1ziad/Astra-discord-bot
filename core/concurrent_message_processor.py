"""
🚀 CONCURRENT MESSAGE PROCESSOR - Ultra-High Performance
Handles multiple simultaneous conversations with millisecond response times

Designed for high-traffic scenarios:
- 10+ people chatting simultaneously
- Instant moderation warnings
- Natural AI conversations
- Question/answer responses
- Seamless multitasking

Features:
- Async task queues for parallel processing
- Priority-based message handling
- Intelligent rate limiting
- Memory-efficient conversation tracking
- Performance monitoring and optimization
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Set, Any, Callable, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import weakref
import discord
from discord.ext import commands


class MessagePriority(Enum):
    """Message processing priority levels"""
    CRITICAL = 1      # Security violations, emergencies
    HIGH = 2          # Direct mentions, questions
    NORMAL = 3        # Regular conversation
    LOW = 4           # Background analysis


class ProcessingResult(Enum):
    """Processing results for tracking"""
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    QUEUED = "queued"


@dataclass
class MessageTask:
    """Individual message processing task"""
    message: discord.Message
    priority: MessagePriority
    task_type: str
    timestamp: float = field(default_factory=time.time)
    retries: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        return self.priority.value < other.priority.value


@dataclass
class PerformanceMetrics:
    """Real-time performance tracking"""
    messages_processed: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_response_time: float = 0.0
    concurrent_tasks: int = 0
    queue_size: int = 0
    last_update: float = field(default_factory=time.time)


class ConcurrentMessageProcessor:
    """
    🚀 ULTRA-HIGH PERFORMANCE Concurrent Message Processor
    
    Handles multiple simultaneous conversations with:
    - Parallel task execution (up to 50 concurrent tasks)
    - Priority-based processing queues
    - Intelligent rate limiting per user
    - Memory-efficient conversation tracking
    - Real-time performance monitoring
    """
    
    def __init__(self, bot: commands.Bot, max_concurrent_tasks: int = 50):
        self.bot = bot
        self.logger = logging.getLogger("astra.concurrent_processor")
        
        # Performance Configuration
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_timeout = 30.0  # 30 seconds max per task
        self.queue_size_limit = 1000
        
        # Task Management
        self.task_queue = asyncio.PriorityQueue(maxsize=self.queue_size_limit)
        self.active_tasks: Set[asyncio.Task] = set()
        self.processing_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # Performance Tracking
        self.metrics = PerformanceMetrics()
        self.response_times = deque(maxlen=100)  # Track last 100 response times
        
        # User Rate Limiting
        self.user_message_times: Dict[int, deque] = defaultdict(lambda: deque(maxlen=10))
        self.rate_limit_window = 10.0  # 10 seconds
        self.max_messages_per_window = 5
        
        # Task Handlers Registry
        self.task_handlers: Dict[str, Callable] = {}
        self.cog_references: Dict[str, weakref.ref] = {}
        
        # Processing Statistics
        self.task_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            'processed': 0, 'success': 0, 'error': 0, 'avg_time': 0.0
        })
        
        # Start the processing worker
        self.processor_task = None
        self.running = False
        
        self.logger.info("🚀 Concurrent Message Processor initialized")
    
    async def start(self):
        """Start the concurrent processing system"""
        if self.running:
            return
            
        self.running = True
        self.processor_task = asyncio.create_task(self._process_queue())
        self.logger.info("⚡ Concurrent Message Processor STARTED")
    
    async def stop(self):
        """Stop the concurrent processing system"""
        self.running = False
        
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all active tasks
        for task in self.active_tasks.copy():
            task.cancel()
        
        # Wait for tasks to complete
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
        
        self.logger.info("🛑 Concurrent Message Processor STOPPED")
    
    def register_handler(self, task_type: str, handler: Callable, cog_name: str = None):
        """Register a task handler function"""
        self.task_handlers[task_type] = handler
        if cog_name:
            # Store weak reference to avoid circular references
            cog = getattr(self.bot, 'get_cog')(cog_name)
            if cog:
                self.cog_references[task_type] = weakref.ref(cog)
        
        self.logger.info(f"📝 Registered handler: {task_type}")
    
    async def process_message(self, message: discord.Message) -> bool:
        """
        🚀 ENTRY POINT: Process a message with intelligent task distribution
        
        Returns: True if message was queued for processing, False if rate limited
        """
        if message.author.bot:
            return False
        
        # Rate limiting check
        if not self._check_rate_limit(message.author.id):
            self.logger.debug(f"Rate limited user {message.author.id}")
            return False
        
        # Determine message priority and tasks
        tasks = await self._analyze_message_tasks(message)
        
        # Queue all tasks
        queued_count = 0
        for task in tasks:
            try:
                self.task_queue.put_nowait(task)
                queued_count += 1
                self.metrics.queue_size += 1
            except asyncio.QueueFull:
                self.logger.warning(f"Task queue full, dropping {task.task_type} task")
                break
        
        if queued_count > 0:
            self.metrics.messages_processed += 1
            self.logger.debug(f"Queued {queued_count} tasks for message from {message.author}")
        
        return queued_count > 0
    
    async def _analyze_message_tasks(self, message: discord.Message) -> List[MessageTask]:
        """🧠 Intelligent task analysis and priority assignment"""
        tasks = []
        content = message.content.lower().strip()
        
        # CRITICAL: Security violations (highest priority)
        if self._detect_potential_violation(content):
            tasks.append(MessageTask(
                message=message,
                priority=MessagePriority.CRITICAL,
                task_type="security_check"
            ))
        
        # HIGH: Direct mentions or questions
        if message.mentions or '?' in content or 'astra' in content:
            tasks.append(MessageTask(
                message=message,
                priority=MessagePriority.HIGH,
                task_type="ai_response"
            ))
        
        # HIGH: Urgent keywords
        urgent_keywords = ['help', 'urgent', 'emergency', 'issue', 'problem', 'error']
        if any(keyword in content for keyword in urgent_keywords):
            tasks.append(MessageTask(
                message=message,
                priority=MessagePriority.HIGH,
                task_type="support_response"
            ))
        
        # NORMAL: Regular conversation
        if len(content) > 10 and not any(task.task_type == "ai_response" for task in tasks):
            tasks.append(MessageTask(
                message=message,
                priority=MessagePriority.NORMAL,
                task_type="conversation"
            ))
        
        # LOW: Analytics and background processing
        tasks.append(MessageTask(
            message=message,
            priority=MessagePriority.LOW,
            task_type="analytics"
        ))
        
        return tasks
    
    def _detect_potential_violation(self, content: str) -> bool:
        """Quick preliminary violation detection"""
        # Basic bad word detection (extend as needed)
        violation_indicators = [
            'fuck', 'shit', 'damn', 'hell', 'bitch', 'asshole',
            'spam', 'advertise', 'discord.gg/', 'http://', 'https://'
        ]
        return any(indicator in content for indicator in violation_indicators)
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        current_time = time.time()
        user_times = self.user_message_times[user_id]
        
        # Remove old timestamps
        while user_times and current_time - user_times[0] > self.rate_limit_window:
            user_times.popleft()
        
        # Check if under limit
        if len(user_times) >= self.max_messages_per_window:
            return False
        
        # Add current timestamp
        user_times.append(current_time)
        return True
    
    async def _process_queue(self):
        """🔄 Main processing loop - handles tasks concurrently"""
        self.logger.info("🔄 Processing queue started")
        
        while self.running:
            try:
                # Get next task (blocks if queue is empty)
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                    self.metrics.queue_size -= 1
                except asyncio.TimeoutError:
                    continue
                
                # Clean up completed tasks
                self._cleanup_completed_tasks()
                
                # Process task if we have capacity
                if len(self.active_tasks) < self.max_concurrent_tasks:
                    processor_task = asyncio.create_task(
                        self._execute_task(task)
                    )
                    self.active_tasks.add(processor_task)
                else:
                    # Requeue task if at capacity
                    await self.task_queue.put(task)
                    self.metrics.queue_size += 1
                    await asyncio.sleep(0.1)  # Brief pause
                
                # Update metrics
                await self._update_performance_metrics()
                
            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(1.0)
    
    async def _execute_task(self, task: MessageTask):
        """🎯 Execute individual task with performance tracking"""
        start_time = time.time()
        
        try:
            async with self.processing_semaphore:
                self.metrics.concurrent_tasks += 1
                
                # Get handler for task type
                handler = self.task_handlers.get(task.task_type)
                if not handler:
                    self.logger.warning(f"No handler for task type: {task.task_type}")
                    return ProcessingResult.SKIPPED
                
                # Execute with timeout
                try:
                    await asyncio.wait_for(
                        handler(task.message), 
                        timeout=self.task_timeout
                    )
                    result = ProcessingResult.SUCCESS
                    
                except asyncio.TimeoutError:
                    self.logger.warning(f"Task timeout: {task.task_type}")
                    result = ProcessingResult.ERROR
                    
                except Exception as e:
                    self.logger.error(f"Task execution error: {task.task_type} - {e}")
                    result = ProcessingResult.ERROR
                
                # Update statistics
                execution_time = time.time() - start_time
                self._update_task_stats(task.task_type, result, execution_time)
                
                return result
        
        finally:
            self.metrics.concurrent_tasks -= 1
            self.metrics.tasks_completed += 1
            
            # Track response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
    
    def _cleanup_completed_tasks(self):
        """Clean up completed async tasks"""
        completed = {task for task in self.active_tasks if task.done()}
        self.active_tasks -= completed
    
    def _update_task_stats(self, task_type: str, result: ProcessingResult, execution_time: float):
        """Update task statistics"""
        stats = self.task_stats[task_type]
        stats['processed'] += 1
        
        if result == ProcessingResult.SUCCESS:
            stats['success'] += 1
        elif result == ProcessingResult.ERROR:
            stats['error'] += 1
        
        # Update average execution time
        if stats['processed'] > 1:
            stats['avg_time'] = (stats['avg_time'] + execution_time) / 2
        else:
            stats['avg_time'] = execution_time
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        current_time = time.time()
        
        # Update average response time
        if self.response_times:
            self.metrics.average_response_time = sum(self.response_times) / len(self.response_times)
        
        self.metrics.last_update = current_time
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            "metrics": {
                "messages_processed": self.metrics.messages_processed,
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "average_response_time": f"{self.metrics.average_response_time:.3f}s",
                "concurrent_tasks": self.metrics.concurrent_tasks,
                "queue_size": self.metrics.queue_size,
                "active_tasks": len(self.active_tasks),
            },
            "task_stats": dict(self.task_stats),
            "system": {
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "queue_size_limit": self.queue_size_limit,
                "rate_limit_window": self.rate_limit_window,
                "running": self.running,
            }
        }
    
    async def get_status_embed(self) -> discord.Embed:
        """Generate performance status embed"""
        stats = self.get_performance_stats()
        
        embed = discord.Embed(
            title="🚀 Concurrent Message Processor Status",
            color=0x00ff00 if self.running else 0xff0000,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Performance metrics
        metrics = stats["metrics"]
        embed.add_field(
            name="📊 Performance",
            value=f"""
            **Messages Processed:** {metrics['messages_processed']:,}
            **Tasks Completed:** {metrics['tasks_completed']:,}
            **Avg Response Time:** {metrics['average_response_time']}
            **Queue Size:** {metrics['queue_size']}/{self.queue_size_limit}
            **Active Tasks:** {metrics['active_tasks']}/{self.max_concurrent_tasks}
            """,
            inline=True
        )
        
        # Task statistics
        task_info = []
        for task_type, stats in self.task_stats.items():
            if stats['processed'] > 0:
                success_rate = (stats['success'] / stats['processed']) * 100
                task_info.append(f"**{task_type}:** {stats['processed']} ({success_rate:.1f}% success)")
        
        if task_info:
            embed.add_field(
                name="🎯 Task Statistics",
                value="\n".join(task_info[:5]),  # Show top 5
                inline=True
            )
        
        # System status
        status_icon = "🟢" if self.running else "🔴"
        embed.add_field(
            name=f"{status_icon} System Status",
            value=f"**Running:** {self.running}\n**Max Concurrent:** {self.max_concurrent_tasks}",
            inline=True
        )
        
        return embed


# Global instance (will be initialized by the bot)
message_processor: Optional[ConcurrentMessageProcessor] = None


async def initialize_processor(bot: commands.Bot) -> ConcurrentMessageProcessor:
    """Initialize the global message processor"""
    global message_processor
    
    if message_processor is None:
        message_processor = ConcurrentMessageProcessor(bot, max_concurrent_tasks=50)
        await message_processor.start()
    
    return message_processor


async def shutdown_processor():
    """Shutdown the global message processor"""
    global message_processor
    
    if message_processor:
        await message_processor.stop()
        message_processor = None