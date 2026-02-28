package com.example.ach2rtp.util;

import com.example.ach2rtp.exception.AchParsingException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalTime;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("ACH Field Extractor Tests")
class AchFieldExtractorTest {

    private static final String SAMPLE_RECORD = 
            "101 094101041234567890210101011234567890000000000000000000000000000000000000000000000000000000000000";

    @Test
    @DisplayName("Should extract string field correctly")
    void testExtractStringField() {
        String result = AchFieldExtractor.extractStringField(SAMPLE_RECORD, 1, 1);
        assertEquals("1", result);
    }

    @Test
    @DisplayName("Should extract numeric field correctly")
    void testExtractNumericField() {
        Long result = AchFieldExtractor.extractNumericField(SAMPLE_RECORD, 2, 2);
        assertEquals(1L, result);
    }

    @Test
    @DisplayName("Should extract amount field correctly")
    void testExtractAmountField() {
        String amountRecord = "123456789012345678901234567890000000000000000000001000000000000000000000000000000000000000000000";
        BigDecimal result = AchFieldExtractor.extractAmountField(amountRecord, 81, 10);
        assertEquals(new BigDecimal("100.00"), result);
    }

    @Test
    @DisplayName("Should extract date field correctly")
    void testExtractDateField() {
        String dateRecord = "101 094101041234567890240101011234567890000000000000000000000000000000000000000000000000000000000000";
        LocalDate result = AchFieldExtractor.extractDateField(dateRecord, 16);
        assertEquals(LocalDate.of(2024, 1, 1), result);
    }

    @Test
    @DisplayName("Should extract time field correctly")
    void testExtractTimeField() {
        String timeRecord = "101 094101041234567890240101011234567890000000000000000000000000000000000000000000000000000000000000";
        LocalTime result = AchFieldExtractor.extractTimeField(timeRecord, 22);
        assertEquals(LocalTime.of(1, 1), result);
    }

    @Test
    @DisplayName("Should throw exception for invalid numeric field")
    void testExtractNumericFieldInvalid() {
        String invalidRecord = "101 ABC101041234567890240101011234567890000000000000000000000000000000000000000000000000000000000000";
        assertThrows(AchParsingException.class, () -> 
            AchFieldExtractor.extractNumericField(invalidRecord, 5, 3)
        );
    }

    @Test
    @DisplayName("Should throw exception for invalid date field")
    void testExtractDateFieldInvalid() {
        String invalidRecord = "101 094101041234567890991301011234567890000000000000000000000000000000000000000000000000000000000000";
        assertThrows(AchParsingException.class, () -> 
            AchFieldExtractor.extractDateField(invalidRecord, 16)
        );
    }

    @Test
    @DisplayName("Should validate field correctly")
    void testValidateField() {
        assertDoesNotThrow(() -> 
            AchFieldExtractor.validateField(SAMPLE_RECORD, 1, 1, "1")
        );
    }

    @Test
    @DisplayName("Should throw exception for field validation failure")
    void testValidateFieldFailure() {
        assertThrows(AchParsingException.class, () -> 
            AchFieldExtractor.validateField(SAMPLE_RECORD, 1, 1, "9")
        );
    }

    @Test
    @DisplayName("Should detect blank field correctly")
    void testIsFieldBlank() {
        String blankRecord = "                                                                                                    ";
        assertTrue(AchFieldExtractor.isFieldBlank(blankRecord, 1, 94));
    }

    @Test
    @DisplayName("Should get record type correctly")
    void testGetRecordType() {
        String result = AchFieldExtractor.getRecordType(SAMPLE_RECORD);
        assertEquals("1", result);
    }

    @Test
    @DisplayName("Should throw exception for null record")
    void testGetRecordTypeNull() {
        assertThrows(AchParsingException.class, () -> 
            AchFieldExtractor.getRecordType(null)
        );
    }

    @Test
    @DisplayName("Should throw exception for empty record")
    void testGetRecordTypeEmpty() {
        assertThrows(AchParsingException.class, () -> 
            AchFieldExtractor.getRecordType("")
        );
    }

    @Test
    @DisplayName("Should throw exception for record too short")
    void testExtractFieldTooShort() {
        assertThrows(AchParsingException.class, () -> 
            AchFieldExtractor.extractField("123", 1, 10)
        );
    }
}
