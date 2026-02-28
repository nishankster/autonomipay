package com.example.ach2rtp.exception;

/**
 * Exception thrown when message publishing to queue fails.
 */
public class PublishingException extends RuntimeException {

    private final String messageId;
    private final int retryAttempt;
    private final boolean retryable;

    public PublishingException(String message) {
        super(message);
        this.messageId = null;
        this.retryAttempt = 0;
        this.retryable = false;
    }

    public PublishingException(String message, Throwable cause) {
        super(message, cause);
        this.messageId = null;
        this.retryAttempt = 0;
        this.retryable = false;
    }

    public PublishingException(String message, String messageId, int retryAttempt, boolean retryable) {
        super(message);
        this.messageId = messageId;
        this.retryAttempt = retryAttempt;
        this.retryable = retryable;
    }

    public PublishingException(String message, String messageId, int retryAttempt, boolean retryable, Throwable cause) {
        super(message, cause);
        this.messageId = messageId;
        this.retryAttempt = retryAttempt;
        this.retryable = retryable;
    }

    public String getMessageId() {
        return messageId;
    }

    public int getRetryAttempt() {
        return retryAttempt;
    }

    public boolean isRetryable() {
        return retryable;
    }

    @Override
    public String toString() {
        return "PublishingException{" +
                "message='" + getMessage() + '\'' +
                ", messageId='" + messageId + '\'' +
                ", retryAttempt=" + retryAttempt +
                ", retryable=" + retryable +
                '}';
    }
}
