package com.example.ach2rtp.model.ach;

import java.time.LocalDate;
import java.time.LocalTime;

/**
 * Domain model representing ACH File Header Record (Type 1).
 * 
 * Contains file-level metadata including originating bank, company, and timing information.
 */
public class AchFileHeader {

    private String recordTypeCode; // "101"
    private String priorityCode;
    private String immediateDestination; // Receiving bank routing number
    private String immediateOrigin; // Originating bank routing number
    private LocalDate fileCreationDate;
    private LocalTime fileCreationTime;
    private String fileIdModifier;
    private String recordSize; // "094"
    private String blockingFactor; // "10"
    private String formatCode; // "1"
    private String immediateDestinationName;
    private String immediateOriginName;
    private String referenceCode;

    // Getters and Setters
    public String getRecordTypeCode() {
        return recordTypeCode;
    }

    public void setRecordTypeCode(String recordTypeCode) {
        this.recordTypeCode = recordTypeCode;
    }

    public String getPriorityCode() {
        return priorityCode;
    }

    public void setPriorityCode(String priorityCode) {
        this.priorityCode = priorityCode;
    }

    public String getImmediateDestination() {
        return immediateDestination;
    }

    public void setImmediateDestination(String immediateDestination) {
        this.immediateDestination = immediateDestination;
    }

    public String getImmediateOrigin() {
        return immediateOrigin;
    }

    public void setImmediateOrigin(String immediateOrigin) {
        this.immediateOrigin = immediateOrigin;
    }

    public LocalDate getFileCreationDate() {
        return fileCreationDate;
    }

    public void setFileCreationDate(LocalDate fileCreationDate) {
        this.fileCreationDate = fileCreationDate;
    }

    public LocalTime getFileCreationTime() {
        return fileCreationTime;
    }

    public void setFileCreationTime(LocalTime fileCreationTime) {
        this.fileCreationTime = fileCreationTime;
    }

    public String getFileIdModifier() {
        return fileIdModifier;
    }

    public void setFileIdModifier(String fileIdModifier) {
        this.fileIdModifier = fileIdModifier;
    }

    public String getRecordSize() {
        return recordSize;
    }

    public void setRecordSize(String recordSize) {
        this.recordSize = recordSize;
    }

    public String getBlockingFactor() {
        return blockingFactor;
    }

    public void setBlockingFactor(String blockingFactor) {
        this.blockingFactor = blockingFactor;
    }

    public String getFormatCode() {
        return formatCode;
    }

    public void setFormatCode(String formatCode) {
        this.formatCode = formatCode;
    }

    public String getImmediateDestinationName() {
        return immediateDestinationName;
    }

    public void setImmediateDestinationName(String immediateDestinationName) {
        this.immediateDestinationName = immediateDestinationName;
    }

    public String getImmediateOriginName() {
        return immediateOriginName;
    }

    public void setImmediateOriginName(String immediateOriginName) {
        this.immediateOriginName = immediateOriginName;
    }

    public String getReferenceCode() {
        return referenceCode;
    }

    public void setReferenceCode(String referenceCode) {
        this.referenceCode = referenceCode;
    }

    @Override
    public String toString() {
        return "AchFileHeader{" +
                "recordTypeCode='" + recordTypeCode + '\'' +
                ", immediateDestination='" + immediateDestination + '\'' +
                ", immediateOrigin='" + immediateOrigin + '\'' +
                ", fileCreationDate=" + fileCreationDate +
                ", fileCreationTime=" + fileCreationTime +
                ", immediateDestinationName='" + immediateDestinationName + '\'' +
                ", immediateOriginName='" + immediateOriginName + '\'' +
                '}';
    }
}
