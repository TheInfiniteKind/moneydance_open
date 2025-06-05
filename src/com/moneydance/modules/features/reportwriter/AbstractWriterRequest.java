package com.moneydance.modules.features.reportwriter;

public interface AbstractWriterRequest {
    public abstract String getTransactionId();

    public abstract String getShortSummary();

}
