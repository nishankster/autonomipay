package com.example.ach2rtp.monitoring;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

/**
 * Audit logger for recording compliance and security-relevant events.
 */
@Component
public class AuditLogger {

    private static final Logger auditLogger = LoggerFactory.getLogger("AUDIT");
    private static final DateTimeFormatter TIMESTAMP_FORMATTER = 
            DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss'Z'");
    private static final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Log a file upload event.
     */
    public void logFileUpload(String fileName, long fileSize, String uploadedBy) {
        Map<String, Object> event = createBaseEvent("FILE_UPLOADED");
        event.put("fileName", fileName);
        event.put("fileSize", fileSize);
        event.put("uploadedBy", uploadedBy);
        logEvent(event);
    }

    /**
     * Log a file parsing event.
     */
    public void logFileParsing(String fileName, int batchCount, int entryCount, boolean success) {
        Map<String, Object> event = createBaseEvent("FILE_PARSING");
        event.put("fileName", fileName);
        event.put("batchCount", batchCount);
        event.put("entryCount", entryCount);
        event.put("success", success);
        logEvent(event);
    }

    /**
     * Log a message generation event.
     */
    public void logMessageGeneration(String entryId, String messageId, boolean success, String errorMessage) {
        Map<String, Object> event = createBaseEvent("MESSAGE_GENERATION");
        event.put("entryId", entryId);
        event.put("messageId", messageId);
        event.put("success", success);
        if (errorMessage != null) {
            event.put("errorMessage", errorMessage);
        }
        logEvent(event);
    }

    /**
     * Log a message publishing event.
     */
    public void logMessagePublishing(String messageId, boolean success, String errorMessage) {
        Map<String, Object> event = createBaseEvent("MESSAGE_PUBLISHING");
        event.put("messageId", messageId);
        event.put("success", success);
        if (errorMessage != null) {
            event.put("errorMessage", errorMessage);
        }
        logEvent(event);
    }

    /**
     * Log an error event.
     */
    public void logError(String errorType, String errorMessage, String context) {
        Map<String, Object> event = createBaseEvent("ERROR");
        event.put("errorType", errorType);
        event.put("errorMessage", errorMessage);
        event.put("context", context);
        logEvent(event);
    }

    /**
     * Log a security event.
     */
    public void logSecurityEvent(String eventType, String details) {
        Map<String, Object> event = createBaseEvent("SECURITY_EVENT");
        event.put("eventType", eventType);
        event.put("details", details);
        logEvent(event);
    }

    /**
     * Create a base event map with common fields.
     */
    private Map<String, Object> createBaseEvent(String eventType) {
        Map<String, Object> event = new HashMap<>();
        event.put("timestamp", LocalDateTime.now().format(TIMESTAMP_FORMATTER));
        event.put("eventType", eventType);
        event.put("severity", "INFO");
        return event;
    }

    /**
     * Log the event as JSON.
     */
    private void logEvent(Map<String, Object> event) {
        try {
            String jsonEvent = objectMapper.writeValueAsString(event);
            auditLogger.info(jsonEvent);
        } catch (Exception e) {
            auditLogger.error("Error serializing audit event: {}", e.getMessage());
        }
    }
}
