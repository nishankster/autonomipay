package com.example.ach2rtp.service;

import com.example.ach2rtp.exception.RtpMessageException;
import com.example.ach2rtp.model.ach.AchEntry;
import com.example.ach2rtp.model.ach.AchFileHeader;
import com.example.ach2rtp.model.ach.AchBatchHeader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

/**
 * Service for building ISO 20022 RTP (pacs.008) messages from ACH entries.
 * 
 * Converts ACH transaction data to ISO 20022 XML format.
 */
@Service
public class RtpMessageBuilderService {

    private static final Logger logger = LoggerFactory.getLogger(RtpMessageBuilderService.class);
    private static final String CURRENCY_CODE = "USD";
    private static final DateTimeFormatter ISO_DATETIME_FORMATTER = 
            DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss'Z'");

    /**
     * Build an ISO 20022 pacs.008 RTP message from an ACH entry.
     * 
     * @param achEntry The ACH entry to convert
     * @param fileHeader The ACH file header
     * @param batchHeader The ACH batch header
     * @return XML string containing the RTP message
     * @throws RtpMessageException if message generation fails
     */
    public String buildRtpMessage(AchEntry achEntry, AchFileHeader fileHeader, AchBatchHeader batchHeader) 
            throws RtpMessageException {
        
        try {
            logger.debug("Building RTP message for entry: {}", achEntry.getTraceNumber());
            
            String messageId = UUID.randomUUID().toString();
            String paymentId = achEntry.getTraceNumber();
            LocalDateTime creationTime = LocalDateTime.now();
            
            // Validate required fields
            validateEntry(achEntry);
            
            // Build XML message
            StringBuilder xml = new StringBuilder();
            xml.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
            xml.append("<Document xmlns=\"urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02\">\n");
            xml.append("  <CstmrCdtTrfInitn>\n");
            
            // Group Header
            xml.append("    <GrpHdr>\n");
            xml.append("      <MsgId>").append(escapeXml(messageId)).append("</MsgId>\n");
            xml.append("      <CreDtTm>").append(creationTime.format(ISO_DATETIME_FORMATTER)).append("</CreDtTm>\n");
            xml.append("      <NbOfTxns>1</NbOfTxns>\n");
            xml.append("      <CtrlSum>").append(achEntry.getAmount()).append("</CtrlSum>\n");
            xml.append("    </GrpHdr>\n");
            
            // Payment Information
            xml.append("    <PmtInf>\n");
            xml.append("      <PmtInfId>").append(escapeXml(paymentId)).append("</PmtInfId>\n");
            xml.append("      <PmtMtd>TRF</PmtMtd>\n");
            xml.append("      <CreDtTm>").append(creationTime.format(ISO_DATETIME_FORMATTER)).append("</CreDtTm>\n");
            xml.append("      <NbOfTxns>1</NbOfTxns>\n");
            xml.append("      <CtrlSum>").append(achEntry.getAmount()).append("</CtrlSum>\n");
            
            // Debtor (Originating Party)
            xml.append("      <Debtor>\n");
            xml.append("        <Nm>").append(escapeXml(fileHeader.getImmediateOriginName())).append("</Nm>\n");
            xml.append("      </Debtor>\n");
            
            // Debtor Account
            xml.append("      <DebtorAcct>\n");
            xml.append("        <Id>").append(escapeXml(fileHeader.getImmediateOrigin())).append("</Id>\n");
            xml.append("        <Ccy>").append(CURRENCY_CODE).append("</Ccy>\n");
            xml.append("      </DebtorAcct>\n");
            
            // Debtor Agent (Originating Bank)
            xml.append("      <DebtorAgt>\n");
            xml.append("        <FinInstnId>\n");
            xml.append("          <ClrSysMmbId>\n");
            xml.append("            <MmbId>").append(escapeXml(fileHeader.getImmediateOrigin())).append("</MmbId>\n");
            xml.append("          </ClrSysMmbId>\n");
            xml.append("        </FinInstnId>\n");
            xml.append("      </DebtorAgt>\n");
            
            // Credit Transfer Transaction Information
            xml.append("      <CdtTrfTxInf>\n");
            xml.append("        <PmtId>\n");
            xml.append("          <InstrId>").append(escapeXml(achEntry.getTraceNumber())).append("</InstrId>\n");
            xml.append("          <EndToEndId>").append(escapeXml(achEntry.getTraceNumber())).append("</EndToEndId>\n");
            xml.append("        </PmtId>\n");
            xml.append("        <Amt>\n");
            xml.append("          <InstdAmt Ccy=\"").append(CURRENCY_CODE).append("\">");
            xml.append(achEntry.getAmount()).append("</InstdAmt>\n");
            xml.append("        </Amt>\n");
            
            // Creditor Agent (Receiving Bank)
            xml.append("        <CdtrAgt>\n");
            xml.append("          <FinInstnId>\n");
            xml.append("            <ClrSysMmbId>\n");
            xml.append("              <MmbId>").append(escapeXml(achEntry.getReceivingDfiRoutingNumber())).append("</MmbId>\n");
            xml.append("            </ClrSysMmbId>\n");
            xml.append("          </FinInstnId>\n");
            xml.append("        </CdtrAgt>\n");
            
            // Creditor (Beneficiary)
            xml.append("        <Cdtr>\n");
            xml.append("          <Nm>").append(escapeXml(achEntry.getIndividualName())).append("</Nm>\n");
            xml.append("        </Cdtr>\n");
            
            // Creditor Account
            xml.append("        <CdtrAcct>\n");
            xml.append("          <Id>").append(escapeXml(achEntry.getReceivingDfiAccountNumber())).append("</Id>\n");
            xml.append("          <Ccy>").append(CURRENCY_CODE).append("</Ccy>\n");
            xml.append("        </CdtrAcct>\n");
            
            // Remittance Information (from addenda if available)
            if (!achEntry.getAddendaRecords().isEmpty()) {
                xml.append("        <RmtInf>\n");
                xml.append("          <Ustrd>");
                achEntry.getAddendaRecords().forEach(addenda -> 
                    xml.append(escapeXml(addenda.getPaymentRelatedInformation())).append(" ")
                );
                xml.append("</Ustrd>\n");
                xml.append("        </RmtInf>\n");
            }
            
            xml.append("      </CdtTrfTxInf>\n");
            xml.append("    </PmtInf>\n");
            xml.append("  </CstmrCdtTrfInitn>\n");
            xml.append("</Document>\n");
            
            String message = xml.toString();
            logger.debug("Successfully built RTP message for entry: {}", achEntry.getTraceNumber());
            
            return message;
            
        } catch (Exception e) {
            logger.error("Error building RTP message for entry {}: {}", 
                    achEntry.getTraceNumber(), e.getMessage(), e);
            throw new RtpMessageException(
                    "Failed to build RTP message for entry " + achEntry.getTraceNumber(),
                    achEntry.getTraceNumber(),
                    e.getMessage(),
                    e
            );
        }
    }

