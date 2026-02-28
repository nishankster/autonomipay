package com.example.ach2rtp.parser;

import com.example.ach2rtp.exception.AchParsingException;
import com.example.ach2rtp.model.ach.*;
import com.example.ach2rtp.util.AchFieldExtractor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

/**
 * Parser for NACHA ACH files.
 * 
 * Reads fixed-width ACH records and converts them into domain objects.
 */
@Component
public class AchFileParser {

    private static final Logger logger = LoggerFactory.getLogger(AchFileParser.class);
    private static final int EXPECTED_RECORD_LENGTH = 94;
    private static final String RECORD_TYPE_FILE_HEADER = "1";
    private static final String RECORD_TYPE_BATCH_HEADER = "5";
    private static final String RECORD_TYPE_ENTRY_DETAIL = "6";
    private static final String RECORD_TYPE_ADDENDA = "7";
    private static final String RECORD_TYPE_BATCH_CONTROL = "8";
    private static final String RECORD_TYPE_FILE_CONTROL = "9";
    private static final String RECORD_TYPE_PADDING = "9";

    /**
     * Parse an ACH file from an input stream.
     * 
     * @param inputStream Input stream containing ACH file content
     * @param fileName Name of the file being parsed
     * @return Parsed AchFile object
     * @throws AchParsingException if parsing fails
     */
    public AchFile parseFile(InputStream inputStream, String fileName) throws AchParsingException {
        logger.info("Starting to parse ACH file: {}", fileName);
        
        AchFile achFile = new AchFile(null, fileName);
        List<String> records = readRecords(inputStream);
        
        int lineNumber = 0;
        AchBatch currentBatch = null;
        
        try {
            for (String record : records) {
                lineNumber++;
                
                if (record.length() != EXPECTED_RECORD_LENGTH) {
                    logger.warn("Record {} has unexpected length: {} (expected {})", 
                            lineNumber, record.length(), EXPECTED_RECORD_LENGTH);
                }
                
                String recordType = AchFieldExtractor.getRecordType(record);
                
                switch (recordType) {
                    case RECORD_TYPE_FILE_HEADER:
                        achFile.setFileHeader(parseFileHeader(record, lineNumber));
                        logger.debug("Parsed file header at line {}", lineNumber);
                        break;
                        
                    case RECORD_TYPE_BATCH_HEADER:
                        currentBatch = new AchBatch(achFile.getBatches().size() + 1);
                        currentBatch.setBatchHeader(parseBatchHeader(record, lineNumber));
                        achFile.addBatch(currentBatch);
                        logger.debug("Parsed batch header at line {}", lineNumber);
                        break;
                        
                    case RECORD_TYPE_ENTRY_DETAIL:
                        if (currentBatch == null) {
                            throw new AchParsingException(
                                    "Entry detail record found without batch header",
                                    RECORD_TYPE_ENTRY_DETAIL,
                                    lineNumber,
                                    record
                            );
                        }
                        AchEntry entry = parseEntryDetail(record, lineNumber);
                        currentBatch.addEntry(entry);
                        logger.debug("Parsed entry detail at line {}", lineNumber);
                        break;
                        
                    case RECORD_TYPE_ADDENDA:
                        if (currentBatch == null || currentBatch.getEntries().isEmpty()) {
                            throw new AchParsingException(
                                    "Addenda record found without entry detail",
                                    RECORD_TYPE_ADDENDA,
                                    lineNumber,
                                    record
                            );
                        }
                        AchAddenda addenda = parseAddenda(record, lineNumber);
                        currentBatch.getEntries().get(currentBatch.getEntries().size() - 1).addAddenda(addenda);
                        logger.debug("Parsed addenda record at line {}", lineNumber);
                        break;
                        
                    case RECORD_TYPE_BATCH_CONTROL:
                        if (currentBatch == null) {
                            throw new AchParsingException(
                                    "Batch control record found without batch header",
                                    RECORD_TYPE_BATCH_CONTROL,
                                    lineNumber,
                                    record
                            );
                        }
                        currentBatch.setBatchControl(parseBatchControl(record, lineNumber));
                        logger.debug("Parsed batch control at line {}", lineNumber);
                        break;
                        
                    case RECORD_TYPE_FILE_CONTROL:
                        achFile.setFileControl(parseFileControl(record, lineNumber));
                        logger.debug("Parsed file control at line {}", lineNumber);
                        break;
                        
                    case RECORD_TYPE_PADDING:
                        // Skip padding records (all 9s)
                        logger.debug("Skipped padding record at line {}", lineNumber);
                        break;
                        
                    default:
                        logger.warn("Unknown record type {} at line {}", recordType, lineNumber);
                }
            }
            
            logger.info("Successfully parsed ACH file: {} with {} batches and {} total entries",
                    fileName, achFile.getBatches().size(), achFile.getTotalEntries());
            
            return achFile;
            
        } catch (AchParsingException e) {
            logger.error("Error parsing ACH file at line {}: {}", lineNumber, e.getMessage(), e);
            throw e;
        } catch (Exception e) {
            logger.error("Unexpected error parsing ACH file at line {}: {}", lineNumber, e.getMessage(), e);
            throw new AchParsingException("Unexpected parsing error at line " + lineNumber, e);
        }
    }

