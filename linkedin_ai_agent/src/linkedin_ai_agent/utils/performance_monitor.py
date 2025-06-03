"""
Performance monitoring utility for tracking conversation response times
and optimizing the chatbot experience.
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class ConversationPerformanceMonitor:
    """
    Monitor conversation performance metrics to ensure real-time chatbot experience.
    """
    
    def __init__(self, target_response_time: float = 2.0):
        """
        Initialize the performance monitor.
        
        Args:
            target_response_time: Target response time in seconds (default: 2.0s)
        """
        self.target_response_time = target_response_time
        self.metrics: Dict[int, Dict] = {}  # User-specific metrics
        self.global_metrics = {
            'total_questions': 0,
            'total_responses': 0,
            'timeouts': 0,
            'avg_response_time': 0.0,
            'response_times': deque(maxlen=100)  # Keep last 100 response times
        }
    
    def start_question(self, user_id: int, question: str) -> None:
        """Record when a question is sent to user."""
        if user_id not in self.metrics:
            self.metrics[user_id] = {
                'questions': [],
                'response_times': [],
                'timeouts': 0,
                'current_question': None
            }
        
        self.metrics[user_id]['current_question'] = {
            'question': question,
            'start_time': time.time(),
            'timestamp': datetime.now()
        }
        self.global_metrics['total_questions'] += 1
        
        logger.info(f"Question started for user {user_id}: {question[:50]}...")
    
    def record_response(self, user_id: int, response: str) -> float:
        """
        Record when a response is received and calculate response time.
        
        Returns:
            Response time in seconds
        """
        if user_id not in self.metrics or not self.metrics[user_id].get('current_question'):
            logger.warning(f"No pending question for user {user_id}")
            return 0.0
        
        current_q = self.metrics[user_id]['current_question']
        response_time = time.time() - current_q['start_time']
        
        # Record metrics
        self.metrics[user_id]['questions'].append({
            'question': current_q['question'],
            'response': response,
            'response_time': response_time,
            'timestamp': current_q['timestamp']
        })
        self.metrics[user_id]['response_times'].append(response_time)
        self.metrics[user_id]['current_question'] = None
        
        # Update global metrics
        self.global_metrics['total_responses'] += 1
        self.global_metrics['response_times'].append(response_time)
        self._update_average_response_time()
        
        # Log performance
        if response_time > self.target_response_time:
            logger.warning(f"Slow response from user {user_id}: {response_time:.2f}s (target: {self.target_response_time}s)")
        else:
            logger.info(f"Good response time from user {user_id}: {response_time:.2f}s")
        
        return response_time
    
    def record_timeout(self, user_id: int) -> None:
        """Record when a question times out."""
        if user_id in self.metrics:
            self.metrics[user_id]['timeouts'] += 1
            self.metrics[user_id]['current_question'] = None
        
        self.global_metrics['timeouts'] += 1
        logger.warning(f"Question timeout for user {user_id}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get performance statistics for a specific user."""
        if user_id not in self.metrics:
            return {}
        
        user_data = self.metrics[user_id]
        response_times = user_data['response_times']
        
        if not response_times:
            return {
                'total_questions': 0,
                'avg_response_time': 0,
                'timeouts': user_data['timeouts']
            }
        
        return {
            'total_questions': len(user_data['questions']),
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'timeouts': user_data['timeouts'],
            'timeout_rate': user_data['timeouts'] / (len(user_data['questions']) + user_data['timeouts'])
        }
    
    def get_global_stats(self) -> Dict:
        """Get global performance statistics."""
        return {
            'total_questions': self.global_metrics['total_questions'],
            'total_responses': self.global_metrics['total_responses'],
            'total_timeouts': self.global_metrics['timeouts'],
            'avg_response_time': self.global_metrics['avg_response_time'],
            'response_rate': self.global_metrics['total_responses'] / self.global_metrics['total_questions'] 
                           if self.global_metrics['total_questions'] > 0 else 0
        }
    
    def _update_average_response_time(self) -> None:
        """Update the global average response time."""
        response_times = list(self.global_metrics['response_times'])
        if response_times:
            self.global_metrics['avg_response_time'] = sum(response_times) / len(response_times)
    
    def get_optimization_suggestions(self) -> List[str]:
        """Get suggestions for optimizing conversation flow based on metrics."""
        suggestions = []
        stats = self.get_global_stats()
        
        # Check average response time
        if stats['avg_response_time'] > self.target_response_time * 2:
            suggestions.append(f"⚠️ Average response time ({stats['avg_response_time']:.1f}s) is too high. Consider:")
            suggestions.append("  - Shortening questions to be more concise")
            suggestions.append("  - Reducing timeout to 15-20 seconds")
            suggestions.append("  - Pre-caching common responses")
        
        # Check timeout rate
        if stats['total_timeouts'] > stats['total_responses'] * 0.2:
            suggestions.append("⚠️ High timeout rate detected. Consider:")
            suggestions.append("  - Making questions clearer and easier to answer")
            suggestions.append("  - Adding quick response suggestions")
            suggestions.append("  - Implementing smart defaults for no response")
        
        # Check response rate
        if stats['response_rate'] < 0.8:
            suggestions.append("⚠️ Low response rate. Consider:")
            suggestions.append("  - Improving question engagement")
            suggestions.append("  - Adding context to questions")
            suggestions.append("  - Making the conversation more interactive")
        
        if not suggestions:
            suggestions.append("✅ Performance is optimal! Keep up the good work.")
        
        return suggestions
    
    def print_performance_report(self) -> None:
        """Print a formatted performance report."""
        print("\n" + "="*60)
        print("🚀 CONVERSATION PERFORMANCE REPORT")
        print("="*60)
        
        stats = self.get_global_stats()
        print(f"\n📊 Global Statistics:")
        print(f"  Total Questions: {stats['total_questions']}")
        print(f"  Total Responses: {stats['total_responses']}")
        print(f"  Total Timeouts: {stats['total_timeouts']}")
        print(f"  Average Response Time: {stats['avg_response_time']:.2f}s")
        print(f"  Response Rate: {stats['response_rate']:.1%}")
        
        print(f"\n💡 Optimization Suggestions:")
        for suggestion in self.get_optimization_suggestions():
            print(f"  {suggestion}")
        
        print("\n" + "="*60) 