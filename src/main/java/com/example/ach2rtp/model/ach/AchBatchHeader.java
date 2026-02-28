package com.example.ach2rtp.model.ach;

import java.time.LocalDate;

/**
 * Domain model representing ACH Batch Header Record (Type 5).
 * 
 * Describes the type and purpose of transactions within a batch.
 */
public class AchBatchHeader {

    private String recordTypeCode; // "5"
    private String serviceClassCode; // 200, 220, 225, 280
    private String companyName;
    private String companyDiscretionaryData;
    private String companyIdentificationNumber;
    private String standardEntryClassCode; // PPD, CCD, WEB, TEL, etc.
    private String companyEntryDescription;
    private LocalDate companyDescriptiveDate;
    private LocalDate effectiveDate;
    private String settlementDate;
    private String originatorStatusCode;
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

    public String getCompanyName() {
        return companyName;
    }

    public void setCompanyName(String companyName) {
        this.companyName = companyName;
    }

    public String getCompanyDiscretionaryData() {
        return companyDiscretionaryData;
    }

    public void setCompanyDiscretionaryData(String companyDiscretionaryData) {
        this.companyDiscretionaryData = companyDiscretionaryData;
    }

    public String getCompanyIdentificationNumber() {
        return companyIdentificationNumber;
    }

    public void setCompanyIdentificationNumber(String companyIdentificationNumber) {
        this.companyIdentificationNumber = companyIdentificationNumber;
    }

    public String getStandardEntryClassCode() {
        return standardEntryClassCode;
    }

    public void setStandardEntryClassCode(String standardEntryClassCode) {
        this.standardEntryClassCode = standardEntryClassCode;
    }

    public String getCompanyEntryDescription() {
        return companyEntryDescription;
    }

    public void setCompanyEntryDescription(String companyEntryDescription) {
        this.companyEntryDescription = companyEntryDescription;
    }

    public LocalDate getCompanyDescriptiveDate() {
        return companyDescriptiveDate;
    }

    public void setCompanyDescriptiveDate(LocalDate companyDescriptiveDate) {
        this.companyDescriptiveDate = companyDescriptiveDate;
    }

    public LocalDate getEffectiveDate() {
        return effectiveDate;
    }

    public void setEffectiveDate(LocalDate effectiveDate) {
        this.effectiveDate = effectiveDate;
    }

    public String getSettlementDate() {
        return settlementDate;
    }

    public void setSettlementDate(String settlementDate) {
        this.settlementDate = settlementDate;
    }

    public String getOriginatorStatusCode() {
        return originatorStatusCode;
    }

    public void setOriginatorStatusCode(String originatorStatusCode) {
        this.originatorStatusCode = originatorStatusCode;
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
        return "AchBatchHeader{" +
                "serviceClassCode='" + serviceClassCode + '\'' +
                ", companyName='" + companyName + '\'' +
                ", standardEntryClassCode='" + standardEntryClassCode + '\'' +
                ", effectiveDate=" + effectiveDate +
                ", batchNumber='" + batchNumber + '\'' +
                '}';
    }
}
