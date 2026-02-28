"""
ACH data models representing NACHA file structure.

These models represent the different record types in an ACH file:
- File Header (Type 1)
- Batch Header (Type 5)
- Entry Detail (Type 6)
- Addenda Record (Type 7)
- Batch Control (Type 8)
- File Control (Type 9)
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class AchFileHeader:
    """ACH File Header Record (Type 1)."""
    
    record_type: str  # "1"
    priority_code: str
    immediate_destination: str
    immediate_origin: str
    file_creation_date: str  # YYMMDD
    file_creation_time: str  # HHMM
    file_id_modifier: str
    record_size: int
    blocking_factor: int
    format_code: str
    immediate_destination_name: str
    immediate_origin_name: str
    reference_code: str


@dataclass
class AchBatchHeader:
    """ACH Batch Header Record (Type 5)."""
    
    record_type: str  # "5"
    service_class_code: str
    company_name: str
    company_discretionary_data: str
    company_identification: str
    standard_entry_class_code: str
    company_entry_description: str
    company_descriptive_date: str
    effective_entry_date: str  # YYMMDD
    settlement_date: str  # YYMMDD
    originator_status_code: str
    originating_dfi_identification: str
    batch_number: str


@dataclass
class AchEntry:
    """ACH Entry Detail Record (Type 6)."""
    
    record_type: str  # "6"
    transaction_code: str
    receiving_dfi_identification: str
    check_digit: str
    account_number: str
    amount: int  # In cents
    individual_identification_number: str
    individual_name: str
    discretionary_data: str
    addenda_record_indicator: str
    trace_number: str


@dataclass
class AchAddenda:
    """ACH Addenda Record (Type 7)."""
    
    record_type: str  # "7"
    addenda_type_code: str
    payment_related_information: str
    addenda_sequence_number: str
    entry_detail_sequence_number: str


@dataclass
class AchBatchControl:
    """ACH Batch Control Record (Type 8)."""
    
    record_type: str  # "8"
    service_class_code: str
    entry_addenda_count: int
    entry_hash: str
    total_debit_entry_dollar_amount: int
    total_credit_entry_dollar_amount: int
    company_identification: str
    message_authentication_code: str
    reserved: str
    originating_dfi_identification: str
    batch_number: str


@dataclass
class AchFileControl:
    """ACH File Control Record (Type 9)."""
    
    record_type: str  # "9"
    batch_count: int
    block_count: int
    entry_addenda_count: int
    entry_hash: str
    total_debit_entry_dollar_amount: int
    total_credit_entry_dollar_amount: int
    reserved: str


@dataclass
class AchBatch:
    """Container for a batch of ACH entries."""
    
    batch_header: AchBatchHeader
    entries: List[AchEntry]
    addenda_records: List[AchAddenda]
    batch_control: AchBatchControl


@dataclass
class AchFile:
    """Complete ACH file representation."""
    
    file_header: AchFileHeader
    batches: List[AchBatch]
    file_control: AchFileControl
    
    @property
    def total_entries(self) -> int:
        """Get total number of entries across all batches."""
        return sum(len(batch.entries) for batch in self.batches)
    
    @property
    def total_debit_amount(self) -> int:
        """Get total debit amount in cents."""
        total = 0
        for batch in self.batches:
            if batch.batch_control:
                total += batch.batch_control.total_debit_entry_dollar_amount
        return total
    
    @property
    def total_credit_amount(self) -> int:
        """Get total credit amount in cents."""
        total = 0
        for batch in self.batches:
            if batch.batch_control:
                total += batch.batch_control.total_credit_entry_dollar_amount
        return total
