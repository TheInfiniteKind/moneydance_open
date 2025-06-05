package com.moneydance.modules.features.reportwriter.view;

import java.awt.*;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.util.ArrayList;
import java.util.List;
import javax.swing.*;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;

public class BeanSelectionPanel {
    private JDialog dialog;
    private BeanSelectionTable table;
    private BeanSelectionTableModel tableModel;
    private List<BeanSelectionRow> listModel;
    private List<String> selected=new ArrayList<>();
    private List<BeanSelectionRow> list;
    private String inActiveStr;
    private JButton inActiveBtn;
    private JScrollPane scroll;
    private int SCREENWIDTH;
    private int SCREENHEIGHT;

    private JPanel panDisplay;
    private String title;
    public BeanSelectionPanel (List<BeanSelectionRow> list, String inActiveStr, String title) {
        this.list = list;
        this.inActiveStr = inActiveStr;
        this.title=title;

    }
    public void display() {
        dialog = new JDialog();
        dialog.setModalityType(Dialog.ModalityType.APPLICATION_MODAL);
        dialog.addComponentListener(new ComponentListener(){

            @Override
            public void componentResized(ComponentEvent e) {
                JDialog tmp = (JDialog)e.getComponent();
                SCREENWIDTH = tmp.getWidth();
                Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.CRNTBEANPANEWIDTH, SCREENWIDTH);
                SCREENHEIGHT=tmp.getHeight();
                Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.CRNTBEANPANEHEIGHT, SCREENHEIGHT);
                resize();
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
        panDisplay = new JPanel();
        dialog.add(panDisplay);
        dialog.setTitle(title);
        panDisplay.setLayout(new GridBagLayout());
        listModel =list;
        for (BeanSelectionRow row : listModel)
            row.setPanel(this);
        tableModel = new BeanSelectionTableModel(listModel);
        table= new BeanSelectionTable(tableModel);
        scroll = new JScrollPane();
        scroll.setViewportView(table);
        int ix=0;
        int iy=0;
        panDisplay.add(scroll, GridC.getc(ix,iy).west().insets(5,10,5,10).colspan(5));
        JButton okBtn = new JButton();
        if (Main.loadedIcons.okImg == null)
            okBtn.setText("OK");
        else
            okBtn.setIcon(new ImageIcon(Main.loadedIcons.okImg));
        okBtn.addActionListener(e -> {
            selected.clear();
            for (BeanSelectionRow row : list) {
                if (row.isSelected())
                    selected.add(row.getRowId());
            }
            dialog.setVisible(false);
        });
        JButton cancelBtn = new JButton();
        if (Main.loadedIcons.cancelImg == null)
            cancelBtn.setText("Cancel");
        else
            cancelBtn.setIcon(new ImageIcon(Main.loadedIcons.cancelImg));
        cancelBtn.addActionListener(e -> dialog.setVisible(false));
        JButton selectAllBtn = new JButton("Select All");
        selectAllBtn.addActionListener(e -> selectAll());
        JButton deSelectAllBtn = new JButton("Deselect All");
        deSelectAllBtn.addActionListener(e -> deSelectAll());
        if (inActiveStr != null && !inActiveStr.isEmpty()) {
            inActiveBtn = new JButton(inActiveStr);
            inActiveBtn.addActionListener(e -> selectInactive());
        }
        iy=2;
        panDisplay.add(selectAllBtn, GridC.getc(ix++, iy).insets(10,10,10,10));
        panDisplay.add(deSelectAllBtn, GridC.getc(ix++, iy).insets(10,10,10,10));
        if (inActiveStr != null && !inActiveStr.isEmpty()) {
            panDisplay.add(inActiveBtn,GridC.getc(ix++, iy).insets(10,10,10,10));
        }
        panDisplay.add(okBtn,GridC.getc(ix++, iy).insets(10,10,10,10));
        panDisplay.add(cancelBtn,GridC.getc(ix, iy).insets(10,10,10,10));
        resize();
        dialog.pack();
        setLocation();
        dialog.setVisible(true);
    }
    public List<String> getSelected(){
        return selected;
    }
    private void selectAll() {
        for (BeanSelectionRow row : listModel) {
            row.setSelected(true);
        }
        tableModel.fireTableDataChanged();
    }
    private void deSelectAll() {
        for (BeanSelectionRow row : listModel) {
            row.setSelected(false);
        }
        tableModel.fireTableDataChanged();
    }
    private void selectInactive() {
        for (BeanSelectionRow row : listModel) {
            row.setSelected(!row.isInActive());
        }
        tableModel.fireTableDataChanged();
    }
    // TODO retest method
    public void setChildren(BeanSelectionRow rowSelected, Boolean select) {
        boolean found=false;
        Integer depthSelected=0;
        for (BeanSelectionRow row :listModel) {
            if (row == rowSelected) {
                found = true;
                depthSelected = row.getDepth();
            }
            else {
                if (found) {
                    if (row.getDepth() > depthSelected)
                        row.setSelected(select);
                    else
                        break;
                }
            }
        }
        tableModel.fireTableDataChanged();
    }
    public void setLocation(){
        int mainWidth = Main.frame.getWidth();
        int mainHeight = Main.frame.getHeight();
        int locationX = (mainWidth-SCREENWIDTH)/2;
        int locationY = (mainHeight-SCREENHEIGHT)/2;
        dialog.setLocation(locationX,locationY);
    }
    public void resize() {
        SCREENWIDTH = Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.CRNTBEANPANEWIDTH,
                Constants.BEANSCREENWIDTH);
        SCREENHEIGHT = Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.CRNTBEANPANEHEIGHT,
                Constants.BEANSCREENHEIGHT);
        Main.rwDebugInst.debug("BeanSelectionPanel","resize", MRBDebug.DETAILED,"size set to "+SCREENWIDTH+"/"+SCREENHEIGHT);
        if (dialog != null) {
            dialog.setPreferredSize(new Dimension(SCREENWIDTH,SCREENHEIGHT));
            scroll.setPreferredSize(new Dimension(SCREENWIDTH-20,SCREENHEIGHT-100));
            scroll.setMinimumSize(new Dimension(SCREENWIDTH-20,SCREENHEIGHT-100));
            Main.rwDebugInst.debug("BeanSelectionPanel","resize", MRBDebug.DETAILED,"scroll size set to "+scroll.getWidth()+"/"+scroll.getHeight());
        }
    }

}
