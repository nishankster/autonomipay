package com.example.ach2rtp.model.ach;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Domain model representing a complete ACH file.
 * 
 * An ACH file contains a file header, one or more batches, and a file control record.
 */
public class AchFile {

    private String fileId;
    private AchFileHeader fileHeader;
    private List<AchBatch> batches;
    private AchFileControl fileControl;
    private LocalDateTime parsedAt;
    private String fileName;
    private long fileSizeBytes;

    public AchFile() {
        this.batches = new ArrayList<>();
    }

    public AchFile(String fileId, String fileName) {
        this.fileId = fileId;
        this.fileName = fileName;
        this.batches = new ArrayList<>();
        this.parsedAt = LocalDateTime.now();
    }

    // Getters and Setters
    public String getFileId() {
        return fileId;
    }

    public void setFileId(String fileId) {
        this.fileId = fileId;
    }

    public AchFileHeader getFileHeader() {
        return fileHeader;
    }

    public void setFileHeader(AchFileHeader fileHeader) {
        this.fileHeader = fileHeader;
    }

    public List<AchBatch> getBatches() {
        return batches;
    }

    public void setBatches(List<AchBatch> batches) {
        this.batches = batches;
    }

    public void addBatch(AchBatch batch) {
        this.batches.add(batch);
    }

    public AchFileControl getFileControl() {
        return fileControl;
    }

    public void setFileControl(AchFileControl fileControl) {
        this.fileControl = fileControl;
    }

    public LocalDateTime getParsedAt() {
        return parsedAt;
    }

    public void setParsedAt(LocalDateTime parsedAt) {
        this.parsedAt = parsedAt;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public long getFileSizeBytes() {
        return fileSizeBytes;
    }

    public void setFileSizeBytes(long fileSizeBytes) {
        this.fileSizeBytes = fileSizeBytes;
    }

    public int getTotalEntries() {
        return batches.stream().mapToInt(b -> b.getEntries().size()).sum();
    }

    @Override
    public String toString() {
        return "AchFile{" +
                "fileId='" + fileId + '\'' +
                ", fileName='" + fileName + '\'' +
                ", batches=" + batches.size() +
                ", totalEntries=" + getTotalEntries() +
                ", fileSizeBytes=" + fileSizeBytes +
                ", parsedAt=" + parsedAt +
                '}';
    }
}
