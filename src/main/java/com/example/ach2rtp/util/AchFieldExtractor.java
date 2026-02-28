package com.example.ach2rtp.util;

import com.example.ach2rtp.exception.AchParsingException;
import org.apache.commons.lang3.StringUtils;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

/**
 * Utility class for extracting and parsing fields from ACH records.
 * 
 * ACH records are fixed-width ASCII with specific field positions.
 */
public class AchFieldExtractor {

    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyMMdd");
    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("HHmm");

    /**
     * Extract a substring from the record at the specified position and length.
     * 
     * @param record The ACH record line
     * @param startPosition 1-based starting position
     * @param length Number of characters to extract
     * @return Extracted substring
     */
    public static String extractField(String record, int startPosition, int length) {
        if (record == null || record.length() < startPosition + length - 1) {
            throw new AchParsingException(
                    "Record too short to extract field at position " + startPosition + " with length " + length,
                    null,
                    -1,
                    record
            );
        }
        return record.substring(startPosition - 1, startPosition - 1 + length);
    }

    /**
     * Extract and trim a string field (left-justified, space-padded).
     * 
     * @param record The ACH record line
     * @param startPosition 1-based starting position
     * @param length Number of characters to extract
     * @return Trimmed string value
     */
    public static String extractStringField(String record, int startPosition, int length) {
        String value = extractField(record, startPosition, length);
        return value.trim();
    }

    /**
     * Extract a numeric field (right-justified, zero-padded).
     * 
     * @param record The ACH record line
     * @param startPosition 1-based starting position
     * @param length Number of characters to extract
     * @return Numeric value as Long
     */
    public static Long extractNumericField(String record, int startPosition, int length) {
        String value = extractField(record, startPosition, length);
        try {
            return Long.parseLong(value.trim());
        } catch (NumberFormatException e) {
            throw new AchParsingException(
                    "Invalid numeric field at position " + startPosition + ": " + value,
                    null,
                    -1,
                    record,
                    e
            );
        }
    }

    /**
     * Extract an amount field (in cents, right-justified, zero-padded).
     * 
     * @param record The ACH record line
     * @param startPosition 1-based starting position
     * @param length Number of characters to extract
     * @return Amount as BigDecimal (divided by 100 for cents)
     */
    public static BigDecimal extractAmountField(String record, int startPosition, int length) {
        Long cents = extractNumericField(record, startPosition, length);
        return BigDecimal.valueOf(cents).scaleByPowerOfTen(-2);
    }

    /**
     * Extract a date field in YYMMDD format.
     * 
     * @param record The ACH record line
     * @param startPosition 1-based starting position
     * @return LocalDate parsed from YYMMDD format
     */
    public static LocalDate extractDateField(String record, int startPosition) {
        String dateStr = extractField(record, startPosition, 6);
        try {
            return LocalDate.parse(dateStr, DATE_FORMATTER);
        } catch (Exception e) {
            throw new AchParsingException(
                    "Invalid date field at position " + startPosition + ": " + dateStr,
                    null,
                    -1,
                    record,
                    e
            );
        }
    }

    /**
     * Extract a time field in HHmm format.
     * 
     * @param record The ACH record line
     * @param startPosition 1-based starting position
     * @return LocalTime parsed from HHmm format
     */
    public static LocalTime extractTimeField(String record, int startPosition) {
        String timeStr = extractField(record, startPosition, 4);
        try {
            return LocalTime.parse(timeStr, TIME_FORMATTER);
        } catch (Exception e) {
            throw new AchParsingException(
                    "Invalid time field at position " + startPosition + ": " + timeStr,
                    null,
                    -1,
                    record,
                    e
            );
        }
    }

    /**
     * Validate that a field matches an expected value.
     * 
     * @param record The ACH record line
     * @param startPosition 1-based starting position
     * @param length Number of characters to validate
     * @param expectedValue Expected value
     * @throws AchParsingException if field doesn't match expected value
     */
    public static void validateField(String record, int startPosition, int length, String expectedValue) {
        String actualValue = extractField(record, startPosition, length);
        if (!actualValue.equals(expectedValue)) {
            throw new AchParsingException(
                    "Field validation failed at position " + startPosition + 
                    ": expected '" + expectedValue + "', got '" + actualValue + "'",
                    null,
                    -1,
                    record
            );
        }
    }

    /**
     * Check if a field is blank (all spaces).
     * 
     * @param record The ACH record line
     * @param startPosition 1-based starting position
     * @param length Number of characters to check
     * @return true if field is blank, false otherwise
     */
    public static boolean isFieldBlank(String record, int startPosition, int length) {
        String value = extractField(record, startPosition, length);
        return StringUtils.isBlank(value);
    }

    /**
     * Get the record type code (first character).
     * 
     * @param record The ACH record line
     * @return Record type code as String
     */
    public static String getRecordType(String record) {
        if (record == null || record.length() == 0) {
            throw new AchParsingException("Record is empty or null", null, -1, record);
        }
        return record.substring(0, 1);
    }
}
