package com.example.ach2rtp.service;

import com.example.ach2rtp.exception.PublishingException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.core.AmqpTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * Service for publishing RTP messages to message queue.
 * 
 * Handles asynchronous message delivery to RTP gateway.
 */
@Service
public class MessagePublisherService {

    private static final Logger logger = LoggerFactory.getLogger(MessagePublisherService.class);

    @Autowired
    private AmqpTemplate amqpTemplate;

    @Value("${mq.exchange-name:rtp-gateway}")
    private String exchangeName;

    @Value("${mq.routing-key:rtp.credit.transfer}")
    private String routingKey;

    /**
     * Publish an RTP message to the message queue.
     * 
     * @param message The RTP XML message
     * @param messageId Unique message identifier
     * @throws PublishingException if publishing fails
     */
    public void publishMessage(String message, String messageId) throws PublishingException {
        try {
            logger.debug("Publishing RTP message {} to exchange: {}, routing key: {}", 
                    messageId, exchangeName, routingKey);
            
            amqpTemplate.convertAndSend(exchangeName, routingKey, message, msg -> {
                msg.getMessageProperties().setHeader("X-Message-Id", messageId);
                msg.getMessageProperties().setHeader("X-Timestamp", System.currentTimeMillis());
                msg.getMessageProperties().setContentType("application/xml");
                return msg;
            });
            
            logger.info("Successfully published RTP message: {}", messageId);
            
        } catch (Exception e) {
            logger.error("Error publishing RTP message {}: {}", messageId, e.getMessage(), e);
            throw new PublishingException(
                    "Failed to publish RTP message",
                    messageId,
                    1,
                    isRetryable(e),
                    e
            );
        }
    }

    /**
     * Determine if an exception represents a retryable error.
     * 
     * @param exception The exception to evaluate
     * @return true if the error is retryable, false otherwise
     */
    private boolean isRetryable(Exception exception) {
        String message = exception.getMessage();
        if (message == null) {
            return false;
        }
        
        // Connection errors are retryable
        if (message.contains("Connection refused") || 
            message.contains("Connection timeout") ||
            message.contains("Connection reset")) {
            return true;
        }
        
        // Authentication errors are not retryable
        if (message.contains("Authentication") || message.contains("Unauthorized")) {
            return false;
        }
        
        // Default to retryable for unknown errors
        return true;
    }
}
