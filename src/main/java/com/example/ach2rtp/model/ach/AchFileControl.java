package com.example.ach2rtp.model.ach;

import java.math.BigDecimal;

/**
 * Domain model representing ACH File Control Record (Type 9).
 * 
 * Contains file-level totals and validation hash.
 */
public class AchFileControl {

    private String recordTypeCode; // "9"
    private int batchCount;
    private int blockCount;
    private int entryAddendaCount;
    private String entryHash;
    private BigDecimal totalDebitAmount;
    private BigDecimal totalCreditAmount;
    private String reserved;

    // Getters and Setters
    public String getRecordTypeCode() {
        return recordTypeCode;
    }

    public void setRecordTypeCode(String recordTypeCode) {
        this.recordTypeCode = recordTypeCode;
    }

    public int getBatchCount() {
        return batchCount;
    }

    public void setBatchCount(int batchCount) {
        this.batchCount = batchCount;
    }

    public int getBlockCount() {
        return blockCount;
    }

    public void setBlockCount(int blockCount) {
        this.blockCount = blockCount;
    }

    public int getEntryAddendaCount() {
        return entryAddendaCount;
    }

    public void setEntryAddendaCount(int entryAddendaCount) {
        this.entryAddendaCount = entryAddendaCount;
    }

    public String getEntryHash() {
        return entryHash;
    }

    public void setEntryHash(String entryHash) {
        this.entryHash = entryHash;
    }

    public BigDecimal getTotalDebitAmount() {
        return totalDebitAmount;
    }

    public void setTotalDebitAmount(BigDecimal totalDebitAmount) {
        this.totalDebitAmount = totalDebitAmount;
    }

    public BigDecimal getTotalCreditAmount() {
        return totalCreditAmount;
    }

    public void setTotalCreditAmount(BigDecimal totalCreditAmount) {
        this.totalCreditAmount = totalCreditAmount;
    }

    public String getReserved() {
        return reserved;
    }

    public void setReserved(String reserved) {
        this.reserved = reserved;
    }

    @Override
    public String toString() {
        return "AchFileControl{" +
                "batchCount=" + batchCount +
                ", blockCount=" + blockCount +
                ", entryAddendaCount=" + entryAddendaCount +
                ", totalDebitAmount=" + totalDebitAmount +
                ", totalCreditAmount=" + totalCreditAmount +
                '}';
    }
}
