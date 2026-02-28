package com.example.ach2rtp.model.ach;

import java.math.BigDecimal;

/**
 * Domain model representing ACH Batch Control Record (Type 8).
 * 
 * Contains batch-level totals and validation hash.
 */
public class AchBatchControl {

    private String recordTypeCode; // "8"
    private String serviceClassCode;
    private int entryAddendaCount;
    private String entryHash;
    private BigDecimal totalDebitAmount;
    private BigDecimal totalCreditAmount;
    private String companyIdentificationNumber;
    private String messageAuthenticationCode;
    private String reserved;
    private String originatingDfiIdentification;
    private String batchNumber;

    // Getters and Setters
    public String getRecordTypeCode() {
        return recordTypeCode;
    }

    public void setRecordTypeCode(String recordTypeCode) {
        this.recordTypeCode = recordTypeCode;
    }

    public String getServiceClassCode() {
        return serviceClassCode;
    }

    public void setServiceClassCode(String serviceClassCode) {
        this.serviceClassCode = serviceClassCode;
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

    public String getCompanyIdentificationNumber() {
        return companyIdentificationNumber;
    }

    public void setCompanyIdentificationNumber(String companyIdentificationNumber) {
        this.companyIdentificationNumber = companyIdentificationNumber;
    }

    public String getMessageAuthenticationCode() {
        return messageAuthenticationCode;
    }

    public void setMessageAuthenticationCode(String messageAuthenticationCode) {
        this.messageAuthenticationCode = messageAuthenticationCode;
    }

    public String getReserved() {
        return reserved;
    }

    public void setReserved(String reserved) {
        this.reserved = reserved;
    }

    public String getOriginatingDfiIdentification() {
        return originatingDfiIdentification;
    }

    public void setOriginatingDfiIdentification(String originatingDfiIdentification) {
        this.originatingDfiIdentification = originatingDfiIdentification;
    }

    public String getBatchNumber() {
        return batchNumber;
    }

    public void setBatchNumber(String batchNumber) {
        this.batchNumber = batchNumber;
    }

    @Override
    public String toString() {
        return "AchBatchControl{" +
                "entryAddendaCount=" + entryAddendaCount +
                ", totalDebitAmount=" + totalDebitAmount +
                ", totalCreditAmount=" + totalCreditAmount +
                ", batchNumber='" + batchNumber + '\'' +
                '}';
    }
}
