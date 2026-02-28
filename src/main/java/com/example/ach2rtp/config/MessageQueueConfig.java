package com.example.ach2rtp.config;

import org.springframework.amqp.core.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration for RabbitMQ message queue.
 */
@Configuration
public class MessageQueueConfig {

    @Value("${mq.exchange-name:rtp-gateway}")
    private String exchangeName;

    @Value("${mq.routing-key:rtp.credit.transfer}")
    private String routingKey;

    @Value("${mq.dead-letter-queue-enabled:true}")
    private boolean deadLetterQueueEnabled;

    /**
     * Declare the main exchange for RTP messages.
     */
    @Bean
    public TopicExchange rtpExchange() {
        return new TopicExchange(exchangeName, true, false);
    }

    /**
     * Declare the main queue for RTP messages.
     */
    @Bean
    public Queue rtpQueue() {
        if (deadLetterQueueEnabled) {
            return QueueBuilder.durable("rtp-queue")
                    .withArgument("x-dead-letter-exchange", "rtp-dlx")
                    .withArgument("x-dead-letter-routing-key", "rtp.dlq")
                    .build();
        } else {
            return QueueBuilder.durable("rtp-queue").build();
        }
    }

    /**
     * Bind the queue to the exchange with the routing key.
     */
    @Bean
    public Binding rtpBinding(Queue rtpQueue, TopicExchange rtpExchange) {
        return BindingBuilder.bind(rtpQueue)
                .to(rtpExchange)
                .with(routingKey);
    }

    /**
     * Declare the dead-letter exchange (optional).
     */
    @Bean
    public TopicExchange deadLetterExchange() {
        if (deadLetterQueueEnabled) {
            return new TopicExchange("rtp-dlx", true, false);
        }
        return null;
    }

    /**
     * Declare the dead-letter queue (optional).
     */
    @Bean
    public Queue deadLetterQueue() {
        if (deadLetterQueueEnabled) {
            return QueueBuilder.durable("rtp-dlq").build();
        }
        return null;
    }

    /**
     * Bind the dead-letter queue to the dead-letter exchange (optional).
     */
    @Bean
    public Binding deadLetterBinding() {
        if (deadLetterQueueEnabled) {
            return BindingBuilder.bind(deadLetterQueue())
                    .to(deadLetterExchange())
                    .with("rtp.dlq");
        }
        return null;
    }
}
