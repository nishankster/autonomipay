package com.example.ach2rtp.exception;

/**
 * Exception thrown when ACH file parsing fails.
 */
public class AchParsingException extends RuntimeException {

    private final String recordType;
    private final int lineNumber;
    private final String recordContent;

    public AchParsingException(String message) {
        super(message);
        this.recordType = null;
        this.lineNumber = -1;
        this.recordContent = null;
    }

    public AchParsingException(String message, Throwable cause) {
        super(message, cause);
        this.recordType = null;
        this.lineNumber = -1;
        this.recordContent = null;
    }

    public AchParsingException(String message, String recordType, int lineNumber, String recordContent) {
        super(message);
        this.recordType = recordType;
        this.lineNumber = lineNumber;
        this.recordContent = recordContent;
    }

    public AchParsingException(String message, String recordType, int lineNumber, String recordContent, Throwable cause) {
        super(message, cause);
        this.recordType = recordType;
        this.lineNumber = lineNumber;
        this.recordContent = recordContent;
    }

    public String getRecordType() {
        return recordType;
    }

    public int getLineNumber() {
        return lineNumber;
    }

    public String getRecordContent() {
        return recordContent;
    }

    @Override
    public String toString() {
        return "AchParsingException{" +
                "message='" + getMessage() + '\'' +
                ", recordType='" + recordType + '\'' +
                ", lineNumber=" + lineNumber +
                ", recordContent='" + recordContent + '\'' +
                '}';
    }
}
