package com.example.ach2rtp.exception;

import java.util.ArrayList;
import java.util.List;

/**
 * Exception thrown when validation of ACH or RTP data fails.
 */
public class ValidationException extends RuntimeException {

    private final List<String> errors;
    private final String fieldName;

    public ValidationException(String message) {
        super(message);
        this.errors = new ArrayList<>();
        this.fieldName = null;
    }

    public ValidationException(String message, String fieldName) {
        super(message);
        this.errors = new ArrayList<>();
        this.fieldName = fieldName;
    }

    public ValidationException(String message, List<String> errors) {
        super(message);
        this.errors = errors != null ? errors : new ArrayList<>();
        this.fieldName = null;
    }

    public ValidationException(String message, List<String> errors, String fieldName) {
        super(message);
        this.errors = errors != null ? errors : new ArrayList<>();
        this.fieldName = fieldName;
    }

    public ValidationException(String message, Throwable cause) {
        super(message, cause);
        this.errors = new ArrayList<>();
        this.fieldName = null;
    }

    public List<String> getErrors() {
        return errors;
    }

    public String getFieldName() {
        return fieldName;
    }

    public void addError(String error) {
        this.errors.add(error);
    }

    @Override
    public String toString() {
        return "ValidationException{" +
                "message='" + getMessage() + '\'' +
                ", fieldName='" + fieldName + '\'' +
                ", errors=" + errors +
                '}';
    }
}
