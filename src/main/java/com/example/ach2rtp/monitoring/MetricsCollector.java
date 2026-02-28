package com.example.ach2rtp.monitoring;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * Collects and records application metrics for monitoring and observability.
 */
@Component
public class MetricsCollector {

    private final MeterRegistry meterRegistry;

    // Counters
    private final Counter fileUploadCounter;
    private final Counter fileUploadErrorCounter;
    private final Counter achEntriesProcessedCounter;
    private final Counter achEntriesFailedCounter;
    private final Counter rtpMessagesGeneratedCounter;
    private final Counter rtpMessagesPublishedCounter;
    private final Counter rtpMessagesPublishFailedCounter;

    // Timers
    private final Timer fileParsingTimer;
    private final Timer messageGenerationTimer;
    private final Timer messagePublishingTimer;

    @Autowired
    public MetricsCollector(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;

        // Initialize counters
        this.fileUploadCounter = Counter.builder("ach.file.uploads.total")
                .description("Total number of ACH file uploads")
                .register(meterRegistry);

        this.fileUploadErrorCounter = Counter.builder("ach.file.uploads.errors.total")
                .description("Total number of ACH file upload errors")
                .register(meterRegistry);

        this.achEntriesProcessedCounter = Counter.builder("ach.entries.processed.total")
                .description("Total number of ACH entries processed")
                .register(meterRegistry);

        this.achEntriesFailedCounter = Counter.builder("ach.entries.failed.total")
                .description("Total number of ACH entries that failed processing")
                .register(meterRegistry);

        this.rtpMessagesGeneratedCounter = Counter.builder("rtp.messages.generated.total")
                .description("Total number of RTP messages generated")
                .register(meterRegistry);

        this.rtpMessagesPublishedCounter = Counter.builder("rtp.messages.published.total")
                .description("Total number of RTP messages published")
                .register(meterRegistry);

        this.rtpMessagesPublishFailedCounter = Counter.builder("rtp.messages.publish.failed.total")
                .description("Total number of RTP message publish failures")
                .register(meterRegistry);

        // Initialize timers
        this.fileParsingTimer = Timer.builder("ach.file.parsing.duration")
                .description("Time taken to parse ACH files")
                .publishPercentiles(0.5, 0.95, 0.99)
                .register(meterRegistry);

        this.messageGenerationTimer = Timer.builder("rtp.message.generation.duration")
                .description("Time taken to generate RTP messages")
                .publishPercentiles(0.5, 0.95, 0.99)
                .register(meterRegistry);

        this.messagePublishingTimer = Timer.builder("rtp.message.publishing.duration")
                .description("Time taken to publish RTP messages")
                .publishPercentiles(0.5, 0.95, 0.99)
                .register(meterRegistry);
    }

    // Counter methods
    public void incrementFileUploads() {
        fileUploadCounter.increment();
    }

    public void incrementFileUploadErrors() {
        fileUploadErrorCounter.increment();
    }

    public void incrementAchEntriesProcessed(int count) {
        achEntriesProcessedCounter.increment(count);
    }

    public void incrementAchEntriesFailed(int count) {
        achEntriesFailedCounter.increment(count);
    }

    public void incrementRtpMessagesGenerated(int count) {
        rtpMessagesGeneratedCounter.increment(count);
    }

    public void incrementRtpMessagesPublished(int count) {
        rtpMessagesPublishedCounter.increment(count);
    }

    public void incrementRtpMessagesPublishFailed(int count) {
        rtpMessagesPublishFailedCounter.increment(count);
    }

    // Timer methods
    public Timer.Sample startFileParsingTimer() {
        return Timer.start(meterRegistry);
    }

    public void recordFileParsingTime(Timer.Sample sample) {
        sample.stop(fileParsingTimer);
    }

    public Timer.Sample startMessageGenerationTimer() {
        return Timer.start(meterRegistry);
    }

    public void recordMessageGenerationTime(Timer.Sample sample) {
        sample.stop(messageGenerationTimer);
    }

    public Timer.Sample startMessagePublishingTimer() {
        return Timer.start(meterRegistry);
    }

    public void recordMessagePublishingTime(Timer.Sample sample) {
        sample.stop(messagePublishingTimer);
    }
}
