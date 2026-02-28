package com.example.ach2rtp.model.ach;

/**
 * Domain model representing an ACH Addenda Record (Type 7).
 * 
 * Contains additional information for complex transactions.
 */
public class AchAddenda {

    private String recordTypeCode; // "7"
    private String addendaTypeCode;
    private String paymentRelatedInformation;
    private String addendaSequenceNumber;
    private String entryDetailSequenceNumber;

    // Getters and Setters
    public String getRecordTypeCode() {
        return recordTypeCode;
    }

    public void setRecordTypeCode(String recordTypeCode) {
        this.recordTypeCode = recordTypeCode;
    }

    public String getAddendaTypeCode() {
        return addendaTypeCode;
    }

    public void setAddendaTypeCode(String addendaTypeCode) {
        this.addendaTypeCode = addendaTypeCode;
    }

    public String getPaymentRelatedInformation() {
        return paymentRelatedInformation;
    }

    public void setPaymentRelatedInformation(String paymentRelatedInformation) {
        this.paymentRelatedInformation = paymentRelatedInformation;
    }

    public String getAddendaSequenceNumber() {
        return addendaSequenceNumber;
    }

    public void setAddendaSequenceNumber(String addendaSequenceNumber) {
        this.addendaSequenceNumber = addendaSequenceNumber;
    }

    public String getEntryDetailSequenceNumber() {
        return entryDetailSequenceNumber;
    }

    public void setEntryDetailSequenceNumber(String entryDetailSequenceNumber) {
        this.entryDetailSequenceNumber = entryDetailSequenceNumber;
    }

    @Override
    public String toString() {
        return "AchAddenda{" +
                "recordTypeCode='" + recordTypeCode + '\'' +
                ", addendaTypeCode='" + addendaTypeCode + '\'' +
                ", paymentRelatedInformation='" + paymentRelatedInformation + '\'' +
                ", addendaSequenceNumber='" + addendaSequenceNumber + '\'' +
                '}';
    }
}
