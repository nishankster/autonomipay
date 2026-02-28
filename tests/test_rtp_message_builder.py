"""
Unit tests for RTP message builder.
"""

import pytest
from app.services.rtp_message_builder import RtpMessageBuilder
from app.models.ach_models import AchEntry, AchFileHeader, AchBatchHeader
from app.exceptions import RtpMessageException


class TestRtpMessageBuilder:
    """Test cases for RTP message generation."""
    
    @pytest.fixture
    def sample_entry(self):
        """Create sample ACH entry."""
        return AchEntry(
            record_type="6",
            transaction_code="22",
            receiving_dfi_identification="12100002",
            check_digit="1",
            account_number="0123456789",
            amount=100000,  # $1000.00
            individual_identification_number="ID123456",
            individual_name="John Doe",
            discretionary_data="",
            addenda_record_indicator="0",
            trace_number="000000000000001"
        )
    
    @pytest.fixture
    def sample_file_header(self):
        """Create sample ACH file header."""
        return AchFileHeader(
            record_type="1",
            priority_code="00",
            immediate_destination="210000001",
            immediate_origin="094101041",
            file_creation_date="210101",
            file_creation_time="0101",
            file_id_modifier="A",
            record_size=94,
            blocking_factor=10,
            format_code="1",
            immediate_destination_name="DESTINATION BANK",
            immediate_origin_name="ORIGIN BANK",
            reference_code="000000"
        )
    
    @pytest.fixture
    def sample_batch_header(self):
        """Create sample ACH batch header."""
        return AchBatchHeader(
            record_type="5",
            service_class_code="200",
            company_name="ACME CORP",
            company_discretionary_data="",
            company_identification="1234567890",
            standard_entry_class_code="PPD",
            company_entry_description="PAYROLL",
            company_descriptive_date="210101",
            effective_entry_date="210101",
            settlement_date="210",
            originator_status_code="0",
            originating_dfi_identification="09410104",
            batch_number="000001"
        )
    
    def test_build_rtp_message_success(
        self,
        sample_entry,
        sample_file_header,
        sample_batch_header
    ):
        """Test successful RTP message generation."""
        message = RtpMessageBuilder.build_rtp_message(
            entry=sample_entry,
            file_header=sample_file_header,
            batch_header=sample_batch_header
        )
        
        assert message is not None
        assert "<?xml" in message or "<Document" in message
        assert "CstmrCdtTrfInitn" in message
        assert "John Doe" in message
        assert "1000.00" in message
    
    def test_build_rtp_message_missing_name(
        self,
        sample_entry,
        sample_file_header,
        sample_batch_header
    ):
        """Test RTP message generation with missing name."""
        sample_entry.individual_name = ""
        
        with pytest.raises(RtpMessageException):
            RtpMessageBuilder.build_rtp_message(
                entry=sample_entry,
                file_header=sample_file_header,
                batch_header=sample_batch_header
            )
    
    def test_build_rtp_message_zero_amount(
        self,
        sample_entry,
        sample_file_header,
        sample_batch_header
    ):
        """Test RTP message generation with zero amount."""
        sample_entry.amount = 0
        
        with pytest.raises(RtpMessageException):
            RtpMessageBuilder.build_rtp_message(
                entry=sample_entry,
                file_header=sample_file_header,
                batch_header=sample_batch_header
            )
    
    def test_format_amount(self):
        """Test amount formatting."""
        assert RtpMessageBuilder._format_amount(100000) == "1000.00"
        assert RtpMessageBuilder._format_amount(1) == "0.01"
        assert RtpMessageBuilder._format_amount(100) == "1.00"
    
    def test_escape_xml(self):
        """Test XML character escaping."""
        assert RtpMessageBuilder._escape_xml("A & B") == "A &amp; B"
        assert RtpMessageBuilder._escape_xml("<tag>") == "&lt;tag&gt;"
        assert RtpMessageBuilder._escape_xml('He said "Hi"') == 'He said &quot;Hi&quot;'
