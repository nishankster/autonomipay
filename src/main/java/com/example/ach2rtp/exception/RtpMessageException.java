package com.example.ach2rtp.exception;

/**
 * Exception thrown when RTP message generation or validation fails.
 */
public class RtpMessageException extends RuntimeException {

    private final String messageId;
    private final String validationError;

    public RtpMessageException(String message) {
        super(message);
        this.messageId = null;
        this.validationError = null;
    }

    public RtpMessageException(String message, Throwable cause) {
        super(message, cause);
        this.messageId = null;
        this.validationError = null;
    }

    public RtpMessageException(String message, String messageId, String validationError) {
        super(message);
        this.messageId = messageId;
        this.validationError = validationError;
    }

    public RtpMessageException(String message, String messageId, String validationError, Throwable cause) {
        super(message, cause);
        this.messageId = messageId;
        this.validationError = validationError;
    }

    public String getMessageId() {
        return messageId;
    }

    public String getValidationError() {
        return validationError;
    }

    @Override
    public String toString() {
        return "RtpMessageException{" +
                "message='" + getMessage() + '\'' +
                ", messageId='" + messageId + '\'' +
                ", validationError='" + validationError + '\'' +
                '}';
    }
}
