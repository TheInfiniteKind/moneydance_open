/*
 * Copyright (c) 2021, Michael Bray.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */
package com.moneydance.modules.features.reportwriter.view;

import java.awt.*;
import java.awt.event.*;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.databeans.DataBean;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnTitle;

import javax.swing.*;

public class FieldSelectionPane {
	private JDialog stage;
	private MyGridPane pane;
	private JPanel buttons;
	private JScrollPane scroll;
	private List<FieldSelectionRow> model;
	private FieldSelectionTable thisTable = null;
	private FieldSelectionTableModel tableModel;
	private List<String> current;
	private String windowName;
	private int SCREENWIDTH;
	private int SCREENHEIGHT;
	private DataBean bean;
	private int mainWidth;
	private int mainHeight;
	private int locationX;
	private int locationY;

	public FieldSelectionPane(String windowName, DataBean bean, List<String> current) {
		this.current = current;
		this.windowName = windowName;
		this.bean = bean;
		Field[] fields = this.bean.getClass().getDeclaredFields();
		List<FieldSelectionRow> fieldList = new ArrayList<>();
		for (Field field : fields) {
			if (!field.isAnnotationPresent(ColumnName.class)) // not database field
				continue;
			ColumnName name = field.getAnnotation(ColumnName.class);
			String fldTitle;
			if (field.isAnnotationPresent(ColumnTitle.class)) {
				ColumnTitle title = field.getAnnotation(ColumnTitle.class);
				fldTitle = title.value();
			} else
				fldTitle = name.value();
			boolean selected;
            selected = current.contains(name.value());
			FieldSelectionRow fldRow = new FieldSelectionRow(name.value(), fldTitle, selected);
			fieldList.add(fldRow);

		}
		model = fieldList;

	}

	public List<String> displayPanel() {
		stage = new JDialog();
		stage.setModalityType(Dialog.ModalityType.APPLICATION_MODAL);
		pane = new MyGridPane(windowName);
		stage.add(pane);
		stage.setTitle("Select " + bean.getScreenTitle() + " Fields");
		stage.addComponentListener(new ComponentListener(){

			@Override
			public void componentResized(ComponentEvent e) {
				JDialog tmp = (JDialog)e.getComponent();
				SCREENWIDTH = tmp.getWidth();
				Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.FIELDPANEWIDTH, SCREENWIDTH);
				SCREENHEIGHT=tmp.getHeight();
				Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.FIELDPANEHEIGHT, SCREENHEIGHT);
				Main.rwDebugInst.debug("FieldSelectionPane","componentListener",
						MRBDebug.DETAILED,"Field Pane size set to "+SCREENWIDTH+"/"+SCREENHEIGHT);
			}

			@Override
			public void componentMoved(ComponentEvent e) {

			}

			@Override
			public void componentShown(ComponentEvent e) {

			}

			@Override
			public void componentHidden(ComponentEvent e) {

			}
		});
		int ix = 0;
		int iy = 0;
		setUpTable();
		scroll = new JScrollPane(thisTable);
		pane.add(scroll, GridC.getc(ix, iy++).colspan(2));
		buttons = new JPanel();
		buttons.setLayout(new BoxLayout(buttons,BoxLayout.X_AXIS));
		JButton selectAllBtn = new JButton("Select All");
		selectAllBtn.addActionListener(e -> selectAll());
		JButton deSelectAllBtn = new JButton("Deselect All");
		deSelectAllBtn.addActionListener(e -> deSelectAll());
		JButton okBtn = new JButton();
		if (Main.loadedIcons.okImg == null)
			okBtn.setText("OK");
		else
			okBtn.setIcon(new ImageIcon(Main.loadedIcons.okImg));
		okBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e){
				updateParms();
				stage.setVisible(false);
			}
		});
		JButton cancelBtn = new JButton();
		if (Main.loadedIcons.cancelImg == null)
			cancelBtn.setText("Cancel");
		else
			cancelBtn.setIcon(new ImageIcon(Main.loadedIcons.cancelImg));
		cancelBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				stage.setVisible(false);
			}
		});
		buttons.add(okBtn);
		buttons.add(Box.createRigidArea(new Dimension(5, 0)));
		buttons.add(selectAllBtn);
		buttons.add(Box.createRigidArea(new Dimension(5, 0)));
		buttons.add(deSelectAllBtn);
		buttons.add(Box.createRigidArea(new Dimension(5, 0)));
		buttons.add(cancelBtn);
		buttons.add(Box.createRigidArea(new Dimension(5, 0)));
		pane.add(buttons,GridC.getc( 0, iy).colspan(2).insets(10,5,5,5));
		resize();
		stage.pack();
		setLocation();
		stage.setVisible(true);
		return current;
	}
	public void setLocation(){
		mainWidth = Main.frame.getWidth();
		mainHeight = Main.frame.getHeight();
		locationX = (mainWidth-SCREENWIDTH)/2;
		locationY = (mainHeight-SCREENHEIGHT)/2;
		stage.setLocation(locationX,locationY);
	}
	public void resize() {
		SCREENWIDTH = Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.FIELDPANEWIDTH,
				Constants.FIELDSCREENWIDTH);
		SCREENHEIGHT = Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.FIELDPANEHEIGHT,
				Constants.FIELDSCREENHEIGHT);
		if (stage != null) {
			stage.setPreferredSize(new Dimension(SCREENWIDTH,SCREENHEIGHT));
		}


	}

	private void selectAll() {
		for (FieldSelectionRow row : model) {
			row.setSelected(true);
		}
		tableModel.fireTableDataChanged();
	}

	private void deSelectAll() {
		for (FieldSelectionRow row : model) {
			row.setSelected(false);
		}
		tableModel.fireTableDataChanged();
	}

	private void updateParms() {
		current = new ArrayList<String>();
		for (FieldSelectionRow row : model) {
			if (row.getSelected())
				current.add(row.getFieldName());
		}
	}

	@SuppressWarnings("unchecked")
	private void setUpTable() {
		tableModel = new FieldSelectionTableModel(model);
		thisTable = new FieldSelectionTable(tableModel);

	}

}
