package com.moneydance.modules.features.loadsectrans;

import java.util.List;

public class ParametersFile {
    /*
     * The following fields are stored
     */

    private String ticker;
    private String value;
    private String dateField;
    private String reference;
    private String desc;
    private String unit;
    private boolean stripExch;
    private String delimiter;
    private List<FieldLine> fieldLines;
    public ParametersFile (){

    }

    public String getTicker() {
        return ticker;
    }

    public void setTicker(String ticker) {
        this.ticker = ticker;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getDateField() {
        return dateField;
    }

    public void setDateField(String dateField) {
        this.dateField = dateField;
    }

    public String getReference() {
        return reference;
    }

    public void setReference(String reference) {
        this.reference = reference;
    }

    public String getDesc() {
        return desc;
    }

    public void setDesc(String desc) {
        this.desc = desc;
    }

    public boolean isStripExch() {
        return stripExch;
    }

    public void setStripExch(boolean stripExch) {
        this.stripExch = stripExch;
    }

    public List<FieldLine> getFieldLines() {
        return fieldLines;
    }

    public void setFieldLines(List<FieldLine> fieldLines) {
        this.fieldLines = fieldLines;
    }

    public String getUnit() {
        return unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }
}