    /**
     * Validate that the ACH entry contains all required fields for RTP conversion.
     * 
     * @param entry The ACH entry to validate
     * @throws RtpMessageException if validation fails
     */
    private void validateEntry(AchEntry entry) throws RtpMessageException {
        if (entry.getReceivingDfiRoutingNumber() == null || entry.getReceivingDfiRoutingNumber().trim().isEmpty()) {
            throw new RtpMessageException("Receiving DFI routing number is required", entry.getTraceNumber(), 
                    "Missing receiving DFI routing number");
        }
        
        if (entry.getReceivingDfiAccountNumber() == null || entry.getReceivingDfiAccountNumber().trim().isEmpty()) {
            throw new RtpMessageException("Receiving account number is required", entry.getTraceNumber(), 
                    "Missing receiving account number");
        }
        
        if (entry.getAmount() == null || entry.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new RtpMessageException("Amount must be positive", entry.getTraceNumber(), 
                    "Invalid amount: " + entry.getAmount());
        }
        
        if (entry.getIndividualName() == null || entry.getIndividualName().trim().isEmpty()) {
            throw new RtpMessageException("Individual name is required", entry.getTraceNumber(), 
                    "Missing individual name");
        }
        
        if (entry.getTraceNumber() == null || entry.getTraceNumber().trim().isEmpty()) {
            throw new RtpMessageException("Trace number is required", entry.getTraceNumber(), 
                    "Missing trace number");
        }
    }

    /**
     * Escape special XML characters in a string.
     * 
     * @param str String to escape
     * @return Escaped string safe for XML
     */
    private String escapeXml(String str) {
        if (str == null) {
            return "";
        }
        return str.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&apos;");
    }
}
