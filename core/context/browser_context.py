"""
Browser Context Integration System
Analyzes browser history to provide context for cognitive metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re
import logging

class BrowserContextAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.browser_history = pd.DataFrame()
        self.resource_patterns = {
            'documentation': r'docs?|documentation|reference|api|guide',
            'learning': r'learn|tutorial|course|example|how-to',
            'problem_solving': r'stackoverflow|github.com/issues|error|bug|fix',
            'research': r'paper|research|arxiv|ieee|acm'
        }
        
    async def load_history(self, history_data: List[Dict]):
        """Load browser history data"""
        try:
            self.browser_history = pd.DataFrame(history_data)
            self.browser_history['timestamp'] = pd.to_datetime(
                self.browser_history['timestamp']
            )
            self.browser_history['domain'] = self.browser_history['url'].apply(
                lambda x: urlparse(x).netloc
            )
            self._preprocess_history()
        except Exception as e:
            self.logger.error(f"Error loading browser history: {e}")
            raise
            
    def _preprocess_history(self):
        """Preprocess and categorize browser history"""
        self.browser_history['resource_type'] = self.browser_history['url'].apply(
            self._categorize_resource
        )
        self.browser_history['search_query'] = self.browser_history['url'].apply(
            self._extract_search_query
        )
        
    def analyze_context(self, 
                       timestamp: datetime,
                       window: timedelta = timedelta(minutes=5)) -> Dict:
        """Analyze browser context around a specific timestamp"""
        try:
            relevant_history = self._get_relevant_history(timestamp, window)
            
            if relevant_history.empty:
                return None
                
            return {
                'learning_sequence': self._analyze_learning_sequence(relevant_history),
                'research_pattern': self._analyze_research_pattern(relevant_history),
                'context_switches': self._analyze_context_switches(relevant_history),
                'knowledge_seeking': self._analyze_knowledge_seeking(relevant_history)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing context: {e}")
            return None
            
    def _get_relevant_history(self, 
                            timestamp: datetime,
                            window: timedelta) -> pd.DataFrame:
        """Get browser history within the specified time window"""
        return self.browser_history[
            (self.browser_history['timestamp'] >= timestamp - window) &
            (self.browser_history['timestamp'] <= timestamp + window)
        ]
        
    def _categorize_resource(self, url: str) -> str:
        """Categorize URL based on resource patterns"""
        url_lower = url.lower()
        
        for category, pattern in self.resource_patterns.items():
            if re.search(pattern, url_lower):
                return category
                
        return 'other'
        
    def _extract_search_query(self, url: str) -> Optional[str]:
        """Extract search query from URL if present"""
        parsed = urlparse(url)
        if 'google.com/search' in url:
            query_params = dict(param.split('=') for param in parsed.query.split('&'))
            return query_params.get('q')
        return None
        
    def _analyze_learning_sequence(self, history: pd.DataFrame) -> Dict:
        """Analyze learning sequence from browser history"""
        learning_resources = history[
            history['resource_type'].isin(['documentation', 'learning'])
        ]
        
        if learning_resources.empty:
            return None
            
        return {
            'sequence_length': len(learning_resources),
            'resource_progression': learning_resources['resource_type'].tolist(),
            'time_spent': self._calculate_time_spent(learning_resources),
            'depth_indicators': self._calculate_learning_depth(learning_resources)
        }
        
    def _analyze_research_pattern(self, history: pd.DataFrame) -> Dict:
        """Analyze research behavior patterns"""
        search_sequence = history[history['search_query'].notna()]
        
        if search_sequence.empty:
            return None
            
        return {
            'search_count': len(search_sequence),
            'query_progression': search_sequence['search_query'].tolist(),
            'topic_evolution': self._analyze_topic_evolution(search_sequence),
            'search_refinement': self._analyze_search_refinement(search_sequence)
        }
        
    def _analyze_context_switches(self, history: pd.DataFrame) -> Dict:
        """Analyze context switching patterns"""
        if len(history) < 2:
            return None
            
        switches = []
        prev_type = None
        
        for _, row in history.iterrows():
            if prev_type and row['resource_type'] != prev_type:
                switches.append({
                    'timestamp': row['timestamp'],
                    'from_type': prev_type,
                    'to_type': row['resource_type']
                })
            prev_type = row['resource_type']
            
        return {
            'switch_count': len(switches),
            'switch_patterns': switches,
            'avg_time_between_switches': self._calculate_avg_switch_time(switches)
        }
        
    def _analyze_knowledge_seeking(self, history: pd.DataFrame) -> Dict:
        """Analyze knowledge seeking behavior"""
        knowledge_resources = history[
            history['resource_type'].isin(['documentation', 'research'])
        ]
        
        if knowledge_resources.empty:
            return None
            
        return {
            'resource_count': len(knowledge_resources),
            'depth_distribution': knowledge_resources['resource_type'].value_counts().to_dict(),
            'knowledge_path': self._analyze_knowledge_path(knowledge_resources)
        }
        
    def _calculate_time_spent(self, history: pd.DataFrame) -> Dict:
        """Calculate time spent on different resource types"""
        if history.empty:
            return {}
            
        time_spent = {}
        for resource_type in history['resource_type'].unique():
            resources = history[history['resource_type'] == resource_type]
            time_spent[resource_type] = self._calculate_duration(resources)
            
        return time_spent
        
    def _calculate_duration(self, sequence: pd.DataFrame) -> timedelta:
        """Calculate duration of a sequence of events"""
        if len(sequence) < 2:
            return timedelta(0)
            
        return sequence['timestamp'].max() - sequence['timestamp'].min()
        
    def _analyze_topic_evolution(self, search_sequence: pd.DataFrame) -> List[Dict]:
        """Analyze how search topics evolve over time"""
        if search_sequence.empty:
            return []
            
        topics = []
        current_topic = None
        
        for _, row in search_sequence.iterrows():
            query = row['search_query']
            if query:
                topic = self._extract_main_topic(query)
                if topic != current_topic:
                    topics.append({
                        'timestamp': row['timestamp'],
                        'topic': topic,
                        'query': query
                    })
                current_topic = topic
                
        return topics
        
    def _extract_main_topic(self, query: str) -> str:
        """Extract main topic from search query"""
        # Simple implementation - could be enhanced with NLP
        words = query.lower().split()
        # Remove common words
        stop_words = {'how', 'to', 'what', 'is', 'are', 'the', 'in', 'on', 'at'}
        topic_words = [w for w in words if w not in stop_words]
        return ' '.join(topic_words[:2]) if topic_words else ''
        
    def get_context_summary(self, 
                          start_time: datetime,
                          end_time: datetime) -> Dict:
        """Get summary of browser context for a time period"""
        period_history = self.browser_history[
            (self.browser_history['timestamp'] >= start_time) &
            (self.browser_history['timestamp'] <= end_time)
        ]
        
        if period_history.empty:
            return None
            
        return {
            'resource_usage': self._calculate_time_spent(period_history),
            'learning_patterns': self._analyze_learning_sequence(period_history),
            'research_behavior': self._analyze_research_pattern(period_history),
            'context_switching': self._analyze_context_switches(period_history)
        }
