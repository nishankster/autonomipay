package com.example.ach2rtp.service;

import com.example.ach2rtp.exception.RtpMessageException;
import com.example.ach2rtp.model.ach.AchEntry;
import com.example.ach2rtp.model.ach.AchFileHeader;
import com.example.ach2rtp.model.ach.AchBatchHeader;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalTime;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("RTP Message Builder Service Tests")
class RtpMessageBuilderServiceTest {

    private RtpMessageBuilderService rtpMessageBuilderService;
    private AchEntry achEntry;
    private AchFileHeader fileHeader;
    private AchBatchHeader batchHeader;

    @BeforeEach
    void setUp() {
        rtpMessageBuilderService = new RtpMessageBuilderService();

        // Create test data
        fileHeader = new AchFileHeader();
        fileHeader.setImmediateOrigin("021000021");
        fileHeader.setImmediateOriginName("ORIGIN BANK");
        fileHeader.setImmediateDestination("021000021");
        fileHeader.setImmediateDestinationName("DEST BANK");
        fileHeader.setFileCreationDate(LocalDate.now());
        fileHeader.setFileCreationTime(LocalTime.now());

        batchHeader = new AchBatchHeader();
        batchHeader.setEffectiveDate(LocalDate.now());
        batchHeader.setCompanyName("TEST COMPANY");

        achEntry = new AchEntry();
        achEntry.setTraceNumber("000000000000001");
        achEntry.setReceivingDfiRoutingNumber("021000021");
        achEntry.setReceivingDfiAccountNumber("123456789");
        achEntry.setAmount(new BigDecimal("100.00"));
        achEntry.setIndividualName("JOHN DOE");
    }

    @Test
    @DisplayName("Should build valid RTP message")
    void testBuildRtpMessage() {
        String message = rtpMessageBuilderService.buildRtpMessage(achEntry, fileHeader, batchHeader);

        assertNotNull(message);
        assertTrue(message.contains("<?xml version=\"1.0\""));
        assertTrue(message.contains("CstmrCdtTrfInitn"));
        assertTrue(message.contains("JOHN DOE"));
        assertTrue(message.contains("100.00"));
    }

    @Test
    @DisplayName("Should throw exception for missing routing number")
    void testBuildRtpMessageMissingRoutingNumber() {
        achEntry.setReceivingDfiRoutingNumber(null);

        assertThrows(RtpMessageException.class, () -> 
            rtpMessageBuilderService.buildRtpMessage(achEntry, fileHeader, batchHeader)
        );
    }

    @Test
    @DisplayName("Should throw exception for missing account number")
    void testBuildRtpMessageMissingAccountNumber() {
        achEntry.setReceivingDfiAccountNumber(null);

        assertThrows(RtpMessageException.class, () -> 
            rtpMessageBuilderService.buildRtpMessage(achEntry, fileHeader, batchHeader)
        );
    }

    @Test
    @DisplayName("Should throw exception for invalid amount")
    void testBuildRtpMessageInvalidAmount() {
        achEntry.setAmount(BigDecimal.ZERO);

        assertThrows(RtpMessageException.class, () -> 
            rtpMessageBuilderService.buildRtpMessage(achEntry, fileHeader, batchHeader)
        );
    }

    @Test
    @DisplayName("Should throw exception for missing individual name")
    void testBuildRtpMessageMissingName() {
        achEntry.setIndividualName(null);

        assertThrows(RtpMessageException.class, () -> 
            rtpMessageBuilderService.buildRtpMessage(achEntry, fileHeader, batchHeader)
        );
    }

    @Test
    @DisplayName("Should throw exception for missing trace number")
    void testBuildRtpMessageMissingTraceNumber() {
        achEntry.setTraceNumber(null);

        assertThrows(RtpMessageException.class, () -> 
            rtpMessageBuilderService.buildRtpMessage(achEntry, fileHeader, batchHeader)
        );
    }

    @Test
    @DisplayName("Should escape XML special characters")
    void testXmlEscaping() {
        achEntry.setIndividualName("JOHN & JANE DOE <TEST>");

        String message = rtpMessageBuilderService.buildRtpMessage(achEntry, fileHeader, batchHeader);

        assertTrue(message.contains("JOHN &amp; JANE DOE &lt;TEST&gt;"));
    }

    @Test
    @DisplayName("Should include addenda information in remittance")
    void testBuildRtpMessageWithAddenda() {
        com.example.ach2rtp.model.ach.AchAddenda addenda = new com.example.ach2rtp.model.ach.AchAddenda();
        addenda.setPaymentRelatedInformation("Payment for invoice #12345");
        achEntry.addAddenda(addenda);

        String message = rtpMessageBuilderService.buildRtpMessage(achEntry, fileHeader, batchHeader);

        assertTrue(message.contains("RmtInf"));
        assertTrue(message.contains("Payment for invoice #12345"));
    }
}
