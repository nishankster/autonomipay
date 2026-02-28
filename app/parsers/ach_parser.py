"""
ACH file parser for NACHA format files.

This module parses ACH files according to NACHA specifications,
extracting all record types and validating data.
"""

import logging
from typing import BinaryIO, Optional
from io import StringIO

from app.models.ach_models import (
    AchFile, AchFileHeader, AchBatch, AchBatchHeader, AchEntry,
    AchAddenda, AchBatchControl, AchFileControl
)
from app.parsers.ach_field_extractor import AchFieldExtractor
from app.exceptions import AchParsingException

logger = logging.getLogger(__name__)


class AchFileParser:
    """Parser for ACH files in NACHA format."""
    
    # Record type constants
    RECORD_TYPE_FILE_HEADER = "1"
    RECORD_TYPE_BATCH_HEADER = "5"
    RECORD_TYPE_ENTRY_DETAIL = "6"
    RECORD_TYPE_ADDENDA = "7"
    RECORD_TYPE_BATCH_CONTROL = "8"
    RECORD_TYPE_FILE_CONTROL = "9"
    
    RECORD_LENGTH = 94
    
    @staticmethod
    async def parse_file(file_content: str, filename: str) -> AchFile:
        """
        Parse an ACH file.
        
        Args:
            file_content: Content of the ACH file
            filename: Name of the file being parsed
        
        Returns:
            AchFile: Parsed ACH file object
        
        Raises:
            AchParsingException: If parsing fails
        """
        try:
            lines = file_content.strip().split('\n')
            
            if not lines:
                raise AchParsingException("File is empty", filename=filename)
            
            line_number = 0
            file_header = None
            batches = []
            current_batch = None
            current_entries = []
            current_addenda = []
            file_control = None
            
            for line_number, line in enumerate(lines, 1):
                # Remove line endings
                line = line.rstrip('\r\n')
                
                # Validate record length
                if not AchFieldExtractor.validate_record_length(line):
                    logger.warning(f"Line {line_number}: Invalid record length {len(line)}")
                
                # Extract record type
                try:
                    record_type = AchFieldExtractor.extract_string_field(line, 1, 1)
                except Exception as e:
                    raise AchParsingException(
                        f"Failed to extract record type: {str(e)}",
                        line_number=line_number
                    )
                
                # Process based on record type
                if record_type == AchFileParser.RECORD_TYPE_FILE_HEADER:
                    file_header = AchFileParser._parse_file_header(line, line_number)
                    logger.info(f"Parsed file header at line {line_number}")
                
                elif record_type == AchFileParser.RECORD_TYPE_BATCH_HEADER:
                    # Save previous batch if exists
                    if current_batch:
                        batch = AchBatch(
                            batch_header=current_batch,
                            entries=current_entries,
                            addenda_records=current_addenda,
                            batch_control=None
                        )
                        batches.append(batch)
                        current_entries = []
                        current_addenda = []
                    
                    current_batch = AchFileParser._parse_batch_header(line, line_number)
                    logger.info(f"Parsed batch header at line {line_number}")
                
                elif record_type == AchFileParser.RECORD_TYPE_ENTRY_DETAIL:
                    entry = AchFileParser._parse_entry_detail(line, line_number)
                    current_entries.append(entry)
                
                elif record_type == AchFileParser.RECORD_TYPE_ADDENDA:
                    addenda = AchFileParser._parse_addenda(line, line_number)
                    current_addenda.append(addenda)
                
                elif record_type == AchFileParser.RECORD_TYPE_BATCH_CONTROL:
                    batch_control = AchFileParser._parse_batch_control(line, line_number)
                    if current_batch:
                        batch = AchBatch(
                            batch_header=current_batch,
                            entries=current_entries,
                            addenda_records=current_addenda,
                            batch_control=batch_control
                        )
                        batches.append(batch)
                        current_batch = None
                        current_entries = []
                        current_addenda = []
                    logger.info(f"Parsed batch control at line {line_number}")
                
                elif record_type == AchFileParser.RECORD_TYPE_FILE_CONTROL:
                    file_control = AchFileParser._parse_file_control(line, line_number)
                    logger.info(f"Parsed file control at line {line_number}")
                
                else:
                    logger.warning(f"Line {line_number}: Unknown record type '{record_type}'")
            
            # Validate required records
            if not file_header:
                raise AchParsingException("File header record not found")
            if not file_control:
                raise AchParsingException("File control record not found")
            if not batches:
                raise AchParsingException("No batches found in file")
            
            # Create and return AchFile
            ach_file = AchFile(
                file_header=file_header,
                batches=batches,
                file_control=file_control
            )
            
            logger.info(
                f"Successfully parsed ACH file: {ach_file.total_entries} entries, "
                f"{len(batches)} batches"
            )
            
            return ach_file
            
        except AchParsingException:
            raise
        except Exception as e:
            raise AchParsingException(
                f"Unexpected error during parsing: {str(e)}",
                line_number=line_number
            )
    
    @staticmethod
    def _parse_file_header(line: str, line_number: int) -> AchFileHeader:
        """Parse file header record (Type 1)."""
        try:
            
            return AchFileHeader( 
	            record_type=AchFieldExtractor.extract_string_field(line, 1, 1), 
	            priority_code=AchFieldExtractor.extract_string_field(line, 2, 3), 
                immediate_destination=AchFieldExtractor.extract_string_field(line, 4, 13), 
                immediate_origin=AchFieldExtractor.extract_string_field(line, 14, 23), 
                file_creation_date=AchFieldExtractor.extract_date_field(line, 24, 29), 
                file_creation_time=AchFieldExtractor.extract_time_field(line, 30, 33), 
                file_id_modifier=AchFieldExtractor.extract_string_field(line, 34, 34), 
                record_size=AchFieldExtractor.extract_numeric_field(line, 35, 37), 
                blocking_factor=AchFieldExtractor.extract_numeric_field(line, 38, 39), 
                format_code=AchFieldExtractor.extract_string_field(line, 40, 40), 
                immediate_destination_name=AchFieldExtractor.extract_string_field(line, 41, 63), 
                immediate_origin_name=AchFieldExtractor.extract_string_field(line, 64, 86), 
                reference_code=AchFieldExtractor.extract_string_field(line, 87, 94), 
	)
        except Exception as e:
            raise AchParsingException(
                f"Failed to parse file header: {str(e)}",
                line_number=line_number,
                record_type="1"
            )
    
    @staticmethod
    def _parse_batch_header(line: str, line_number: int) -> AchBatchHeader:
        """Parse batch header record (Type 5)."""
        try:
            return AchBatchHeader(
                record_type=AchFieldExtractor.extract_string_field(line, 1, 1),
                service_class_code=AchFieldExtractor.extract_string_field(line, 2, 4),
                company_name=AchFieldExtractor.extract_string_field(line, 5, 20),
                company_discretionary_data=AchFieldExtractor.extract_string_field(line, 21, 40),
                company_identification=AchFieldExtractor.extract_string_field(line, 41, 48),
                standard_entry_class_code=AchFieldExtractor.extract_string_field(line, 49, 51),
                company_entry_description=AchFieldExtractor.extract_string_field(line, 52, 61),
                company_descriptive_date=AchFieldExtractor.extract_string_field(line, 62, 69),
                effective_entry_date=AchFieldExtractor.extract_date_field(line, 70, 75),
                settlement_date=AchFieldExtractor.extract_string_field(line, 76, 78),
                originator_status_code=AchFieldExtractor.extract_string_field(line, 79, 79),
                originating_dfi_identification=AchFieldExtractor.extract_string_field(line, 80, 87),
                batch_number=AchFieldExtractor.extract_string_field(line, 88, 94),
            )
        except Exception as e:
            raise AchParsingException(
                f"Failed to parse batch header: {str(e)}",
                line_number=line_number,
                record_type="5"
            )
    
    @staticmethod
    def _parse_entry_detail(line: str, line_number: int) -> AchEntry:
        """Parse entry detail record (Type 6)."""
        try:
            return AchEntry(
                record_type=AchFieldExtractor.extract_string_field(line, 1, 1),
                transaction_code=AchFieldExtractor.extract_string_field(line, 2, 3),
                receiving_dfi_identification=AchFieldExtractor.extract_string_field(line, 4, 11),
                check_digit=AchFieldExtractor.extract_string_field(line, 12, 12),
                account_number=AchFieldExtractor.extract_string_field(line, 13, 29),
                amount=AchFieldExtractor.extract_amount_field(line, 30, 39),
                individual_identification_number=AchFieldExtractor.extract_string_field(line, 40, 54),
                individual_name=AchFieldExtractor.extract_string_field(line, 55, 76),
                discretionary_data=AchFieldExtractor.extract_string_field(line, 77, 78),
                addenda_record_indicator=AchFieldExtractor.extract_string_field(line, 79, 79),
                trace_number=AchFieldExtractor.extract_string_field(line, 80, 94),
            )
        except Exception as e:
            raise AchParsingException(
                f"Failed to parse entry detail: {str(e)}",
                line_number=line_number,
                record_type="6"
            )
    
    @staticmethod
    def _parse_addenda(line: str, line_number: int) -> AchAddenda:
        """Parse addenda record (Type 7)."""
        try:
            return AchAddenda(
                record_type=AchFieldExtractor.extract_string_field(line, 1, 1),
                addenda_type_code=AchFieldExtractor.extract_string_field(line, 2, 3),
                payment_related_information=AchFieldExtractor.extract_string_field(line, 4, 83),
                addenda_sequence_number=AchFieldExtractor.extract_string_field(line, 84, 87),
                entry_detail_sequence_number=AchFieldExtractor.extract_string_field(line, 88, 94),
            )
        except Exception as e:
            raise AchParsingException(
                f"Failed to parse addenda: {str(e)}",
                line_number=line_number,
                record_type="7"
            )
    
    @staticmethod
    def _parse_batch_control(line: str, line_number: int) -> AchBatchControl:
        """Parse batch control record (Type 8)."""
        try:
            return AchBatchControl(
                record_type=AchFieldExtractor.extract_string_field(line, 1, 1),
                service_class_code=AchFieldExtractor.extract_string_field(line, 2, 4),
                entry_addenda_count=AchFieldExtractor.extract_numeric_field(line, 5, 10),
                entry_hash=AchFieldExtractor.extract_string_field(line, 11, 20),
                total_debit_entry_dollar_amount=AchFieldExtractor.extract_amount_field(line, 21, 32),
                total_credit_entry_dollar_amount=AchFieldExtractor.extract_amount_field(line, 33, 44),
                company_identification=AchFieldExtractor.extract_string_field(line, 45, 52),
                message_authentication_code=AchFieldExtractor.extract_string_field(line, 53, 73),
                reserved=AchFieldExtractor.extract_string_field(line, 74, 76),
                originating_dfi_identification=AchFieldExtractor.extract_string_field(line, 77, 84),
                batch_number=AchFieldExtractor.extract_string_field(line, 85, 94),
            )
        except Exception as e:
            raise AchParsingException(
                f"Failed to parse batch control: {str(e)}",
                line_number=line_number,
                record_type="8"
            )
    
    @staticmethod
    def _parse_file_control(line: str, line_number: int) -> AchFileControl:
        """Parse file control record (Type 9)."""
        try:
            return AchFileControl(
                record_type=AchFieldExtractor.extract_string_field(line, 1, 1),
                batch_count=AchFieldExtractor.extract_numeric_field(line, 2, 7),
                block_count=AchFieldExtractor.extract_numeric_field(line, 8, 13),
                entry_addenda_count=AchFieldExtractor.extract_numeric_field(line, 14, 21),
                entry_hash=AchFieldExtractor.extract_string_field(line, 22, 31),
                total_debit_entry_dollar_amount=AchFieldExtractor.extract_amount_field(line, 32, 43),
                total_credit_entry_dollar_amount=AchFieldExtractor.extract_amount_field(line, 44, 55),
                reserved=AchFieldExtractor.extract_string_field(line, 56, 94),
            )
        except Exception as e:
            raise AchParsingException(
                f"Failed to parse file control: {str(e)}",
                line_number=line_number,
                record_type="9"
            )
