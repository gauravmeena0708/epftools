import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationUtils:
    """
    Validation utilities for EPF/EPFO-specific data formats.

    Provides validators for member IDs, claim IDs, establishment codes,
    and other EPFO-specific identifiers.
    """

    # EPFO ID patterns
    MEMBER_ID_PATTERN = r'^PYKRP\d{7}\d{3}\d{7}$'
    CLAIM_ID_PATTERN = r'^PYKRP\d{12}$'
    ESTABLISHMENT_CODE_PATTERN = r'^PYKRP\d{7}$'
    TASK_ID_PATTERN = r'^\d{5}$'
    GROUP_ID_PATTERN = r'^\d{3}$'

    # Valid form types
    VALID_FORM_TYPES = [
        'Form-19', 'Form-31', 'Form-10C', 'Form-10D',
        'Form-13', 'Form-14', 'Form-20', 'Form-5IF',
        # Variations
        'Form-31 [ 68J / Illness ]', 'Form-31 [ COVID ]',
        'Form-13 (Transfer Out) [ WITH-MONEY ]',
        'Form-13 (Transfer Out) [ WITHOUT-MONEY  ]',
        'Form-13 (Transfer Out) [ OTHERS ]',
        'Form-13 (Transfer In / Same Office)',
        'Form-10C [ Withdrawal Benefit ] ',
        'Form-10C [ Scheme Certificate ]',
        'Form-10D [ Death Case ]',
        'Form-14 (Funding of LIP)'
    ]

    @staticmethod
    def validate_member_id(member_id):
        """
        Validate EPFO Member ID format.

        Format: PYKRP + 7-digit establishment code + 3-digit extension + 7-digit employee number
        Total: PYKRP followed by 17 digits

        Args:
            member_id (str): Member ID to validate

        Returns:
            tuple: (is_valid: bool, message: str)

        Examples:
            >>> ValidationUtils.validate_member_id("PYKRP00534130000030651")
            (True, "Valid")
            >>> ValidationUtils.validate_member_id("PYKRP123")
            (False, "Invalid format: must be PYKRP + 17 digits")
        """
        if not member_id or not isinstance(member_id, str):
            return False, "Member ID must be a non-empty string"

        if not re.match(ValidationUtils.MEMBER_ID_PATTERN, member_id):
            return False, "Invalid format: must be PYKRP + 17 digits (7-digit est + 3-digit ext + 7-digit emp)"

        return True, "Valid"

    @staticmethod
    def validate_claim_id(claim_id):
        """
        Validate EPFO Claim ID format.

        Format: PYKRP + 12 digits
        Example: PYKRP230650019449

        Args:
            claim_id (str): Claim ID to validate

        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not claim_id or not isinstance(claim_id, str):
            return False, "Claim ID must be a non-empty string"

        if not re.match(ValidationUtils.CLAIM_ID_PATTERN, claim_id):
            return False, "Invalid format: must be PYKRP + 12 digits"

        return True, "Valid"

    @staticmethod
    def validate_establishment_code(est_code):
        """
        Validate establishment code format.

        Format: PYKRP + 7 digits
        Example: PYKRP0053413

        Args:
            est_code (str): Establishment code to validate

        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not est_code or not isinstance(est_code, str):
            return False, "Establishment code must be a non-empty string"

        if not re.match(ValidationUtils.ESTABLISHMENT_CODE_PATTERN, est_code):
            return False, "Invalid format: must be PYKRP + 7 digits"

        return True, "Valid"

    @staticmethod
    def validate_task_id(task_id):
        """
        Validate Task ID format.

        Format: 5 digits
        Example: 10406

        Args:
            task_id (str or int): Task ID to validate

        Returns:
            tuple: (is_valid: bool, message: str)
        """
        task_id_str = str(task_id)

        if not re.match(ValidationUtils.TASK_ID_PATTERN, task_id_str):
            return False, "Invalid format: must be 5 digits"

        return True, "Valid"

    @staticmethod
    def validate_group_id(group_id):
        """
        Validate Group ID format.

        Format: 3 digits
        Example: 104

        Args:
            group_id (str or int): Group ID to validate

        Returns:
            tuple: (is_valid: bool, message: str)
        """
        group_id_str = str(group_id)

        if not re.match(ValidationUtils.GROUP_ID_PATTERN, group_id_str):
            return False, "Invalid format: must be 3 digits"

        return True, "Valid"

    @staticmethod
    def validate_form_type(form_type):
        """
        Validate form type against known EPFO form types.

        Args:
            form_type (str): Form type to validate

        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not form_type or not isinstance(form_type, str):
            return False, "Form type must be a non-empty string"

        # Check exact match first
        if form_type in ValidationUtils.VALID_FORM_TYPES:
            return True, "Valid"

        # Check if it starts with a valid form prefix
        valid_prefixes = ['Form-19', 'Form-31', 'Form-10C', 'Form-10D',
                         'Form-13', 'Form-14', 'Form-20', 'Form-5IF']

        for prefix in valid_prefixes:
            if form_type.startswith(prefix):
                return True, f"Valid (variant of {prefix})"

        return False, f"Unknown form type: {form_type}"

    @staticmethod
    def parse_member_id(member_id):
        """
        Parse Member ID into components.

        Args:
            member_id (str): Valid member ID

        Returns:
            dict: Dictionary with keys 'prefix', 'establishment_code',
                  'extension', 'employee_number', or None if invalid

        Example:
            >>> ValidationUtils.parse_member_id("PYKRP00534130000030651")
            {
                'prefix': 'PYKRP',
                'establishment_code': '0053413',
                'extension': '000',
                'employee_number': '0030651',
                'full_establishment': 'PYKRP0053413000'
            }
        """
        is_valid, msg = ValidationUtils.validate_member_id(member_id)

        if not is_valid:
            logger.warning(f"Invalid member ID: {msg}")
            return None

        return {
            'prefix': member_id[:5],
            'establishment_code': member_id[5:12],
            'extension': member_id[12:15],
            'employee_number': member_id[15:22],
            'full_establishment': member_id[:15]
        }

    @staticmethod
    def validate_date_format(date_str, format='%d/%m/%Y'):
        """
        Validate date string format.

        Args:
            date_str (str): Date string to validate
            format (str): Expected date format (default: '%d/%m/%Y')

        Returns:
            tuple: (is_valid: bool, message: str, parsed_date: datetime or None)
        """
        if not date_str or not isinstance(date_str, str):
            return False, "Date must be a non-empty string", None

        try:
            parsed_date = datetime.strptime(date_str, format)
            return True, "Valid", parsed_date
        except ValueError as e:
            return False, f"Invalid date format (expected {format}): {str(e)}", None

    @staticmethod
    def validate_pending_days(days):
        """
        Validate pending days value.

        Args:
            days (int or str): Pending days value

        Returns:
            tuple: (is_valid: bool, message: str, days_int: int or None)
        """
        try:
            days_int = int(days)

            if days_int < 0:
                return False, "Pending days cannot be negative", None

            if days_int > 10000:
                return False, "Pending days seems unreasonably high (>10000)", days_int

            return True, "Valid", days_int

        except (ValueError, TypeError):
            return False, f"Pending days must be a valid integer, got: {days}", None

    @staticmethod
    def validate_dataframe_columns(df, required_columns, strict=False):
        """
        Validate that a DataFrame has required columns.

        Args:
            df (pd.DataFrame): DataFrame to validate
            required_columns (list): List of required column names
            strict (bool): If True, DataFrame must have ONLY these columns

        Returns:
            tuple: (is_valid: bool, message: str, missing_columns: list)
        """
        if df is None or df.empty:
            return False, "DataFrame is None or empty", required_columns

        df_columns = set(df.columns)
        required_set = set(required_columns)

        missing = required_set - df_columns

        if missing:
            return False, f"Missing columns: {missing}", list(missing)

        if strict:
            extra = df_columns - required_set
            if extra:
                return False, f"Extra columns found: {extra}", []

        return True, "Valid", []

    @staticmethod
    def validate_batch(items, validator_func, stop_on_error=False):
        """
        Validate a batch of items using a validator function.

        Args:
            items (list): List of items to validate
            validator_func (callable): Validator function that returns (bool, str)
            stop_on_error (bool): Stop on first error

        Returns:
            dict: {
                'total': int,
                'valid': int,
                'invalid': int,
                'errors': list of (item, error_message)
            }
        """
        results = {
            'total': len(items),
            'valid': 0,
            'invalid': 0,
            'errors': []
        }

        for item in items:
            is_valid, message = validator_func(item)

            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].append((item, message))

                if stop_on_error:
                    break

        return results


# Example usage
"""
from epftools import ValidationUtils

# Validate single ID
is_valid, msg = ValidationUtils.validate_member_id("PYKRP00534130000030651")
print(f"Valid: {is_valid}, Message: {msg}")

# Parse member ID
components = ValidationUtils.parse_member_id("PYKRP00534130000030651")
print(f"Establishment: {components['establishment_code']}")

# Batch validation
member_ids = ["PYKRP00534130000030651", "INVALID123", "PYKRP00536390000017473"]
results = ValidationUtils.validate_batch(member_ids, ValidationUtils.validate_member_id)
print(f"Valid: {results['valid']}/{results['total']}")
print(f"Errors: {results['errors']}")

# DataFrame validation
import pandas as pd
df = pd.read_csv("claims.csv")
is_valid, msg, missing = ValidationUtils.validate_dataframe_columns(
    df, ['CLAIM ID', 'MEMBER ID', 'STATUS']
)
"""
