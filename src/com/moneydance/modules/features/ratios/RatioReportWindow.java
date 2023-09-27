/*
 * ************************************************************************
 * Copyright (C) 2015 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */
 
package com.moneydance.modules.features.ratios;

import com.moneydance.apps.md.view.gui.*;
import com.moneydance.apps.md.controller.*;
import com.moneydance.apps.md.view.gui.reporttool.GraphReportUtil;
import com.moneydance.apps.md.view.gui.reporttool.Report;
import com.moneydance.apps.md.view.gui.reporttool.ReportGenerator;
import com.moneydance.apps.md.view.gui.reporttool.ReportViewer;
import com.moneydance.awt.*;
import com.moneydance.util.UiUtil;

import java.awt.*;
import java.awt.event.*;
import java.util.concurrent.Callable;
import java.util.concurrent.CancellationException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.FutureTask;
import javax.swing.*;
import javax.swing.border.*;

public class RatioReportWindow extends SecondaryDialog implements ActionListener
{
  private static final String CARD_REPORT = "report";
  private static final String CARD_NOTHING = "nothing";
  private static final String LAND_SIZE_KEY = "gui.ratios_land_report_size";
  private static final String LAND_LOC_KEY = "gui.ratios_land_report_loc";
  private static final String PORT_SIZE_KEY = "gui.ratios_port_report_size";
  private static final String PORT_LOC_KEY = "gui.ratios_port_report_loc";

  private final ReportGenerator _generator;

  private JLabel _nothingLabel;
  private CardLayout _cardLayout;
  private JButton doneButton;
  private JButton printButton;
  private JButton saveButton;
  private JButton copyButton;
  private JCheckBox _orientationBox;
  private ReportViewer _reportViewer;
  private JPanel _mainDetailView;

  // runs tasks on a separate thread
  private FutureTask _currentTask;

  public RatioReportWindow(MoneydanceGUI mdGUI, Frame parent, ReportGenerator generator) {
    super(mdGUI, parent, mdGUI.getStr("report"), false);
    _generator = generator;
    _generator.setSuppressMessageDialogs(true); // we'll handle the messages here

    JPanel p = createControls(mdGUI, generator.isLandscape());
    addListeners();
    getContentPane().add(p);
    setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
    enableEvents(WindowEvent.WINDOW_CLOSING);

    pack();
    
    if (generator.isLandscape()) {
      setRememberSizeLocationKeys(LAND_SIZE_KEY, LAND_LOC_KEY, new Dimension(800, 620));
    } else {
      setRememberSizeLocationKeys(PORT_SIZE_KEY, PORT_LOC_KEY, new Dimension(620, 800));
    }

    // transfer the initial setting to the viewer too to keep _layoutButton in sync
    _reportViewer.setLandscape(generator.isLandscape());
    setCalculationError(mdGUI.getStr("generating"));

    setCurrentTask(new GenerateReportTask(generator));
    ExecutorService executor = Executors.newFixedThreadPool(1);
    executor.execute(_currentTask);
  }

  private void addListeners() {
    doneButton.addActionListener(this);
    saveButton.addActionListener(this);
    printButton.addActionListener(this);
    copyButton.addActionListener(this);
    _orientationBox.addItemListener(new ItemListener() {
      public void itemStateChanged(ItemEvent event) {
        // toggle print orientation
        final boolean isLandscape = (event.getStateChange() == ItemEvent.SELECTED);
        _reportViewer.setLandscape(isLandscape);
        _generator.setLandscape(isLandscape);
      }
    });
  }

  private void cleanUpTask() {
    synchronized (this) {
      _currentTask = null;
    }
  }

  private JPanel createControls(final MoneydanceGUI mdGUI, final boolean isLandscape) {
    doneButton = new JButton(mdGUI.getStr("done"));
    printButton = new JButton(mdGUI.getStr("report_print"));
    saveButton = new JButton(mdGUI.getStr("report_save"));
    copyButton = new JButton(mdGUI.getStr("edit_copy"));
    _reportViewer = new ReportViewer(mdGUI);
    _orientationBox = new JCheckBox(mdGUI.getStr("report_landscape"), isLandscape);
    _orientationBox.setOpaque(false);
    _nothingLabel = new JLabel(mdGUI.getStr("generating"));
    _nothingLabel.setHorizontalAlignment(JLabel.CENTER);
    _nothingLabel.setVerticalAlignment(JLabel.CENTER);
    Font currentFont = _nothingLabel.getFont();
    _nothingLabel.setFont(currentFont.deriveFont(Font.BOLD, currentFont.getSize() + 3f));
    _nothingLabel.setOpaque(false);

    int x = 0;
    JPanel bp = new JPanel(new GridBagLayout());
    bp.add(printButton, GridC.getc(x++, 0));
    bp.add(saveButton, GridC.getc(x++,0));
    bp.add(Box.createHorizontalStrut(UiUtil.DLG_HGAP), GridC.getc(x++,0)); // memorize button
    bp.add(copyButton, GridC.getc(x++,0));
    bp.add(_orientationBox, GridC.getc(x++,0));
    bp.add(Box.createHorizontalStrut(UiUtil.DLG_HGAP), GridC.getc(x++,0).wx(1).fillx());
    bp.add(doneButton, GridC.getc(x,0));
    bp.setBorder(new EmptyBorder(UiUtil.DLG_VGAP,UiUtil.DLG_HGAP,UiUtil.DLG_VGAP,UiUtil.DLG_HGAP));

    JPanel reportPanel = new JPanel(new BorderLayout());
    reportPanel.add(_reportViewer, BorderLayout.CENTER);
    reportPanel.add(bp, BorderLayout.SOUTH);

    _cardLayout = new CardLayout();
    _mainDetailView = new JPanel(_cardLayout);
    _mainDetailView.add(reportPanel, CARD_REPORT);
    _mainDetailView.add(_nothingLabel, CARD_NOTHING);
    _cardLayout.show(_mainDetailView, CARD_NOTHING);
    return _mainDetailView;
  }

