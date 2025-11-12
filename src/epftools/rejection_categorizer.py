import os
import logging
import pickle
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Install with: pip install epftools[ml]")


class RejectionCategorizer:
    """
    ML-based categorization of EPF claim rejection reasons.

    Uses TF-IDF vectorization and Logistic Regression to automatically
    categorize rejection reasons into predefined categories.

    Requires scikit-learn: pip install epftools[ml]
    """

    def __init__(self):
        """
        Initialize RejectionCategorizer.

        Raises:
            ImportError: If scikit-learn is not installed
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError(
                "scikit-learn is required for RejectionCategorizer. "
                "Install with: pip install epftools[ml]"
            )

        self.vectorizer = None
        self.model = None
        self.categories = None
        self.is_trained = False

    def train(self, training_data, reason_column='reason', category_column='category',
              test_size=0.2, random_state=42):
        """
        Train the categorizer on labeled data.

        Args:
            training_data (pd.DataFrame or str): Training data DataFrame or path to CSV
            reason_column (str): Column containing rejection reasons
            category_column (str): Column containing categories
            test_size (float): Proportion of data for testing (default: 0.2)
            random_state (int): Random seed for reproducibility

        Returns:
            dict: Training metrics including accuracy and classification report

        Raises:
            ValueError: If required columns not found or data is empty
        """
        # Load data if path provided
        if isinstance(training_data, str):
            if not os.path.exists(training_data):
                raise FileNotFoundError(f"Training data file not found: {training_data}")
            training_data = pd.read_csv(training_data)

        # Validate columns
        if reason_column not in training_data.columns:
            raise ValueError(f"Column '{reason_column}' not found in training data")

        if category_column not in training_data.columns:
            raise ValueError(f"Column '{category_column}' not found in training data")

        # Prepare data
        df = training_data[[reason_column, category_column]].copy()
        df[reason_column] = df[reason_column].fillna('')
        df[category_column] = df[category_column].fillna('')

        # Remove empty entries
        df = df[(df[reason_column] != '') & (df[category_column] != '')]

        if len(df) == 0:
            raise ValueError("No valid training data after cleaning")

        logger.info(f"Training on {len(df)} samples with {df[category_column].nunique()} categories")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df[reason_column], df[category_column],
            test_size=test_size, random_state=random_state
        )

        # Vectorize text
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        # Train model
        self.model = LogisticRegression(max_iter=1000, random_state=random_state)
        self.model.fit(X_train_vec, y_train)

        # Store categories
        self.categories = list(self.model.classes_)
        self.is_trained = True

        # Evaluate
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        logger.info(f"Training complete. Accuracy: {accuracy:.2%}")

        return {
            'accuracy': accuracy,
            'classification_report': report,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'categories': self.categories
        }

    def predict(self, reasons):
        """
        Predict categories for rejection reasons.

        Args:
            reasons (str or list): Single reason string or list of reasons

        Returns:
            pd.DataFrame: DataFrame with columns ['reason', 'predicted_category', 'confidence']

        Raises:
            RuntimeError: If model not trained
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        # Convert single string to list
        if isinstance(reasons, str):
            reasons = [reasons]

        # Ensure reasons are strings and handle NaN
        reasons_clean = [str(r) if pd.notna(r) else '' for r in reasons]

        # Vectorize
        X = self.vectorizer.transform(reasons_clean)

        # Predict
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        confidences = probabilities.max(axis=1)

        # Create result DataFrame
        result = pd.DataFrame({
            'reason': reasons_clean,
            'predicted_category': predictions,
            'confidence': confidences
        })

        return result

    def predict_dataframe(self, df, reason_column='reason',
                         add_confidence=True, inplace=False):
        """
        Predict categories for reasons in a DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            reason_column (str): Column containing rejection reasons
            add_confidence (bool): Add confidence scores column
            inplace (bool): Modify DataFrame inplace

        Returns:
            pd.DataFrame: DataFrame with added 'predicted_category' column
                         (and 'confidence' if add_confidence=True)

        Raises:
            ValueError: If reason_column not found
            RuntimeError: If model not trained
        """
        if reason_column not in df.columns:
            raise ValueError(f"Column '{reason_column}' not found in DataFrame")

        if not inplace:
            df = df.copy()

        predictions = self.predict(df[reason_column].tolist())

        df['predicted_category'] = predictions['predicted_category'].values

        if add_confidence:
            df['confidence'] = predictions['confidence'].values

        logger.info(f"Predicted categories for {len(df)} records")

        return df

    def get_low_confidence_predictions(self, df, threshold=0.5):
        """
        Get predictions with confidence below threshold.

        Args:
            df (pd.DataFrame): DataFrame with 'confidence' column
            threshold (float): Confidence threshold (default: 0.5)

        Returns:
            pd.DataFrame: Filtered DataFrame with low confidence predictions
        """
        if 'confidence' not in df.columns:
            raise ValueError("DataFrame must have 'confidence' column")

        low_conf = df[df['confidence'] < threshold].copy()

        logger.info(f"Found {len(low_conf)} predictions with confidence < {threshold}")

        return low_conf

    def save_model(self, filepath):
        """
        Save trained model to file.

        Args:
            filepath (str): Path to save model

        Raises:
            RuntimeError: If model not trained
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Nothing to save.")

        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'categories': self.categories
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath):
        """
        Load trained model from file.

        Args:
            filepath (str): Path to saved model

        Raises:
            FileNotFoundError: If model file not found
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.vectorizer = model_data['vectorizer']
        self.model = model_data['model']
        self.categories = model_data['categories']
        self.is_trained = True

        logger.info(f"Model loaded from {filepath}")

    def get_feature_importance(self, top_n=10):
        """
        Get most important features (words) for each category.

        Args:
            top_n (int): Number of top features to return per category

        Returns:
            dict: Dictionary mapping category to top features

        Raises:
            RuntimeError: If model not trained
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained.")

        feature_names = self.vectorizer.get_feature_names_out()
        importance_dict = {}

        for i, category in enumerate(self.categories):
            # Get coefficients for this category
            if len(self.categories) == 2:
                # Binary classification
                coef = self.model.coef_[0] if i == 1 else -self.model.coef_[0]
            else:
                # Multi-class classification
                coef = self.model.coef_[i]

            # Get top features
            top_indices = coef.argsort()[-top_n:][::-1]
            top_features = [(feature_names[idx], coef[idx]) for idx in top_indices]

            importance_dict[category] = top_features

        return importance_dict


# Example usage
"""
from epftools import RejectionCategorizer
import pandas as pd

# Initialize categorizer
categorizer = RejectionCategorizer()

# Train on labeled data
training_df = pd.read_csv('reason_category.csv')
metrics = categorizer.train(training_df, reason_column='reason', category_column='category')
print(f"Accuracy: {metrics['accuracy']:.2%}")

# Predict on new data
new_reasons = [
    "PAN card not submitted",
    "15G form is incorrect",
    "TDS not deducted"
]
predictions = categorizer.predict(new_reasons)
print(predictions)

# Or predict on entire DataFrame
claims_df = pd.read_csv('rejected_claims.csv')
claims_df = categorizer.predict_dataframe(claims_df, reason_column='REJECT_REASON')

# Get low confidence predictions for review
low_conf = categorizer.get_low_confidence_predictions(claims_df, threshold=0.6)
print(f"Review {len(low_conf)} low confidence predictions")

# Save model for reuse
categorizer.save_model('rejection_model.pkl')

# Load model later
categorizer2 = RejectionCategorizer()
categorizer2.load_model('rejection_model.pkl')
"""
