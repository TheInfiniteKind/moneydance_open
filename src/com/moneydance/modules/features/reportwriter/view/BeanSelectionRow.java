package com.moneydance.modules.features.reportwriter.view;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class BeanSelectionRow {
    private String text;
    private String type;
    private Boolean selected;
    private String rowId;
    private String sortText;
    private Integer depth;
    private BeanSelectionRow thisRow;
    private BeanSelectionPanel panel;
    private Boolean inActive;
    public BeanSelectionRow(String rowId,String text, String type, Boolean selected) {
        this.rowId=rowId;
        this.text = text;
        this.type=type;
        this.selected = selected;
        thisRow = this;
    }
    public void setPanel(BeanSelectionPanel panel) {
        this.panel= panel;
    }
    public String getText() {
        return text;
    }
    public void setText(String text) {
        this.text = text;
    }
    public String getType() {
        return type;
    }
    public void setType(String type) {
        this.type = type;
    }
    public boolean isSelected() {
        return selected;
    }
    public void setSelected(boolean selected) {
        this.selected=selected;
    }
    public String getRowId() {
        return rowId;
    }
    public void setRowId(String rowId) {
        this.rowId = rowId;
    }

    public String getSortText() {
        return sortText;
    }
    public void setSortText(String sortText) {
        this.sortText = sortText;
    }

    public Integer getDepth() {
        return depth;
    }
    public void setDepth(Integer depth) {
        this.depth = depth;
    }

    public boolean isInActive() {
        return inActive;
    }
    public void setInActive(boolean inActive) {
        this.inActive=inActive;
    }
    public JCheckBox getCol1() {
        JCheckBox check = new JCheckBox();
        check.setSelected(selected);
        check.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                JCheckBox tmp = (JCheckBox)e.getSource();
                setSelected(tmp.isSelected());
                if (panel!= null)
                    panel.setChildren(thisRow, selected);
            }
        });
        return check;
    }
    public JPanel getCol2() {
        JPanel listRow = new JPanel();
        listRow.setLayout(new BoxLayout(listRow, BoxLayout.X_AXIS));
        JLabel textLbl = new JLabel(getText());
        JLabel typeLbl = new JLabel(getType());
        listRow.add(textLbl);
        listRow.add(Box.createRigidArea(new Dimension(5, 0)));
        listRow.add(typeLbl);
        return listRow;
    }
}
