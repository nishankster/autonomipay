package com.example.ach2rtp.controller;

import com.example.ach2rtp.exception.AchParsingException;
import com.example.ach2rtp.exception.PublishingException;
import com.example.ach2rtp.exception.RtpMessageException;
import com.example.ach2rtp.exception.ValidationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import java.util.HashMap;
import java.util.Map;

/**
 * Global exception handler for REST API error responses.
 */
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /**
     * Handle ACH parsing exceptions.
     */
    @ExceptionHandler(AchParsingException.class)
    public ResponseEntity<?> handleAchParsingException(AchParsingException e) {
        logger.error("ACH parsing error: {}", e.getMessage(), e);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "ERROR");
        response.put("errorType", "ACH_PARSING_ERROR");
        response.put("message", e.getMessage());
        response.put("recordType", e.getRecordType());
        response.put("lineNumber", e.getLineNumber());
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handle RTP message generation exceptions.
     */
    @ExceptionHandler(RtpMessageException.class)
    public ResponseEntity<?> handleRtpMessageException(RtpMessageException e) {
        logger.error("RTP message error: {}", e.getMessage(), e);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "ERROR");
        response.put("errorType", "RTP_MESSAGE_ERROR");
        response.put("message", e.getMessage());
        response.put("messageId", e.getMessageId());
        response.put("validationError", e.getValidationError());
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }

    /**
     * Handle message publishing exceptions.
     */
    @ExceptionHandler(PublishingException.class)
    public ResponseEntity<?> handlePublishingException(PublishingException e) {
        logger.error("Publishing error: {}", e.getMessage(), e);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "ERROR");
        response.put("errorType", "PUBLISHING_ERROR");
        response.put("message", e.getMessage());
        response.put("messageId", e.getMessageId());
        response.put("retryable", e.isRetryable());
        response.put("retryAttempt", e.getRetryAttempt());
        response.put("timestamp", System.currentTimeMillis());
        
        HttpStatus status = e.isRetryable() ? HttpStatus.SERVICE_UNAVAILABLE : HttpStatus.BAD_REQUEST;
        return ResponseEntity.status(status).body(response);
    }

    /**
     * Handle validation exceptions.
     */
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<?> handleValidationException(ValidationException e) {
        logger.error("Validation error: {}", e.getMessage(), e);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "ERROR");
        response.put("errorType", "VALIDATION_ERROR");
        response.put("message", e.getMessage());
        response.put("fieldName", e.getFieldName());
        response.put("errors", e.getErrors());
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handle file upload size exceeded exceptions.
     */
    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<?> handleMaxUploadSizeExceededException(MaxUploadSizeExceededException e) {
        logger.error("File upload size exceeded: {}", e.getMessage());
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "ERROR");
        response.put("errorType", "FILE_SIZE_EXCEEDED");
        response.put("message", "Uploaded file exceeds maximum allowed size");
        response.put("maxSize", "10 MB");
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE).body(response);
    }

    /**
     * Handle generic exceptions.
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<?> handleGenericException(Exception e) {
        logger.error("Unexpected error: {}", e.getMessage(), e);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "ERROR");
        response.put("errorType", "INTERNAL_SERVER_ERROR");
        response.put("message", "An unexpected error occurred");
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }
}