    private List<String> readRecords(InputStream inputStream) throws AchParsingException {
        List<String> records = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            String line;
            while ((line = reader.readLine()) != null) {
                records.add(line);
            }
        } catch (IOException e) {
            throw new AchParsingException("Error reading ACH file", e);
        }
        return records;
    }

    private AchFileHeader parseFileHeader(String record, int lineNumber) {
        AchFileHeader header = new AchFileHeader();
        header.setRecordTypeCode(AchFieldExtractor.extractStringField(record, 1, 1));
        header.setPriorityCode(AchFieldExtractor.extractStringField(record, 2, 2));
        header.setImmediateDestination(AchFieldExtractor.extractStringField(record, 4, 10));
        header.setImmediateOrigin(AchFieldExtractor.extractStringField(record, 14, 10));
        header.setFileCreationDate(AchFieldExtractor.extractDateField(record, 24));
        header.setFileCreationTime(AchFieldExtractor.extractTimeField(record, 30));
        header.setFileIdModifier(AchFieldExtractor.extractStringField(record, 34, 1));
        header.setRecordSize(AchFieldExtractor.extractStringField(record, 35, 3));
        header.setBlockingFactor(AchFieldExtractor.extractStringField(record, 38, 2));
        header.setFormatCode(AchFieldExtractor.extractStringField(record, 40, 1));
        header.setImmediateDestinationName(AchFieldExtractor.extractStringField(record, 41, 23));
        header.setImmediateOriginName(AchFieldExtractor.extractStringField(record, 64, 23));
        header.setReferenceCode(AchFieldExtractor.extractStringField(record, 87, 8));
        return header;
    }

    private AchBatchHeader parseBatchHeader(String record, int lineNumber) {
        AchBatchHeader header = new AchBatchHeader();
        header.setRecordTypeCode(AchFieldExtractor.extractStringField(record, 1, 1));
        header.setServiceClassCode(AchFieldExtractor.extractStringField(record, 2, 3));
        header.setCompanyName(AchFieldExtractor.extractStringField(record, 5, 16));
        header.setCompanyDiscretionaryData(AchFieldExtractor.extractStringField(record, 21, 20));
        header.setCompanyIdentificationNumber(AchFieldExtractor.extractStringField(record, 41, 10));
        header.setStandardEntryClassCode(AchFieldExtractor.extractStringField(record, 51, 3));
        header.setCompanyEntryDescription(AchFieldExtractor.extractStringField(record, 54, 10));
        header.setCompanyDescriptiveDate(AchFieldExtractor.extractDateField(record, 64));
        header.setEffectiveDate(AchFieldExtractor.extractDateField(record, 70));
        header.setSettlementDate(AchFieldExtractor.extractStringField(record, 76, 3));
        header.setOriginatorStatusCode(AchFieldExtractor.extractStringField(record, 79, 1));
        header.setOriginatingDfiIdentification(AchFieldExtractor.extractStringField(record, 80, 8));
        header.setBatchNumber(AchFieldExtractor.extractStringField(record, 88, 7));
        return header;
    }

    private AchEntry parseEntryDetail(String record, int lineNumber) {
        AchEntry entry = new AchEntry();
        entry.setRecordTypeCode(AchFieldExtractor.extractStringField(record, 1, 1));
        entry.setTransactionCode(AchFieldExtractor.extractStringField(record, 2, 2));
        entry.setReceivingDfiRoutingNumber(AchFieldExtractor.extractStringField(record, 4, 8));
        entry.setReceivingDfiAccountNumber(AchFieldExtractor.extractStringField(record, 12, 17));
        entry.setAmount(AchFieldExtractor.extractAmountField(record, 29, 10));
        entry.setIndividualIdentificationNumber(AchFieldExtractor.extractStringField(record, 39, 15));
        entry.setIndividualName(AchFieldExtractor.extractStringField(record, 54, 22));
        entry.setDiscretionaryData(AchFieldExtractor.extractStringField(record, 76, 2));
        entry.setAddendaRecordIndicator(AchFieldExtractor.extractStringField(record, 78, 1));
        entry.setTraceNumber(AchFieldExtractor.extractStringField(record, 79, 15));
        return entry;
    }

    private AchAddenda parseAddenda(String record, int lineNumber) {
        AchAddenda addenda = new AchAddenda();
        addenda.setRecordTypeCode(AchFieldExtractor.extractStringField(record, 1, 1));
        addenda.setAddendaTypeCode(AchFieldExtractor.extractStringField(record, 2, 2));
        addenda.setPaymentRelatedInformation(AchFieldExtractor.extractStringField(record, 4, 80));
        addenda.setAddendaSequenceNumber(AchFieldExtractor.extractStringField(record, 84, 4));
        addenda.setEntryDetailSequenceNumber(AchFieldExtractor.extractStringField(record, 88, 7));
        return addenda;
    }

    private AchBatchControl parseBatchControl(String record, int lineNumber) {
        AchBatchControl control = new AchBatchControl();
        control.setRecordTypeCode(AchFieldExtractor.extractStringField(record, 1, 1));
        control.setServiceClassCode(AchFieldExtractor.extractStringField(record, 2, 3));
        control.setEntryAddendaCount((int) (long) AchFieldExtractor.extractNumericField(record, 5, 6));
        control.setEntryHash(AchFieldExtractor.extractStringField(record, 11, 10));
        control.setTotalDebitAmount(AchFieldExtractor.extractAmountField(record, 21, 12));
        control.setTotalCreditAmount(AchFieldExtractor.extractAmountField(record, 33, 12));
        control.setCompanyIdentificationNumber(AchFieldExtractor.extractStringField(record, 45, 10));
        control.setMessageAuthenticationCode(AchFieldExtractor.extractStringField(record, 55, 19));
        control.setReserved(AchFieldExtractor.extractStringField(record, 74, 6));
        control.setOriginatingDfiIdentification(AchFieldExtractor.extractStringField(record, 80, 8));
        control.setBatchNumber(AchFieldExtractor.extractStringField(record, 88, 7));
        return control;
    }

    private AchFileControl parseFileControl(String record, int lineNumber) {
        AchFileControl control = new AchFileControl();
        control.setRecordTypeCode(AchFieldExtractor.extractStringField(record, 1, 1));
        control.setBatchCount((int) (long) AchFieldExtractor.extractNumericField(record, 2, 6));
        control.setBlockCount((int) (long) AchFieldExtractor.extractNumericField(record, 8, 6));
        control.setEntryAddendaCount((int) (long) AchFieldExtractor.extractNumericField(record, 14, 8));
        control.setEntryHash(AchFieldExtractor.extractStringField(record, 22, 10));
        control.setTotalDebitAmount(AchFieldExtractor.extractAmountField(record, 32, 12));
        control.setTotalCreditAmount(AchFieldExtractor.extractAmountField(record, 44, 12));
        control.setReserved(AchFieldExtractor.extractStringField(record, 56, 39));
        return control;
    }
}
