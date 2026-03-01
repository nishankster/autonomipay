import logging
from typing import Optional

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

    # Basic debit/credit transaction code sets (can be extended as needed)
    DEBIT_CODES = {"27", "37", "28", "38"}
    CREDIT_CODES = {"22", "32", "23", "33"}

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
            lines = file_content.splitlines()

            if not lines:
                raise AchParsingException("File is empty", filename=filename)

            line_number = 0
            file_header: Optional[AchFileHeader] = None
            batches: list[AchBatch] = []
            current_batch: Optional[AchBatchHeader] = None
            current_entries: list[AchEntry] = []
            file_control: Optional[AchFileControl] = None

            for line_number, line in enumerate(lines, 1):
                #line = line.rstrip("\r\n")

                # Validate record length (strict 94 chars)
                if not AchFieldExtractor.validate_record_length(line):
                    raise AchParsingException(
                        f"Invalid record length {len(line)} (expected {AchFileParser.RECORD_LENGTH})",
                        line_number=line_number,
                        filename=filename,
                    )

                # Extract record type
                try:
                    record_type = AchFieldExtractor.extract_string_field(line, 1, 1)
                except Exception as e:
                    raise AchParsingException(
                        f"Failed to extract record type: {str(e)}",
                        line_number=line_number,
                        filename=filename,
                    )

                # Process based on record type
                if record_type == AchFileParser.RECORD_TYPE_FILE_HEADER:
                    if file_header is not None:
                        raise AchParsingException(
                            "Multiple file headers encountered",
                            line_number=line_number,
                            filename=filename,
                        )
                    file_header = AchFileParser._parse_file_header(line, line_number)
                    logger.info(f"Parsed file header at line {line_number}")

                elif record_type == AchFileParser.RECORD_TYPE_BATCH_HEADER:
                    # Close previous batch if exists (must have had a batch control)
                    if current_batch is not None:
                        raise AchParsingException(
                            "New batch header encountered before batch control of previous batch",
                            line_number=line_number,
                            filename=filename,
                        )

                    current_batch = AchFileParser._parse_batch_header(line, line_number)
                    current_entries = []
                    logger.info(f"Parsed batch header at line {line_number}")

                elif record_type == AchFileParser.RECORD_TYPE_ENTRY_DETAIL:
                    if current_batch is None:
                        raise AchParsingException(
                            "Entry detail record encountered outside of a batch",
                            line_number=line_number,
                            filename=filename,
                        )
                    entry = AchFileParser._parse_entry_detail(line, line_number)
                    # Ensure entry has addenda container
                    if not hasattr(entry, "addenda_records"):
                        # If your model uses a different field name, adjust here
                        entry.addenda_records = []
                    current_entries.append(entry)

                elif record_type == AchFileParser.RECORD_TYPE_ADDENDA:
                    if current_batch is None:
                        raise AchParsingException(
                            "Addenda record encountered outside of a batch",
                            line_number=line_number,
                            filename=filename,
                        )
                    if not current_entries:
                        raise AchParsingException(
                            "Addenda record encountered before any entry detail in batch",
                            line_number=line_number,
                            filename=filename,
                        )
                    addenda = AchFileParser._parse_addenda(line, line_number)
                    # Attach addenda to the most recent entry
                    last_entry = current_entries[-1]
                    if not hasattr(last_entry, "addenda_records"):
                        last_entry.addenda_records = []
                    last_entry.addenda_records.append(addenda)

                elif record_type == AchFileParser.RECORD_TYPE_BATCH_CONTROL:
                    if current_batch is None:
                        raise AchParsingException(
                            "Batch control record encountered without an open batch",
                            line_number=line_number,
                            filename=filename,
                        )

                    batch_control = AchFileParser._parse_batch_control(line, line_number)

                    # Validate batch totals against entries/addenda
                    AchFileParser._validate_batch_totals(
                        current_batch,
                        current_entries,
                        batch_control,
                        line_number,
                        filename,
                    )

                    # Close batch
                    batch = AchBatch(
                        batch_header=current_batch,
                        entries=current_entries,
                        addenda_records=[],  # kept for compatibility; addenda now live on entries
                        batch_control=batch_control,
                    )
                    batches.append(batch)
                    current_batch = None
                    current_entries = []
                    logger.info(f"Parsed batch control at line {line_number}")

                elif record_type == AchFileParser.RECORD_TYPE_FILE_CONTROL:
                    if file_control is not None:
                        raise AchParsingException(
                            "Multiple file control records encountered",
                            line_number=line_number,
                            filename=filename,
                        )
                    file_control = AchFileParser._parse_file_control(line, line_number)
                    logger.info(f"Parsed file control at line {line_number}")

                else:
                    raise AchParsingException(
                        f"Unknown record type '{record_type}'",
                        line_number=line_number,
                        filename=filename,
                    )

            # Validate required records
            if not file_header:
                raise AchParsingException("File header record not found", filename=filename)
            if not file_control:
                raise AchParsingException("File control record not found", filename=filename)
            if current_batch is not None:
                raise AchParsingException(
                    "Unclosed batch at end of file (missing batch control)",
                    filename=filename,
                )
            if not batches:
                raise AchParsingException("No batches found in file", filename=filename)

            # File-level validation against file control
            AchFileParser._validate_file_totals(batches, file_control, filename)

            # Create and return AchFile
            ach_file = AchFile(
                file_header=file_header,
                batches=batches,
                file_control=file_control,
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
                line_number=line_number,
                filename=filename,
            )

    # ---------- Record parsers ----------

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
                record_type="1",
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
                company_identification=AchFieldExtractor.extract_string_field(line, 41, 50),
                standard_entry_class_code=AchFieldExtractor.extract_string_field(line, 51, 53),
                company_entry_description=AchFieldExtractor.extract_string_field(line, 54, 63),
                company_descriptive_date=AchFieldExtractor.extract_string_field(line, 64, 69),
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
                record_type="5",
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
                individual_identification_number=AchFieldExtractor.extract_string_field(
                    line, 40, 54
                ),
                individual_name=AchFieldExtractor.extract_string_field(line, 55, 76),
                discretionary_data=AchFieldExtractor.extract_string_field(line, 77, 78),
                addenda_record_indicator=AchFieldExtractor.extract_string_field(line, 79, 79),
                trace_number=AchFieldExtractor.extract_string_field(line, 80, 94),
            )
        except Exception as e:
            raise AchParsingException(
                f"Failed to parse entry detail: {str(e)}",
                line_number=line_number,
                record_type="6",
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
                record_type="7",
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
                total_debit_entry_dollar_amount=AchFieldExtractor.extract_amount_field(
                    line, 21, 32
                ),
                total_credit_entry_dollar_amount=AchFieldExtractor.extract_amount_field(
                    line, 33, 44
                ),
                company_identification=AchFieldExtractor.extract_string_field(line, 45, 54),
                message_authentication_code=AchFieldExtractor.extract_string_field(line, 55, 73),
                reserved=AchFieldExtractor.extract_string_field(line, 74, 79),
                originating_dfi_identification=AchFieldExtractor.extract_string_field(line, 80, 87),
                batch_number=AchFieldExtractor.extract_string_field(line, 88, 94),
            )
        except Exception as e:
            raise AchParsingException(
                f"Failed to parse batch control: {str(e)}",
                line_number=line_number,
                record_type="8",
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
                total_debit_entry_dollar_amount=AchFieldExtractor.extract_amount_field(
                    line, 32, 43
                ),
                total_credit_entry_dollar_amount=AchFieldExtractor.extract_amount_field(
                    line, 44, 55
                ),
                reserved=AchFieldExtractor.extract_string_field(line, 56, 94),
            )
        except Exception as e:
            raise AchParsingException(
                f"Failed to parse file control: {str(e)}",
                line_number=line_number,
                record_type="9",
            )

    # ---------- Validation helpers ----------

    @staticmethod
    def _validate_batch_totals(
        batch_header: AchBatchHeader,
        entries: list[AchEntry],
        batch_control: AchBatchControl,
        line_number: int,
        filename: str,
    ) -> None:
        """Validate batch-level counts and totals against the batch control record."""

        # Entry + addenda count
        total_entries = len(entries)
        total_addenda = sum(len(getattr(e, "addenda_records", [])) for e in entries)
        actual_count = total_entries + total_addenda
        expected_count = batch_control.entry_addenda_count

        if expected_count != actual_count:
            raise AchParsingException(
                f"Entry/Addenda count mismatch in batch {batch_header.batch_number}: "
                f"expected {expected_count}, got {actual_count}",
                line_number=line_number,
                filename=filename,
            )

        # Entry hash (sum of first 8 digits of receiving DFI, truncated to last 10 digits)
        try:
            computed_hash = sum(
                int(e.receiving_dfi_identification[:8]) for e in entries
            )
        except ValueError:
            raise AchParsingException(
                "Non-numeric receiving DFI identification encountered while computing entry hash",
                line_number=line_number,
                filename=filename,
            )

        computed_hash_str = str(computed_hash)[-10:]  # NACHA truncation rule
        expected_hash_str = batch_control.entry_hash.strip().lstrip("0") or "0"
        normalized_computed = computed_hash_str.lstrip("0") or "0"

        if normalized_computed != expected_hash_str:
            raise AchParsingException(
                f"Entry hash mismatch in batch {batch_header.batch_number}: "
                f"expected {batch_control.entry_hash}, got {computed_hash_str}",
                line_number=line_number,
                filename=filename,
            )

        # Debit/Credit totals
        computed_debits = sum(
            e.amount
            for e in entries
            if e.transaction_code in AchFileParser.DEBIT_CODES
        )
        computed_credits = sum(
            e.amount
            for e in entries
            if e.transaction_code in AchFileParser.CREDIT_CODES
        )

        if computed_debits != batch_control.total_debit_entry_dollar_amount:
            raise AchParsingException(
                f"Debit total mismatch in batch {batch_header.batch_number}: "
                f"expected {batch_control.total_debit_entry_dollar_amount}, got {computed_debits}",
                line_number=line_number,
                filename=filename,
            )

        if computed_credits != batch_control.total_credit_entry_dollar_amount:
            raise AchParsingException(
                f"Credit total mismatch in batch {batch_header.batch_number}: "
                f"expected {batch_control.total_credit_entry_dollar_amount}, got {computed_credits}",
                line_number=line_number,
                filename=filename,
            )

    @staticmethod
    def _validate_file_totals(
        batches: list[AchBatch],
        file_control: AchFileControl,
        filename: str,
    ) -> None:
        """Validate file-level counts and totals against the file control record."""

        # Batch count
        if file_control.batch_count != len(batches):
            raise AchParsingException(
                f"File batch count mismatch: expected {file_control.batch_count}, "
                f"got {len(batches)}",
                filename=filename,
            )

        # Entry + addenda count
        total_entries = sum(len(b.entries) for b in batches)
        total_addenda = sum(
            len(getattr(e, "addenda_records", []))
            for b in batches
            for e in b.entries
        )
        actual_count = total_entries + total_addenda

        if file_control.entry_addenda_count != actual_count:
            raise AchParsingException(
                f"File entry/addenda count mismatch: expected {file_control.entry_addenda_count}, "
                f"got {actual_count}",
                filename=filename,
            )

        # Debit/Credit totals
        file_debits = sum(
            e.amount
            for b in batches
            for e in b.entries
            if e.transaction_code in AchFileParser.DEBIT_CODES
        )
        file_credits = sum(
            e.amount
            for b in batches
            for e in b.entries
            if e.transaction_code in AchFileParser.CREDIT_CODES
        )

        if file_debits != file_control.total_debit_entry_dollar_amount:
            raise AchParsingException(
                f"File debit total mismatch: expected {file_control.total_debit_entry_dollar_amount}, "
                f"got {file_debits}",
                filename=filename,
            )

        if file_credits != file_control.total_credit_entry_dollar_amount:
            raise AchParsingException(
                f"File credit total mismatch: expected {file_control.total_credit_entry_dollar_amount}, "
                f"got {file_credits}",
                filename=filename,
            )
