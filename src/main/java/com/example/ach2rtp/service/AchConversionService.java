package com.example.ach2rtp.service;

import com.example.ach2rtp.exception.AchParsingException;
import com.example.ach2rtp.exception.RtpMessageException;
import com.example.ach2rtp.model.ach.*;
import com.example.ach2rtp.parser.AchFileParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

/**
 * Service for orchestrating ACH file conversion to RTP messages.
 * 
 * Coordinates parsing, validation, message building, and publishing.
 */
@Service
public class AchConversionService {

    private static final Logger logger = LoggerFactory.getLogger(AchConversionService.class);

    @Autowired
    private AchFileParser achFileParser;

    @Autowired
    private RtpMessageBuilderService rtpMessageBuilderService;

    @Autowired
    private MessagePublisherService messagePublisherService;

    /**
     * Convert an ACH file to RTP messages and publish them.
     * 
     * @param inputStream Input stream containing ACH file
     * @param fileName Name of the ACH file
     * @return Conversion result with statistics
     */
    public ConversionResult convertAndPublish(InputStream inputStream, String fileName) {
        logger.info("Starting conversion of ACH file: {}", fileName);
        
        ConversionResult result = new ConversionResult(fileName);
        
        try {
            // Parse ACH file
            AchFile achFile = achFileParser.parseFile(inputStream, fileName);
            result.setTotalEntries(achFile.getTotalEntries());
            logger.info("Parsed ACH file with {} batches and {} entries", 
                    achFile.getBatches().size(), achFile.getTotalEntries());
            
            // Process each batch
            for (AchBatch batch : achFile.getBatches()) {
                processBatch(achFile, batch, result);
            }
            
            result.setStatus("COMPLETED");
            logger.info("Conversion completed for file: {} - {} successful, {} failed",
                    fileName, result.getSuccessfulConversions(), result.getFailedConversions());
            
            return result;
            
        } catch (AchParsingException e) {
            logger.error("Error parsing ACH file: {}", e.getMessage(), e);
            result.setStatus("FAILED");
            result.setErrorMessage("Parsing error: " + e.getMessage());
            return result;
        } catch (Exception e) {
            logger.error("Unexpected error during conversion: {}", e.getMessage(), e);
            result.setStatus("FAILED");
            result.setErrorMessage("Unexpected error: " + e.getMessage());
            return result;
        }
    }

    private void processBatch(AchFile achFile, AchBatch batch, ConversionResult result) {
        logger.debug("Processing batch {} with {} entries", batch.getBatchNumber(), batch.getEntries().size());
        
        for (AchEntry entry : batch.getEntries()) {
            try {
                // Build RTP message
                String rtpMessage = rtpMessageBuilderService.buildRtpMessage(
                        entry,
                        achFile.getFileHeader(),
                        batch.getBatchHeader()
                );
                
                // Publish message
                messagePublisherService.publishMessage(rtpMessage, entry.getTraceNumber());
                
                result.incrementSuccessfulConversions();
                logger.debug("Successfully converted and published entry: {}", entry.getTraceNumber());
                
            } catch (RtpMessageException e) {
                logger.error("Error converting entry {}: {}", entry.getTraceNumber(), e.getMessage(), e);
                result.incrementFailedConversions();
                result.addError(entry.getTraceNumber(), e.getMessage());
            } catch (Exception e) {
                logger.error("Unexpected error processing entry {}: {}", entry.getTraceNumber(), e.getMessage(), e);
                result.incrementFailedConversions();
                result.addError(entry.getTraceNumber(), "Unexpected error: " + e.getMessage());
            }
        }
    }

    /**
     * Result object containing conversion statistics and errors.
     */
    public static class ConversionResult {
        private String fileName;
        private String status;
        private int totalEntries;
        private int successfulConversions;
        private int failedConversions;
        private String errorMessage;
        private List<EntryError> errors;

        public ConversionResult(String fileName) {
            this.fileName = fileName;
            this.status = "PROCESSING";
            this.successfulConversions = 0;
            this.failedConversions = 0;
            this.errors = new ArrayList<>();
        }

        public void incrementSuccessfulConversions() {
            this.successfulConversions++;
        }

        public void incrementFailedConversions() {
            this.failedConversions++;
        }

        public void addError(String entryId, String errorMessage) {
            this.errors.add(new EntryError(entryId, errorMessage));
        }

        // Getters
        public String getFileName() { return fileName; }
        public String getStatus() { return status; }
        public int getTotalEntries() { return totalEntries; }
        public int getSuccessfulConversions() { return successfulConversions; }
        public int getFailedConversions() { return failedConversions; }
        public String getErrorMessage() { return errorMessage; }
        public List<EntryError> getErrors() { return errors; }

        // Setters
        public void setStatus(String status) { this.status = status; }
        public void setTotalEntries(int totalEntries) { this.totalEntries = totalEntries; }
        public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    }

    /**
     * Entry-level error information.
     */
    public static class EntryError {
        private String entryId;
        private String errorMessage;

        public EntryError(String entryId, String errorMessage) {
            this.entryId = entryId;
            this.errorMessage = errorMessage;
        }

        public String getEntryId() { return entryId; }
        public String getErrorMessage() { return errorMessage; }
    }
}
