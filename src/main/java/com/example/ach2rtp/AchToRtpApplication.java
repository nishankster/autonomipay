package com.example.ach2rtp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Main Spring Boot application class for ACH to RTP conversion service.
 * 
 * This microservice converts NACHA ACH files to ISO 20022 RTP (pacs.008) messages
 * and publishes them asynchronously to an RTP gateway via message queue.
 */
@SpringBootApplication
@EnableAsync
public class AchToRtpApplication {

    public static void main(String[] args) {
        SpringApplication.run(AchToRtpApplication.class, args);
    }
}
