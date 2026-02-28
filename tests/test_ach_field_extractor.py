"""
Unit tests for ACH field extractor.
"""

import pytest
from app.parsers.ach_field_extractor import AchFieldExtractor
from app.exceptions import ValidationException


class TestAchFieldExtractor:
    """Test cases for ACH field extraction."""
    
    def test_extract_string_field(self):
        """Test string field extraction."""
        record = "1 094101041234567890210101011234567890000000000000000000000000000000000000000000000000000000000000"
        result = AchFieldExtractor.extract_string_field(record, 1, 1)
        assert result == "1"
    
    def test_extract_numeric_field(self):
        """Test numeric field extraction."""
        record = "1 094101041234567890210101011234567890000000000000000000000000000000000000000000000000000000000000"
        result = AchFieldExtractor.extract_numeric_field(record, 2, 3)
        assert result == 94
    
    def test_extract_amount_field(self):
        """Test amount field extraction."""
        record = "6221000210123456789000000001000000000000000000000000000000000000000000000000000000000000000000000001"
        result = AchFieldExtractor.extract_amount_field(record, 30, 39)
        assert result == 1000000
    
    def test_extract_date_field_valid(self):
        """Test valid date field extraction."""
        record = "1 094101041234567890210101011234567890000000000000000000000000000000000000000000000000000000000000"
        result = AchFieldExtractor.extract_date_field(record, 22, 27)
        assert result == "010101"
    
    def test_extract_date_field_invalid_month(self):
        """Test invalid month in date field."""
        record = "1 094101041234567890210113011234567890000000000000000000000000000000000000000000000000000000000000"
        with pytest.raises(ValidationException):
            AchFieldExtractor.extract_date_field(record, 22, 27)
    
    def test_extract_time_field_valid(self):
        """Test valid time field extraction."""
        record = "1 094101041234567890210101011234567890000000000000000000000000000000000000000000000000000000000000"
        result = AchFieldExtractor.extract_time_field(record, 28, 31)
        assert result == "0101"
    
    def test_extract_time_field_invalid_hours(self):
        """Test invalid hours in time field."""
        record = "1 094101041234567890210101251234567890000000000000000000000000000000000000000000000000000000000000"
        with pytest.raises(ValidationException):
            AchFieldExtractor.extract_time_field(record, 28, 31)
    
    def test_validate_record_length_valid(self):
        """Test valid record length."""
        record = "1" * 94
        assert AchFieldExtractor.validate_record_length(record) is True
    
    def test_validate_record_length_invalid(self):
        """Test invalid record length."""
        record = "1" * 50
        assert AchFieldExtractor.validate_record_length(record) is False
    
    def test_validate_record_type_valid(self):
        """Test valid record type."""
        record = "1" + "0" * 93
        assert AchFieldExtractor.validate_record_type(record, "1") is True
    
    def test_validate_record_type_invalid(self):
        """Test invalid record type."""
        record = "5" + "0" * 93
        assert AchFieldExtractor.validate_record_type(record, "1") is False
