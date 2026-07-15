#!/usr/bin/env python3
"""
Enhanced XAI Performance Metrics Module
Calculates comprehensive performance metrics for the cybercrime detection model
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_curve, roc_curve, auc, cohen_kappa_score,
    matthews_corrcoef, balanced_accuracy_score
)
from sklearn.model_selection import cross_val_score, StratifiedKFold
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from collections import Counter

class XAIPerformanceAnalyzer:
    """Comprehensive performance analysis for XAI cybercrime model"""
    
    def __init__(self, model, vectorizer, label_encoder):
        self.model = model
        self.vectorizer = vectorizer
        self.label_encoder = label_encoder
        self.performance_data = {}
        
    def calculate_comprehensive_metrics(self, X_test, y_test, X_train=None, y_train=None):
        """Calculate all performance metrics"""
        
        # Basic predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        # Class names
        class_names = self.label_encoder.classes_
        
        # Basic metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
        precision_micro = precision_score(y_test, y_pred, average='micro', zero_division=0)
        precision_weighted = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        
        recall_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
        recall_micro = recall_score(y_test, y_pred, average='micro', zero_division=0)
        recall_weighted = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
        f1_micro = f1_score(y_test, y_pred, average='micro', zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Advanced metrics
        balanced_acc = balanced_accuracy_score(y_test, y_pred)
        kappa = cohen_kappa_score(y_test, y_pred)
        mcc = matthews_corrcoef(y_test, y_pred)
        
        # Per-class metrics
        class_report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Cross-validation scores (if training data provided)
        cv_scores = None
        if X_train is not None and y_train is not None:
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = {
                'accuracy': cross_val_score(self.model, X_train, y_train, cv=cv, scoring='accuracy'),
                'precision': cross_val_score(self.model, X_train, y_train, cv=cv, scoring='precision_macro'),
                'recall': cross_val_score(self.model, X_train, y_train, cv=cv, scoring='recall_macro'),
                'f1': cross_val_score(self.model, X_train, y_train, cv=cv, scoring='f1_macro')
            }
        
        # Class distribution
        class_distribution = Counter(y_test)
        class_dist_normalized = {class_names[k]: v/len(y_test) for k, v in class_distribution.items()}
        
        # ROC AUC (for multiclass)
        try:
            auc_macro = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='macro')
            auc_weighted = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
        except:
            auc_macro = auc_weighted = None
        
        # Compile all metrics
        self.performance_data = {
            'timestamp': datetime.now().isoformat(),
            'basic_metrics': {
                'accuracy': float(accuracy),
                'balanced_accuracy': float(balanced_acc),
                'precision': {
                    'macro': float(precision_macro),
                    'micro': float(precision_micro),
                    'weighted': float(precision_weighted)
                },
                'recall': {
                    'macro': float(recall_macro),
                    'micro': float(recall_micro),
                    'weighted': float(recall_weighted)
                },
                'f1_score': {
                    'macro': float(f1_macro),
                    'micro': float(f1_micro),
                    'weighted': float(f1_weighted)
                }
            },
            'advanced_metrics': {
                'cohen_kappa': float(kappa),
                'matthews_correlation': float(mcc),
                'roc_auc': {
                    'macro': float(auc_macro) if auc_macro else None,
                    'weighted': float(auc_weighted) if auc_weighted else None
                }
            },
            'class_metrics': self._format_class_metrics(class_report, class_names),
            'confusion_matrix': {
                'matrix': cm.tolist(),
                'labels': class_names.tolist(),
                'normalized': (cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]).tolist()
            },
            'dataset_info': {
                'test_samples': len(y_test),
                'train_samples': len(y_train) if y_train is not None else None,
                'classes': len(class_names),
                'class_names': class_names.tolist(),
                'class_distribution': class_dist_normalized
            },
            'cross_validation': self._format_cv_scores(cv_scores) if cv_scores else None,
            'model_info': {
                'model_type': type(self.model).__name__,
                'features_count': X_test.shape[1],
                'has_feature_importance': hasattr(self.model, 'feature_importances_')
            }
        }
        
        return self.performance_data
    
    def _format_class_metrics(self, class_report, class_names):
        """Format per-class metrics"""
        class_metrics = {}
        for class_name in class_names:
            if class_name in class_report:
                metrics = class_report[class_name]
                class_metrics[class_name] = {
                    'precision': float(metrics.get('precision', 0)),
                    'recall': float(metrics.get('recall', 0)),
                    'f1_score': float(metrics.get('f1-score', 0)),
                    'support': int(metrics.get('support', 0))
                }
        return class_metrics
    
    def _format_cv_scores(self, cv_scores):
        """Format cross-validation scores"""
        if not cv_scores:
            return None
        
        formatted_cv = {}
        for metric, scores in cv_scores.items():
            formatted_cv[metric] = {
                'mean': float(np.mean(scores)),
                'std': float(np.std(scores)),
                'scores': scores.tolist(),
                'confidence_interval': [
                    float(np.mean(scores) - 2*np.std(scores)),
                    float(np.mean(scores) + 2*np.std(scores))
                ]
            }
        return formatted_cv
    
    def generate_performance_summary(self):
        """Generate a human-readable performance summary"""
        if not self.performance_data:
            return "No performance data available. Run calculate_comprehensive_metrics first."
        
        data = self.performance_data
        basic = data['basic_metrics']
        advanced = data['advanced_metrics']
        
        summary = {
            'overall_performance': self._get_performance_grade(basic['accuracy']),
            'key_strengths': [],
            'areas_for_improvement': [],
            'recommendations': []
        }
        
        # Analyze performance
        if basic['accuracy'] >= 0.9:
            summary['key_strengths'].append("Excellent overall accuracy")
        elif basic['accuracy'] >= 0.8:
            summary['key_strengths'].append("Good overall accuracy")
        else:
            summary['areas_for_improvement'].append("Overall accuracy could be improved")
        
        # Check balanced performance
        if basic['balanced_accuracy'] >= 0.85:
            summary['key_strengths'].append("Well-balanced performance across classes")
        else:
            summary['areas_for_improvement'].append("Performance imbalanced across classes")
        
        # Check precision-recall balance
        precision_avg = basic['precision']['weighted']
        recall_avg = basic['recall']['weighted']
        if abs(precision_avg - recall_avg) < 0.05:
            summary['key_strengths'].append("Good precision-recall balance")
        elif precision_avg > recall_avg + 0.05:
            summary['areas_for_improvement'].append("Model is conservative (high precision, lower recall)")
        else:
            summary['areas_for_improvement'].append("Model is aggressive (high recall, lower precision)")
        
        # Generate recommendations
        if basic['accuracy'] < 0.9:
            summary['recommendations'].append("Consider ensemble methods or hyperparameter tuning")
        
        if advanced['cohen_kappa'] < 0.7:
            summary['recommendations'].append("Improve inter-class distinction with feature engineering")
        
        if len(summary['areas_for_improvement']) > len(summary['key_strengths']):
            summary['recommendations'].append("Review dataset quality and balance")
        
        return summary
    
    def _get_performance_grade(self, accuracy):
        """Get performance grade based on accuracy"""
        if accuracy >= 0.95:
            return "Excellent (A+)"
        elif accuracy >= 0.9:
            return "Very Good (A)"
        elif accuracy >= 0.8:
            return "Good (B)"
        elif accuracy >= 0.7:
            return "Fair (C)"
        else:
            return "Needs Improvement (D)"
    
    def get_threat_detection_stats(self):
        """Get statistics specific to threat detection"""
        if not self.performance_data:
            return None
        
        class_metrics = self.performance_data['class_metrics']
        
        # Separate safe vs threat categories
        safe_metrics = class_metrics.get('safe', {})
        threat_categories = {k: v for k, v in class_metrics.items() if k != 'safe'}
        
        # Calculate threat detection performance
        threat_detection_stats = {
            'safe_classification': {
                'precision': safe_metrics.get('precision', 0),
                'recall': safe_metrics.get('recall', 0),
                'f1_score': safe_metrics.get('f1_score', 0)
            },
            'threat_categories': threat_categories,
            'overall_threat_detection': {
                'avg_precision': np.mean([m.get('precision', 0) for m in threat_categories.values()]),
                'avg_recall': np.mean([m.get('recall', 0) for m in threat_categories.values()]),
                'avg_f1': np.mean([m.get('f1_score', 0) for m in threat_categories.values()])
            },
            'false_positive_rate': 1 - safe_metrics.get('precision', 0),
            'false_negative_rate': 1 - safe_metrics.get('recall', 0)
        }
        
        return threat_detection_stats
    
    def export_performance_report(self, filepath=None):
        """Export comprehensive performance report"""
        if not filepath:
            filepath = f"xai_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        full_report = {
            'performance_metrics': self.performance_data,
            'performance_summary': self.generate_performance_summary(),
            'threat_detection_stats': self.get_threat_detection_stats()
        }
        
        with open(filepath, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        return filepath

def load_and_analyze_model():
    """Load the XAI model and analyze its performance"""
    try:
        from xai_cybercrime_model import CybercrimeXAIModel
        import pandas as pd
        
        # Load model
        model = CybercrimeXAIModel()
        if not model.load_model():
            return None
        
        # Load dataset for evaluation
        try:
            df = pd.read_csv('cybercrime_dataset.csv')
        except FileNotFoundError:
            print("Dataset not found. Cannot calculate performance metrics.")
            return None
        
        # Prepare data
        X_vectorized, y_category, y_binary, X_text = model.prepare_data(df)
        
        # Split for evaluation (use same split as training)
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X_vectorized, y_category, test_size=0.2, random_state=42, stratify=y_category
        )
        
        # Create analyzer and calculate metrics
        analyzer = XAIPerformanceAnalyzer(model.model, model.vectorizer, model.label_encoder)
        performance_data = analyzer.calculate_comprehensive_metrics(
            X_test, y_test, X_train, y_train
        )
        
        return analyzer, performance_data
        
    except Exception as e:
        print(f"Error analyzing model performance: {e}")
        return None

if __name__ == "__main__":
    print("Analyzing XAI Model Performance...")
    result = load_and_analyze_model()
    
    if result:
        analyzer, performance_data = result
        
        print("\n" + "="*80)
        print("XAI CYBERCRIME DETECTION MODEL - PERFORMANCE ANALYSIS")
        print("="*80)
        
        basic = performance_data['basic_metrics']
        print(f"\n📊 BASIC METRICS:")
        print(f"   • Accuracy: {basic['accuracy']:.3f}")
        print(f"   • Balanced Accuracy: {basic['balanced_accuracy']:.3f}")
        print(f"   • Precision (Weighted): {basic['precision']['weighted']:.3f}")
        print(f"   • Recall (Weighted): {basic['recall']['weighted']:.3f}")
        print(f"   • F1-Score (Weighted): {basic['f1_score']['weighted']:.3f}")
        
        advanced = performance_data['advanced_metrics']
        print(f"\n🔬 ADVANCED METRICS:")
        print(f"   • Cohen's Kappa: {advanced['cohen_kappa']:.3f}")
        print(f"   • Matthews Correlation: {advanced['matthews_correlation']:.3f}")
        if advanced['roc_auc']['macro']:
            print(f"   • ROC AUC (Macro): {advanced['roc_auc']['macro']:.3f}")
        
        # Performance summary
        summary = analyzer.generate_performance_summary()
        print(f"\n🏆 PERFORMANCE GRADE: {summary['overall_performance']}")
        
        print(f"\n✅ KEY STRENGTHS:")
        for strength in summary['key_strengths']:
            print(f"   • {strength}")
        
        if summary['areas_for_improvement']:
            print(f"\n⚠️ AREAS FOR IMPROVEMENT:")
            for area in summary['areas_for_improvement']:
                print(f"   • {area}")
        
        if summary['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in summary['recommendations']:
                print(f"   • {rec}")
        
        # Export report
        report_path = analyzer.export_performance_report()
        print(f"\n📄 Full report exported to: {report_path}")
        
    else:
        print("Failed to analyze model performance.")
