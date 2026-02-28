"""
RTP message builder for generating ISO 20022 pacs.008 messages.

This module converts ACH entries to ISO 20022 XML format for
Real-Time Payments processing.
"""

import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import Optional
import uuid

from app.models.ach_models import AchEntry, AchFileHeader, AchBatchHeader
from app.exceptions import RtpMessageException

logger = logging.getLogger(__name__)


class RtpMessageBuilder:
    """Builder for ISO 20022 pacs.008 RTP messages."""
    
    # ISO 20022 namespace
    NAMESPACE = "urn:iso:std:iso:20022:tech:xsd:pacs.008.003.02"
    
    @staticmethod
    def build_rtp_message(
        entry: AchEntry,
        file_header: AchFileHeader,
        batch_header: AchBatchHeader,
        message_id: Optional[str] = None
    ) -> str:
        """
        Build ISO 20022 pacs.008 RTP message from ACH entry.
        
        Args:
            entry: ACH entry detail record
            file_header: ACH file header
            batch_header: ACH batch header
            message_id: Optional message ID (generated if not provided)
        
        Returns:
            str: ISO 20022 XML message
        
        Raises:
            RtpMessageException: If message generation fails
        """
        try:
            if not message_id:
                message_id = str(uuid.uuid4())
            
            # Validate required fields
            RtpMessageBuilder._validate_entry(entry)
            
            # Create root element
            root = ET.Element("Document", {
                "xmlns": RtpMessageBuilder.NAMESPACE,
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
            })
            
            # Create CstmrCdtTrfInitn (Customer Credit Transfer Initiation)
            cust_cdt_trf = ET.SubElement(root, "CstmrCdtTrfInitn")
            
            # Add Group Header
            RtpMessageBuilder._add_group_header(cust_cdt_trf, message_id, file_header)
            
            # Add Payment Information
            RtpMessageBuilder._add_payment_info(
                cust_cdt_trf, entry, file_header, batch_header, message_id
            )
            
            # Convert to pretty-printed XML string
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            
            # Remove XML declaration and extra whitespace
            xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])
            
            logger.info(f"Generated RTP message for entry {entry.trace_number}")
            
            return xml_str
            
        except RtpMessageException:
            raise
        except Exception as e:
            raise RtpMessageException(
                f"Failed to build RTP message: {str(e)}",
                entry_id=entry.trace_number
            )
    
    @staticmethod
    def _validate_entry(entry: AchEntry) -> None:
        """
        Validate ACH entry has required fields for RTP conversion.
        
        Args:
            entry: ACH entry to validate
        
        Raises:
            RtpMessageException: If validation fails
        """
        if not entry.individual_name or not entry.individual_name.strip():
            raise RtpMessageException(
                "Individual name is required",
                entry_id=entry.trace_number
            )
        
        if entry.amount <= 0:
            raise RtpMessageException(
                f"Amount must be positive, got {entry.amount}",
                entry_id=entry.trace_number
            )
        
        if not entry.receiving_dfi_identification:
            raise RtpMessageException(
                "Receiving DFI identification is required",
                entry_id=entry.trace_number
            )
        
        if not entry.account_number or not entry.account_number.strip():
            raise RtpMessageException(
                "Account number is required",
                entry_id=entry.trace_number
            )
    
    @staticmethod
    def _add_group_header(
        parent: ET.Element,
        message_id: str,
        file_header: AchFileHeader
    ) -> None:
        """Add Group Header to RTP message."""
        grp_hdr = ET.SubElement(parent, "GrpHdr")
        
        # Message ID
        ET.SubElement(grp_hdr, "MsgId").text = message_id
        
        # Creation DateTime
        ET.SubElement(grp_hdr, "CreDtTm").text = datetime.utcnow().isoformat() + "Z"
        
        # Message Count
        ET.SubElement(grp_hdr, "MsgCnt").text = "1"
        
        # Initiating Party
        initg_pty = ET.SubElement(grp_hdr, "InitgPty")
        ET.SubElement(initg_pty, "Nm").text = RtpMessageBuilder._escape_xml(
            file_header.immediate_origin_name[:70]
        )
    
    @staticmethod
    def _add_payment_info(
        parent: ET.Element,
        entry: AchEntry,
        file_header: AchFileHeader,
        batch_header: AchBatchHeader,
        message_id: str
    ) -> None:
        """Add Payment Information to RTP message."""
        pmt_inf = ET.SubElement(parent, "PmtInf")
        
        # Payment Information ID
        ET.SubElement(pmt_inf, "PmtInfId").text = message_id
        
        # Payment Method
        ET.SubElement(pmt_inf, "PmtMtd").text = "TRF"  # Credit Transfer
        
        # Batch Booking
        ET.SubElement(pmt_inf, "BtchBookg").text = "false"
        
        # Number of Transactions
        ET.SubElement(pmt_inf, "NbOfTxns").text = "1"
        
        # Control Sum
        ET.SubElement(pmt_inf, "CtrlSum").text = RtpMessageBuilder._format_amount(entry.amount)
        
        # Payment Type Information
        pmt_tp_inf = ET.SubElement(pmt_inf, "PmtTpInf")
        ET.SubElement(pmt_tp_inf, "InstrPrty").text = "NORM"
        
        # Debtor
        RtpMessageBuilder._add_debtor(pmt_inf, file_header, batch_header)
        
        # Debtor Account
        RtpMessageBuilder._add_debtor_account(pmt_inf, file_header)
        
        # Debtor Agent
        RtpMessageBuilder._add_debtor_agent(pmt_inf, file_header)
        
        # Credit Transfer Transaction Information
        RtpMessageBuilder._add_credit_transfer_transaction(pmt_inf, entry, file_header)
    
    @staticmethod
    def _add_debtor(
        parent: ET.Element,
        file_header: AchFileHeader,
        batch_header: AchBatchHeader
    ) -> None:
        """Add Debtor information."""
        dbtr = ET.SubElement(parent, "Dbtr")
        ET.SubElement(dbtr, "Nm").text = RtpMessageBuilder._escape_xml(
            batch_header.company_name[:70]
        )
    
    @staticmethod
    def _add_debtor_account(parent: ET.Element, file_header: AchFileHeader) -> None:
        """Add Debtor Account information."""
        dbtr_acct = ET.SubElement(parent, "DbtrAcct")
        
        # Account ID
        acct_id = ET.SubElement(dbtr_acct, "Id")
        ET.SubElement(acct_id, "Othr").text = file_header.immediate_origin[:17]
        
        # Account Type
        ET.SubElement(dbtr_acct, "Tp").text = "CACC"
    
    @staticmethod
    def _add_debtor_agent(parent: ET.Element, file_header: AchFileHeader) -> None:
        """Add Debtor Agent (Bank) information."""
        dbtr_agt = ET.SubElement(parent, "DbtrAgt")
        
        # Financial Institution Identification
        fin_instn_id = ET.SubElement(dbtr_agt, "FinInstnId")
        ET.SubElement(fin_instn_id, "BICFI").text = "UNKNOWN"  # Would need mapping
    
    @staticmethod
    def _add_credit_transfer_transaction(
        parent: ET.Element,
        entry: AchEntry,
        file_header: AchFileHeader
    ) -> None:
        """Add Credit Transfer Transaction Information."""
        cdt_trf_txn_inf = ET.SubElement(parent, "CdtTrfTxnInf")
        
        # Payment ID
        pmt_id = ET.SubElement(cdt_trf_txn_inf, "PmtId")
        ET.SubElement(pmt_id, "InstrId").text = entry.trace_number
        ET.SubElement(pmt_id, "EndToEndId").text = entry.individual_identification_number
        
        # Amount
        amt = ET.SubElement(cdt_trf_txn_inf, "Amt")
        amt_elem = ET.SubElement(amt, "InstdAmt")
        amt_elem.set("Ccy", "USD")
        amt_elem.text = RtpMessageBuilder._format_amount(entry.amount)
        
        # Charge Bearer
        ET.SubElement(cdt_trf_txn_inf, "ChrgBr").text = "SLEV"
        
        # Creditor Agent
        RtpMessageBuilder._add_creditor_agent(cdt_trf_txn_inf, entry)
        
        # Creditor
        RtpMessageBuilder._add_creditor(cdt_trf_txn_inf, entry)
        
        # Creditor Account
        RtpMessageBuilder._add_creditor_account(cdt_trf_txn_inf, entry)
        
        # Purpose
        purp = ET.SubElement(cdt_trf_txn_inf, "Purp")
        ET.SubElement(purp, "Cd").text = "SALA"  # Salary
        
        # Remittance Information
        RtpMessageBuilder._add_remittance_info(cdt_trf_txn_inf, entry)
    
    @staticmethod
    def _add_creditor_agent(parent: ET.Element, entry: AchEntry) -> None:
        """Add Creditor Agent (Receiving Bank) information."""
        cdt_agt = ET.SubElement(parent, "CdtrAgt")
        
        # Financial Institution Identification
        fin_instn_id = ET.SubElement(cdt_agt, "FinInstnId")
        ET.SubElement(fin_instn_id, "BICFI").text = "UNKNOWN"  # Would need mapping
    
    @staticmethod
    def _add_creditor(parent: ET.Element, entry: AchEntry) -> None:
        """Add Creditor (Recipient) information."""
        cdtr = ET.SubElement(parent, "Cdtr")
        ET.SubElement(cdtr, "Nm").text = RtpMessageBuilder._escape_xml(
            entry.individual_name[:70]
        )
    
    @staticmethod
    def _add_creditor_account(parent: ET.Element, entry: AchEntry) -> None:
        """Add Creditor Account information."""
        cdtr_acct = ET.SubElement(parent, "CdtrAcct")
        
        # Account ID
        acct_id = ET.SubElement(cdtr_acct, "Id")
        ET.SubElement(acct_id, "Othr").text = entry.account_number.strip()
        
        # Account Type
        ET.SubElement(cdtr_acct, "Tp").text = "CACC"
    
    @staticmethod
    def _add_remittance_info(parent: ET.Element, entry: AchEntry) -> None:
        """Add Remittance Information."""
        rmtc_inf = ET.SubElement(parent, "RmtcInf")
        
        # Unstructured
        ustrd = ET.SubElement(rmtc_inf, "Ustrd")
        ustrd.text = RtpMessageBuilder._escape_xml(
            entry.discretionary_data[:140] if entry.discretionary_data else "Payment"
        )
    
    @staticmethod
    def _format_amount(amount_cents: int) -> str:
        """
        Format amount from cents to decimal string.
        
        Args:
            amount_cents: Amount in cents
        
        Returns:
            str: Formatted amount (e.g., "1234.56")
        """
        dollars = amount_cents // 100
        cents = amount_cents % 100
        return f"{dollars}.{cents:02d}"
    
    @staticmethod
    def _escape_xml(text: str) -> str:
        """
        Escape special XML characters.
        
        Args:
            text: Text to escape
        
        Returns:
            str: Escaped text
        """
        if not text:
            return ""
        
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace("\"", "&quot;")
        text = text.replace("'", "&apos;")
        
        return text
