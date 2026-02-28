"""
ACH field extraction utility for parsing fixed-width records.

This module provides utilities to extract fields from fixed-width
ACH records according to NACHA specifications.
"""

import logging
from typing import Optional

from app.exceptions import ValidationException

logger = logging.getLogger(__name__)


class AchFieldExtractor:
    """Utility class for extracting fields from ACH records."""
    
    @staticmethod
    def extract_string_field(record: str, start: int, end: int) -> str:
        """
        Extract string field from record.
        
        Args:
            record: The ACH record string
            start: Start position (1-indexed)
            end: End position (1-indexed, inclusive)
        
        Returns:
            str: Extracted and trimmed string
        
        Raises:
            ValidationException: If field extraction fails
        """
        try:
            # Convert to 0-indexed
            start_idx = start - 1
            end_idx = end
            
            if start_idx < 0 or end_idx > len(record):
                raise ValidationException(
                    f"Field position out of range",
                    field=f"pos_{start}_{end}",
                    value=f"record_length={len(record)}"
                )
            
            value = record[start_idx:end_idx]
            return value.strip()
            
        except Exception as e:
            if isinstance(e, ValidationException):
                raise
            raise ValidationException(
                f"Failed to extract string field: {str(e)}",
                field=f"pos_{start}_{end}"
            )
    
    @staticmethod
    def extract_numeric_field(record: str, start: int, end: int) -> int:
        """
        Extract numeric field from record.
        
        Args:
            record: The ACH record string
            start: Start position (1-indexed)
            end: End position (1-indexed, inclusive)
        
        Returns:
            int: Extracted numeric value
        
        Raises:
            ValidationException: If field is not numeric
        """
        try:
            value = AchFieldExtractor.extract_string_field(record, start, end)
            
            if not value:
                return 0
            
            if not value.isdigit():
                raise ValidationException(
                    f"Field is not numeric",
                    field=f"pos_{start}_{end}",
                    value=value
                )
            
            return int(value)
            
        except ValidationException:
            raise
        except Exception as e:
            raise ValidationException(
                f"Failed to extract numeric field: {str(e)}",
                field=f"pos_{start}_{end}"
            )
    
    @staticmethod
    def extract_amount_field(record: str, start: int, end: int) -> int:
        """
        Extract amount field (in cents) from record.
        
        Args:
            record: The ACH record string
            start: Start position (1-indexed)
            end: End position (1-indexed, inclusive)
        
        Returns:
            int: Amount in cents
        
        Raises:
            ValidationException: If field is not a valid amount
        """
        try:
            amount_str = AchFieldExtractor.extract_string_field(record, start, end)
            
            if not amount_str:
                return 0
            
            # Remove leading zeros and convert to integer
            amount_cents = int(amount_str)
            
            if amount_cents < 0:
                raise ValidationException(
                    "Amount cannot be negative",
                    field=f"pos_{start}_{end}",
                    value=amount_str
                )
            
            return amount_cents
            
        except ValidationException:
            raise
        except Exception as e:
            raise ValidationException(
                f"Failed to extract amount field: {str(e)}",
                field=f"pos_{start}_{end}"
            )
    
    @staticmethod
    def extract_date_field(record: str, start: int, end: int) -> str:
        """
        Extract date field (YYMMDD format) from record.
        
        Args:
            record: The ACH record string
            start: Start position (1-indexed)
            end: End position (1-indexed, inclusive)
        
        Returns:
            str: Date in YYMMDD format
        
        Raises:
            ValidationException: If field is not a valid date
        """
        try:
            date_str = AchFieldExtractor.extract_string_field(record, start, end)
            
            if not date_str or len(date_str) != 6:
                raise ValidationException(
                    "Date must be in YYMMDD format",
                    field=f"pos_{start}_{end}",
                    value=date_str
                )
            
            if not date_str.isdigit():
                raise ValidationException(
                    "Date must contain only digits",
                    field=f"pos_{start}_{end}",
                    value=date_str
                )
            
            # Validate month and day
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            
            if month < 1 or month > 12:
                raise ValidationException(
                    f"Invalid month: {month}",
                    field=f"pos_{start}_{end}",
                    value=date_str
                )
            
            if day < 1 or day > 31:
                raise ValidationException(
                    f"Invalid day: {day}",
                    field=f"pos_{start}_{end}",
                    value=date_str
                )
            
            return date_str
            
        except ValidationException:
            raise
        except Exception as e:
            raise ValidationException(
                f"Failed to extract date field: {str(e)}",
                field=f"pos_{start}_{end}"
            )
    
    @staticmethod
    def extract_time_field(record: str, start: int, end: int) -> str:
        """
        Extract time field (HHMM format) from record.
        
        Args:
            record: The ACH record string
            start: Start position (1-indexed)
            end: End position (1-indexed, inclusive)
        
        Returns:
            str: Time in HHMM format
        
        Raises:
            ValidationException: If field is not a valid time
        """
        try:
            time_str = AchFieldExtractor.extract_string_field(record, start, end)
            
            if not time_str or len(time_str) != 4:
                raise ValidationException(
                    "Time must be in HHMM format",
                    field=f"pos_{start}_{end}",
                    value=time_str
                )
            
            if not time_str.isdigit():
                raise ValidationException(
                    "Time must contain only digits",
                    field=f"pos_{start}_{end}",
                    value=time_str
                )
            
            # Validate hours and minutes
            hours = int(time_str[0:2])
            minutes = int(time_str[2:4])
            
            if hours < 0 or hours > 23:
                raise ValidationException(
                    f"Invalid hours: {hours}",
                    field=f"pos_{start}_{end}",
                    value=time_str
                )
            
            if minutes < 0 or minutes > 59:
                raise ValidationException(
                    f"Invalid minutes: {minutes}",
                    field=f"pos_{start}_{end}",
                    value=time_str
                )
            
            return time_str
            
        except ValidationException:
            raise
        except Exception as e:
            raise ValidationException(
                f"Failed to extract time field: {str(e)}",
                field=f"pos_{start}_{end}"
            )
    
    @staticmethod
    def validate_record_length(record: str, expected_length: int = 94) -> bool:
        """
        Validate ACH record length.
        
        Args:
            record: The ACH record string
            expected_length: Expected record length (default 94)
        
        Returns:
            bool: True if valid, False otherwise
        """
        if len(record) != expected_length:
            logger.warning(
                f"Record length mismatch: expected {expected_length}, got {len(record)}"
            )
            return False
        return True
    
    @staticmethod
    def validate_record_type(record: str, expected_type: str) -> bool:
        """
        Validate ACH record type.
        
        Args:
            record: The ACH record string
            expected_type: Expected record type (1-9)
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            record_type = AchFieldExtractor.extract_string_field(record, 1, 1)
            if record_type != expected_type:
                logger.warning(
                    f"Record type mismatch: expected {expected_type}, got {record_type}"
                )
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to validate record type: {str(e)}")
            return False
