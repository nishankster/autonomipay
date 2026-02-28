package com.example.ach2rtp.model.ach;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/**
 * Domain model representing an ACH batch containing header, entries, and control records.
 */
public class AchBatch {

    private int batchNumber;
    private AchBatchHeader batchHeader;
    private List<AchEntry> entries;
    private AchBatchControl batchControl;

    public AchBatch() {
        this.entries = new ArrayList<>();
    }

    public AchBatch(int batchNumber) {
        this.batchNumber = batchNumber;
        this.entries = new ArrayList<>();
    }

    // Getters and Setters
    public int getBatchNumber() {
        return batchNumber;
    }

    public void setBatchNumber(int batchNumber) {
        this.batchNumber = batchNumber;
    }

    public AchBatchHeader getBatchHeader() {
        return batchHeader;
    }

    public void setBatchHeader(AchBatchHeader batchHeader) {
        this.batchHeader = batchHeader;
    }

    public List<AchEntry> getEntries() {
        return entries;
    }

    public void setEntries(List<AchEntry> entries) {
        this.entries = entries;
    }

    public void addEntry(AchEntry entry) {
        this.entries.add(entry);
    }

    public AchBatchControl getBatchControl() {
        return batchControl;
    }

    public void setBatchControl(AchBatchControl batchControl) {
        this.batchControl = batchControl;
    }

    public LocalDate getEffectiveDate() {
        return batchHeader != null ? batchHeader.getEffectiveDate() : null;
    }

    public String getServiceClassCode() {
        return batchHeader != null ? batchHeader.getServiceClassCode() : null;
    }

    @Override
    public String toString() {
        return "AchBatch{" +
                "batchNumber=" + batchNumber +
                ", entries=" + entries.size() +
                ", effectiveDate=" + getEffectiveDate() +
                '}';
    }
}