  @Override
  public void goneAway()
  {
    super.goneAway();
    if (_generator != null) {
      _generator.goneAway();
    }
  }


  public void isNowVisible() {
    doneButton.requestFocus();
  }

  private void setCalculationError(final String errorMessage)
  {
    // refresh
    UiUtil.runOnUIThread(new Runnable()
    {
      public void run()
      {
        _nothingLabel.setText(errorMessage);
        _cardLayout.show(_mainDetailView, CARD_NOTHING);
        validate();
        repaint();
      }
    });
  }

  private void setCurrentTask(final FutureTask task) {
    synchronized (this) {
      if (_currentTask != null) {
        _currentTask.cancel(true);
      }
      _currentTask = task;
    }
  }

  public void actionPerformed(ActionEvent evt) {
    Object src = evt.getSource();
    if(src==doneButton) {
      GraphReportUtil.saveCommonReportSettings(_reportViewer, _generator, true);
      goAwayNow();
    } else if(src==printButton) {
      GraphReportUtil.saveCommonReportSettings(_reportViewer, _generator, true);
      GraphReportUtil.printReport(mdGUI, _reportViewer);
    } else if(src==saveButton) {
      GraphReportUtil.saveCommonReportSettings(_reportViewer, _generator, true);
      GraphReportUtil.saveReport(mdGUI, _reportViewer);
    } else if(src==copyButton) {
      GraphReportUtil.saveCommonReportSettings(_reportViewer, _generator, true);
      GraphReportUtil.copyReport(mdGUI, _reportViewer);
    }
  }

  private void refresh() {
    // refresh
    UiUtil.runOnUIThread(new Runnable()
    {
      public void run()
      {
        validate();
        repaint();
      }
    });
  }

  private void showReport(final Report report) {
    setTitle(report.getTitle());

    // transfer the initial setting to the viewer too to keep in sync
    _reportViewer.setReport(report, _generator.getColumnWidths(), _generator.getColumnOrder());
    _reportViewer.setLandscape(_generator.isLandscape());
    _cardLayout.show(_mainDetailView, CARD_REPORT);

    if (report.getSettings() != null) {
      copyButton.setEnabled(true);
      _orientationBox.setEnabled(true);
    }

    refresh();
  }

  private class GenerateReportTask extends FutureTask<Report> {

    public GenerateReportTask(final ReportGenerator generator) {
      super(new ReportCalculateTask(generator));
    }

    @Override
    protected void done() {
      if (isCancelled()) {
        // nothing to do
        return;
      }

      try {
        final Report result = get();
        if (result == null) {
          setCalculationError(mdGUI.getStr("nothing_to_report"));
        } else {
          UiUtil.runOnUIThread(new Runnable() {
            public void run() {
              showReport(result);
            }
          });
        }
      } catch (InterruptedException | CancellationException ignore) {
        // if multiple transaction changes come in, the task may be canceled with normal
        // program flow, therefore ignore
      } catch (ExecutionException exex) {
        exex.printStackTrace(System.err);
        setCalculationError(mdGUI.getStr("gen_report_error"));
      }
      // remove the current task
      cleanUpTask();
    }
  }

  private static class ReportCalculateTask implements Callable<Report> {
    private final GraphReportGenerator _generator;

    ReportCalculateTask(final GraphReportGenerator generator) {
      _generator = generator;
    }

    public Report call() throws Exception {
      final Report result = (Report) _generator.generate();
//      // if the user has customized the report but not memorized, don't set the memorized
//      // name (null) which makes the title disappear
//      if ((result != null) && isMemorized()) {
//        result.setTitle(_memorizedName);
//      }
      return result;
    }
  }
}
