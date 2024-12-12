"""
Cognitive Metrics Validation System
Implements comprehensive validation approaches for cognitive metrics
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import FactorAnalysis
from sklearn.model_selection import cross_val_score
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

class MetricValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_history = []
        self.confidence_intervals = {}
        self.reliability_scores = {}
        
    def validate_cognitive_metrics(self, 
                                 metrics_data: pd.DataFrame,
                                 external_validations: Optional[Dict] = None) -> Dict:
        """Comprehensive validation of cognitive metrics"""
        try:
            # Statistical validation
            reliability = self._calculate_reliability(metrics_data)
            convergent = self._assess_convergent_validity(metrics_data)
            discriminant = self._assess_discriminant_validity(metrics_data)
            
            # Calculate confidence intervals
            confidence = self._calculate_confidence_intervals(metrics_data)
            
            # External validation if available
            external_validity = None
            if external_validations:
                external_validity = self._validate_against_external(
                    metrics_data, 
                    external_validations
                )
            
            validation_result = {
                'timestamp': datetime.now(),
                'reliability': {
                    'cronbach_alpha': reliability['cronbach_alpha'],
                    'test_retest': reliability['test_retest'],
                    'inter_rater': reliability['inter_rater']
                },
                'validity': {
                    'convergent': convergent,
                    'discriminant': discriminant,
                    'external': external_validity
                },
                'confidence_intervals': confidence,
                'sample_size': len(metrics_data),
                'validation_status': self._determine_validation_status(
                    reliability, convergent, discriminant
                )
            }
            
            self.validation_history.append(validation_result)
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error in metric validation: {e}")
            raise
            
    def _calculate_reliability(self, data: pd.DataFrame) -> Dict:
        """Calculate various reliability metrics"""
        try:
            # Cronbach's alpha for internal consistency
            alpha = self._calculate_cronbach_alpha(data)
            
            # Test-retest reliability
            test_retest = self._calculate_test_retest(data)
            
            # Inter-rater reliability if applicable
            inter_rater = self._calculate_inter_rater(data)
            
            return {
                'cronbach_alpha': alpha,
                'test_retest': test_retest,
                'inter_rater': inter_rater
            }
        except Exception as e:
            self.logger.error(f"Error calculating reliability: {e}")
            return None
            
    def _calculate_cronbach_alpha(self, data: pd.DataFrame) -> float:
        """Calculate Cronbach's alpha for internal consistency"""
        items = data.select_dtypes(include=[np.number])
        item_count = items.shape[1]
        
        if item_count < 2:
            return None
            
        item_vars = items.var(axis=0)
        total_var = items.sum(axis=1).var()
        
        return (item_count / (item_count - 1)) * (1 - item_vars.sum() / total_var)
        
    def _assess_convergent_validity(self, data: pd.DataFrame) -> Dict:
        """Assess convergent validity of metrics"""
        # Calculate correlation matrix
        corr_matrix = data.corr()
        
        # Identify highly correlated metrics (should be correlated if measuring similar constructs)
        convergent_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i,j]) > 0.7:  # Threshold for convergent validity
                    convergent_pairs.append({
                        'metrics': (corr_matrix.columns[i], corr_matrix.columns[j]),
                        'correlation': corr_matrix.iloc[i,j]
                    })
                    
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'convergent_pairs': convergent_pairs,
            'avg_correlation': np.mean([pair['correlation'] for pair in convergent_pairs])
        }
        
    def _assess_discriminant_validity(self, data: pd.DataFrame) -> Dict:
        """Assess discriminant validity using factor analysis"""
        # Perform factor analysis
        fa = FactorAnalysis(n_components=2, random_state=42)
        fa.fit(data.select_dtypes(include=[np.number]))
        
        # Calculate loadings
        loadings = pd.DataFrame(
            fa.components_.T,
            columns=['Factor1', 'Factor2'],
            index=data.select_dtypes(include=[np.number]).columns
        )
        
        # Identify discriminant factors
        discriminant_metrics = []
        for col in loadings.index:
            if abs(loadings.loc[col, 'Factor1']) > 0.7 and abs(loadings.loc[col, 'Factor2']) < 0.3:
                discriminant_metrics.append({
                    'metric': col,
                    'factor1_loading': loadings.loc[col, 'Factor1'],
                    'factor2_loading': loadings.loc[col, 'Factor2']
                })
                
        return {
            'factor_loadings': loadings.to_dict(),
            'discriminant_metrics': discriminant_metrics,
            'variance_explained': fa.explained_variance_ratio_.tolist()
        }
        
    def _calculate_confidence_intervals(self, data: pd.DataFrame) -> Dict:
        """Calculate confidence intervals for metrics"""
        confidence_intervals = {}
        
        for column in data.select_dtypes(include=[np.number]):
            mean = data[column].mean()
            std_err = stats.sem(data[column].dropna())
            ci = stats.t.interval(0.95, len(data[column])-1, mean, std_err)
            
            confidence_intervals[column] = {
                'mean': mean,
                'ci_lower': ci[0],
                'ci_upper': ci[1],
                'std_error': std_err
            }
            
        return confidence_intervals
        
    def _validate_against_external(self, 
                                 metrics_data: pd.DataFrame,
                                 external_data: Dict) -> Dict:
        """Validate against external measures (e.g., NASA-TLX)"""
        validations = {}
        
        if 'nasa_tlx' in external_data:
            validations['nasa_tlx'] = self._correlate_with_nasa_tlx(
                metrics_data, 
                external_data['nasa_tlx']
            )
            
        if 'eye_tracking' in external_data:
            validations['eye_tracking'] = self._validate_with_eye_tracking(
                metrics_data,
                external_data['eye_tracking']
            )
            
        if 'user_surveys' in external_data:
            validations['user_surveys'] = self._validate_with_surveys(
                metrics_data,
                external_data['user_surveys']
            )
            
        return validations
        
    def _determine_validation_status(self,
                                   reliability: Dict,
                                   convergent: Dict,
                                   discriminant: Dict) -> str:
        """Determine overall validation status"""
        # Check reliability thresholds
        reliability_check = (
            reliability['cronbach_alpha'] > 0.7 and
            reliability['test_retest'] > 0.7
        )
        
        # Check convergent validity
        convergent_check = convergent['avg_correlation'] > 0.7
        
        # Check discriminant validity
        discriminant_check = len(discriminant['discriminant_metrics']) > 0
        
        if all([reliability_check, convergent_check, discriminant_check]):
            return 'VALIDATED'
        elif any([reliability_check, convergent_check, discriminant_check]):
            return 'PARTIALLY_VALIDATED'
        else:
            return 'NOT_VALIDATED'
            
    def get_validation_summary(self) -> Dict:
        """Get summary of validation history"""
        if not self.validation_history:
            return None
            
        recent_validations = sorted(
            self.validation_history,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:5]
        
        return {
            'latest_validation': recent_validations[0],
            'validation_trend': [v['validation_status'] for v in recent_validations],
            'reliability_trend': [v['reliability']['cronbach_alpha'] for v in recent_validations],
            'sample_sizes': [v['sample_size'] for v in recent_validations]
        }
