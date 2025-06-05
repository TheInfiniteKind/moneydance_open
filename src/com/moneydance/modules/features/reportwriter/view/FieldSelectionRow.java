package com.moneydance.modules.features.reportwriter.view;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class FieldSelectionRow {
	private String fieldName;
	private String fieldTitle;
	private Boolean selected;
	public FieldSelectionRow(String fieldName, String fieldTitle,Boolean selected) {
		setFieldName(fieldName);
		setFieldTitle(fieldTitle);
		setSelected(selected);
	}
	public String getFieldName() {
		return fieldName;
	}
	public void setFieldName(String fieldName) {
		this.fieldName = fieldName;
	}
	
	public String getFieldTitle() {
		return fieldTitle;
	}
	public void setFieldTitle(String fieldTitle) {
		this.fieldTitle = fieldTitle;
	}
	public Boolean getSelected() {
		return selected;
	}
	public void setSelected(Boolean selected) {
		this.selected = selected;
	}
	public JCheckBox getIncluded() {
		JCheckBox includedBox = new JCheckBox();
		includedBox.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox tmp = (JCheckBox)e.getSource();
				setSelected(tmp.isSelected());
			}
			
		});
		includedBox.setSelected(selected);
		return includedBox;
	}
	

}
