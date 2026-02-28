package com.example.ach2rtp.model.ach;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Domain model representing an ACH Entry Detail Record (Type 6).
 * 
 * Contains transaction details including receiver information, amount, and transaction type.
 */
public class AchEntry {

    private String recordTypeCode; // "6"
    private String transactionCode; // 22, 27, 32, 37, etc.
    private String receivingDfiRoutingNumber;
    private String receivingDfiAccountNumber;
    private BigDecimal amount;
    private String individualIdentificationNumber;
    private String individualName;
    private String discretionaryData;
    private String addendaRecordIndicator;
    private String traceNumber;
    private List<AchAddenda> addendaRecords;

    public AchEntry() {
        this.addendaRecords = new ArrayList<>();
    }

    // Getters and Setters
    public String getRecordTypeCode() {
        return recordTypeCode;
    }

    public void setRecordTypeCode(String recordTypeCode) {
        this.recordTypeCode = recordTypeCode;
    }

    public String getTransactionCode() {
        return transactionCode;
    }

    public void setTransactionCode(String transactionCode) {
        this.transactionCode = transactionCode;
    }

    public String getReceivingDfiRoutingNumber() {
        return receivingDfiRoutingNumber;
    }

    public void setReceivingDfiRoutingNumber(String receivingDfiRoutingNumber) {
        this.receivingDfiRoutingNumber = receivingDfiRoutingNumber;
    }

    public String getReceivingDfiAccountNumber() {
        return receivingDfiAccountNumber;
    }

    public void setReceivingDfiAccountNumber(String receivingDfiAccountNumber) {
        this.receivingDfiAccountNumber = receivingDfiAccountNumber;
    }

    public BigDecimal getAmount() {
        return amount;
    }

    public void setAmount(BigDecimal amount) {
        this.amount = amount;
    }

    public String getIndividualIdentificationNumber() {
        return individualIdentificationNumber;
    }

    public void setIndividualIdentificationNumber(String individualIdentificationNumber) {
        this.individualIdentificationNumber = individualIdentificationNumber;
    }

    public String getIndividualName() {
        return individualName;
    }

    public void setIndividualName(String individualName) {
        this.individualName = individualName;
    }

    public String getDiscretionaryData() {
        return discretionaryData;
    }

    public void setDiscretionaryData(String discretionaryData) {
        this.discretionaryData = discretionaryData;
    }

    public String getAddendaRecordIndicator() {
        return addendaRecordIndicator;
    }

    public void setAddendaRecordIndicator(String addendaRecordIndicator) {
        this.addendaRecordIndicator = addendaRecordIndicator;
    }

    public String getTraceNumber() {
        return traceNumber;
    }

    public void setTraceNumber(String traceNumber) {
        this.traceNumber = traceNumber;
    }

    public List<AchAddenda> getAddendaRecords() {
        return addendaRecords;
    }

    public void setAddendaRecords(List<AchAddenda> addendaRecords) {
        this.addendaRecords = addendaRecords;
    }

    public void addAddenda(AchAddenda addenda) {
        this.addendaRecords.add(addenda);
    }

    public boolean isDebit() {
        return transactionCode != null && (transactionCode.equals("22") || transactionCode.equals("27"));
    }

    public boolean isCredit() {
        return transactionCode != null && (transactionCode.equals("32") || transactionCode.equals("37"));
    }

    @Override
    public String toString() {
        return "AchEntry{" +
                "transactionCode='" + transactionCode + '\'' +
                ", receivingDfiRoutingNumber='" + receivingDfiRoutingNumber + '\'' +
                ", receivingDfiAccountNumber='" + receivingDfiAccountNumber + '\'' +
                ", amount=" + amount +
                ", individualName='" + individualName + '\'' +
                ", traceNumber='" + traceNumber + '\'' +
                ", addendaRecords=" + addendaRecords.size() +
                '}';
    }
}
