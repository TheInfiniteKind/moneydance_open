/*
 * Copyright (c) 2018, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.securityquoteload.view;

import java.awt.BorderLayout;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Enumeration;

import javax.swing.AbstractButton;
import javax.swing.ButtonGroup;
import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JRadioButton;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.Main;

public class CalendarPopup extends JDialog {
	String runType;
	String runParam;
	String prefRunType;
	String prefRunParam;
	JPanel choicePan;
	JRadioButton weekMon = new TransRadio	("Monday");
	JRadioButton weekTue = new TransRadio	("Tuesday");
	JRadioButton weekWed = new TransRadio	("Wednesday");
	JRadioButton weekThu = new TransRadio ("Thursday");
	JRadioButton weekFri = new TransRadio	("Friday");
	JRadioButton weekSat = new TransRadio	("Saturday");
	JRadioButton weekSun = new TransRadio	("Sunday");
	ButtonGroup weeklyGroup;
	JRadioButton monthFirstMon = new TransRadio("First Monday");
	JRadioButton monthLastFri = new TransRadio("Last Friday");
	JRadioButton monthLastDay = new TransRadio("Last Day");
	JRadioButton month1st = new TransRadio("1st");
	JRadioButton month2nd= new TransRadio("2nd");
	JRadioButton month3rd = new TransRadio("3rd");
	JRadioButton month4th = new TransRadio("4th");
	JRadioButton month5th = new TransRadio("5th");
	JRadioButton month6th = new TransRadio("6th");
	JRadioButton month7th = new TransRadio("7th");
	JRadioButton month8th = new TransRadio("8th");
	JRadioButton month9th = new TransRadio("9th");
	JRadioButton month10th = new TransRadio("10th");
	JRadioButton month11th = new TransRadio("11th");
	JRadioButton month12th = new TransRadio("12th");
	JRadioButton month13th = new TransRadio("13th");
	JRadioButton month14th = new TransRadio("14th");
	JRadioButton month15th = new TransRadio("15th");
	JRadioButton month16th = new TransRadio("16th");
	JRadioButton month17th = new TransRadio("17th");
	JRadioButton month18th = new TransRadio("18th");
	JRadioButton month19th = new TransRadio("19th");
	JRadioButton month20th = new TransRadio("20th");
	JRadioButton month21st = new TransRadio("21st");
	JRadioButton month22nd= new TransRadio("22nd");
	JRadioButton month23rd = new TransRadio("23rd");
	JRadioButton month24th = new TransRadio("24th");
	JRadioButton month25th = new TransRadio("25th");
	JRadioButton month26th = new TransRadio("26th");
	JRadioButton month27th = new TransRadio("27th");
	JRadioButton month28th = new TransRadio("28th");
	JRadioButton month29th = new TransRadio("29th");
	JRadioButton month30th = new TransRadio("30th");
	JRadioButton month31st = new TransRadio("31st");
	ButtonGroup monthlyGroup;
	JRadioButton quarterFirst = new TransRadio("First Day");
	JRadioButton quarterLast = new TransRadio("Last Day");
	JRadioButton quarterSpecific = new TransRadio("Set Date");
	JRadioButton quarterMonth1 = new TransRadio("Month 1");
	JRadioButton quarterMonth2 = new TransRadio("Month 2");
	JRadioButton quarterMonth3 = new TransRadio("Month 3");
	JRadioButton quarter1st = new TransRadio("1st");
	JRadioButton quarter2nd= new TransRadio("2nd");
	JRadioButton quarter3rd = new TransRadio("3rd");
	JRadioButton quarter4th = new TransRadio("4th");
	JRadioButton quarter5th = new TransRadio("5th");
	JRadioButton quarter6th = new TransRadio("6th");
	JRadioButton quarter7th = new TransRadio("7th");
	JRadioButton quarter8th = new TransRadio("8th");
	JRadioButton quarter9th = new TransRadio("9th");
	JRadioButton quarter10th = new TransRadio("10th");
	JRadioButton quarter11th = new TransRadio("11th");
	JRadioButton quarter12th = new TransRadio("12th");
	JRadioButton quarter13th = new TransRadio("13th");
	JRadioButton quarter14th = new TransRadio("14th");
	JRadioButton quarter15th = new TransRadio("15th");
	JRadioButton quarter16th = new TransRadio("16th");
	JRadioButton quarter17th = new TransRadio("17th");
	JRadioButton quarter18th = new TransRadio("18th");
	JRadioButton quarter19th = new TransRadio("19th");
	JRadioButton quarter20th = new TransRadio("20th");
	JRadioButton quarter21st = new TransRadio("21st");
	JRadioButton quarter22nd= new TransRadio("22nd");
	JRadioButton quarter23rd = new TransRadio("23rd");
	JRadioButton quarter24th = new TransRadio("24th");
	JRadioButton quarter25th = new TransRadio("25th");
	JRadioButton quarter26th = new TransRadio("26th");
	JRadioButton quarter27th = new TransRadio("27th");
	JRadioButton quarter28th = new TransRadio("28th");
	JRadioButton quarter29th = new TransRadio("29th");
	JRadioButton quarter30th = new TransRadio("30th");
	JRadioButton quarter31st = new TransRadio("31st");
	ButtonGroup quarterlyGroup;
	ButtonGroup quarterlyGroupMonth;
	ButtonGroup quarterlyGroupDay;
	DetailPanel detailPane;
	String resultParam;
	public CalendarPopup (String prefRunTypep, String prefRunParamp){
	   	super((JFrame)null,"Run Time",true);
	   	this.setLayout(new BorderLayout());
	   	prefRunType = prefRunTypep;
	   	prefRunParam = prefRunParamp;
	   	runType = Main.preferences.getString(Constants.PROGRAMNAME+"."+prefRunType,"");
	   	runParam = Main.preferences.getString(Constants.PROGRAMNAME+"."+prefRunParam,"");
	   	switch (runType) {
	   		case Constants.RUNYEARLY :
	   			detailPane = new setupYearly();
	   			break;
	   		case Constants.RUNWEEKLY :
	   			detailPane = new setupWeekly(runParam);
	   			break;
	   		case Constants.RUNMONTHLY :
	   			detailPane = new setupMonthly(runParam);
	   			break;
	   		case Constants.RUNQUARTERLY :
	   			detailPane = new setupQuarterly(runParam);
	   			break;
	   		default :
	   			detailPane = new setupDaily();
	   			break;
	   	}
	   	add(detailPane,BorderLayout.CENTER);
        JPanel buttons = new JPanel(new GridBagLayout());
        JButton okButton = new JButton("Ok");
		okButton.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				if (detailPane.validateFields()) {
					Main.preferences.put(Constants.PROGRAMNAME+"."+prefRunParam,resultParam);
					Main.preferences.isDirty();
					dispose();
				}
			}
		});	
        JButton cancelButton = new JButton("Cancel");
		cancelButton.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				dispose();
			}
		});	


        buttons.add(okButton,GridC.getc(0, 0).center().insets(5,20,5,5));
        buttons.add(cancelButton,GridC.getc(1, 0).center().insets(5,20,5,5));
        this.add(buttons,BorderLayout.SOUTH);
		pack();		
	}
	private abstract class DetailPanel extends JPanel {
		public boolean validateFields(){
			return false;
		}
	}
	private class setupDaily extends DetailPanel{
		public setupDaily() {
			setLayout(new GridBagLayout());
			String text = "<html><b> Set the 'Next Run Date' to the date you wish Automatic Running"
					+ " to start.<p> It will run daily from then on. </b></html>";
			JLabel label = new JLabel( text); 
			add(label,GridC.getc(0,0).insets(30,30,30,30));
		}
		@Override
		public boolean validateFields() {
			return true;
		}
	}
	private class setupYearly extends DetailPanel {
		public setupYearly() {
			setLayout(new GridBagLayout());
			String text = "<html><b> Set the 'Next Run Date' to the date you wish Automatic Running"
					+ " to start.<p> It will run on the same day each year. </b></html>";
			JLabel label = new JLabel( text); 
			add(label,GridC.getc(0,0).insets(30,30,30,30));
		}
		@Override
		public boolean validateFields() {
			return true;
		}
	}
	private class setupWeekly extends DetailPanel implements ActionListener{
		public setupWeekly (String crntDay) {
			setResult(crntDay);
			setLayout(new GridBagLayout());
			weeklyGroup = new ButtonGroup();
			weeklyGroup.add (weekMon);
			weeklyGroup.add (weekTue);
			weeklyGroup.add (weekWed);
			weeklyGroup.add (weekThu);
			weeklyGroup.add (weekFri);
			weeklyGroup.add (weekSat);
			weeklyGroup.add (weekSun);
			if(crntDay.equals(Constants.SCHDAY1)) weekSun.setSelected(true);
			if(crntDay.equals(Constants.SCHDAY2)) weekMon.setSelected(true);
			if(crntDay.equals(Constants.SCHDAY3)) weekTue.setSelected(true);
			if(crntDay.equals(Constants.SCHDAY4)) weekWed.setSelected(true);
			if(crntDay.equals(Constants.SCHDAY5)) weekThu.setSelected(true);
			if(crntDay.equals(Constants.SCHDAY6)) weekFri.setSelected(true);
			if(crntDay.equals(Constants.SCHDAY7)) weekSat.setSelected(true);
			weekMon.addActionListener(this);
			weekTue.addActionListener(this);
			weekWed.addActionListener(this);
			weekThu.addActionListener(this);
			weekFri.addActionListener(this);
			weekSat.addActionListener(this);
			weekSun.addActionListener(this);
			int ix = 0;
			int iy =0;
			JLabel dayLbl = new JLabel("<html><b>  Select the day of the week to run  </b></html>");
			add(dayLbl,GridC.getc(ix,iy++));
			add(weekSun,GridC.getc(ix,iy++));
			add(weekMon,GridC.getc(ix,iy++));
			add(weekTue,GridC.getc(ix,iy++));
			add(weekWed,GridC.getc(ix,iy++));
			add(weekThu,GridC.getc(ix,iy++));
			add(weekFri,GridC.getc(ix,iy++));
			add(weekSat,GridC.getc(ix,iy++));
			return;
		}
		@Override
		public void actionPerformed (ActionEvent e){
			JRadioButton button = (JRadioButton)e.getSource();
			String day = button.getText();
			if (day.contains("Sun")) {setResult(Constants.SCHDAY1);return;}
			if (day.contains("Mon")) {setResult(Constants.SCHDAY2);return;}
			if (day.contains("Tue")) {setResult(Constants.SCHDAY3);return;}
			if (day.contains("Wed")) {setResult(Constants.SCHDAY4);return;}
			if (day.contains("Thu")) {setResult(Constants.SCHDAY5);return;}
			if (day.contains("Fri")) {setResult(Constants.SCHDAY6);return;}
			if (day.contains("Sat")) {setResult(Constants.SCHDAY7);return;}
		}
		private void setResult(String resultp){
			resultParam = resultp;
		}
		@Override
		public boolean validateFields() {
			if (weekSun.isSelected())return true;
			if (weekMon.isSelected())return true;
			if (weekTue.isSelected())return true;
			if (weekWed.isSelected())return true;
			if (weekThu.isSelected())return true;
			if (weekFri.isSelected())return true;
			if (weekSat.isSelected())return true;
			JOptionPane.showMessageDialog(null, "Please select a day of the week");
			return false;
		}
	}
	private class setupMonthly extends DetailPanel implements ActionListener{
		public setupMonthly (String crntDay) {
			setResult(crntDay);
			setLayout(new GridBagLayout());
			monthlyGroup = new ButtonGroup();
			monthlyGroup.add (monthFirstMon);
			monthlyGroup.add (monthLastFri);
			monthlyGroup.add (monthLastDay);
			monthlyGroup.add (month1st);
			monthlyGroup.add (month2nd);
			monthlyGroup.add (month3rd);
			monthlyGroup.add (month4th);
			monthlyGroup.add (month5th);
			monthlyGroup.add (month6th);
			monthlyGroup.add (month7th);
			monthlyGroup.add (month8th);
			monthlyGroup.add (month9th);
			monthlyGroup.add (month10th);
			monthlyGroup.add (month11th);
			monthlyGroup.add (month12th);
			monthlyGroup.add (month13th);
			monthlyGroup.add (month14th);
			monthlyGroup.add (month15th);
			monthlyGroup.add (month16th);
			monthlyGroup.add (month17th);
			monthlyGroup.add (month18th);
			monthlyGroup.add (month19th);
			monthlyGroup.add (month20th);
			monthlyGroup.add (month21st);
			monthlyGroup.add (month22nd);
			monthlyGroup.add (month23rd);
			monthlyGroup.add (month24th);
			monthlyGroup.add (month25th);
			monthlyGroup.add (month26th);
			monthlyGroup.add (month27th);
			monthlyGroup.add (month28th);
			monthlyGroup.add (month29th);
			monthlyGroup.add (month30th);
			monthlyGroup.add (month31st);
			if(crntDay.equals(Constants.SCHFIRSTMON)) monthFirstMon.setSelected(true);
			if(crntDay.equals(Constants.SCHLASTFRI)) monthLastFri.setSelected(true);
			if(crntDay.equals(Constants.SCHLASTDAY)) monthLastDay.setSelected(true);
			if(crntDay.contains(Constants.SCHMONTHDAY) ){
				switch (crntDay.substring(Constants.SCHMONTHDAY.length())){
				case "01" : month1st.setSelected(true);break;
				case "02" : month2nd.setSelected(true);break;
				case "03" : month3rd.setSelected(true);break;
				case "04" : month4th.setSelected(true);break;
				case "05" : month5th.setSelected(true);break;
				case "06" : month6th.setSelected(true);break;
				case "07" : month7th.setSelected(true);break;
				case "08" : month8th.setSelected(true);break;
				case "09" : month9th.setSelected(true);break;
				case "10" : month10th.setSelected(true);break;
				case "11" : month11th.setSelected(true);break;
				case "12" : month12th.setSelected(true);break;
				case "13" : month13th.setSelected(true);break;
				case "14" : month14th.setSelected(true);break;
				case "15" : month15th.setSelected(true);break;
				case "16" : month16th.setSelected(true);break;
				case "17" : month17th.setSelected(true);break;
				case "18" : month18th.setSelected(true);break;
				case "19" : month19th.setSelected(true);break;
				case "20" : month20th.setSelected(true);break;
				case "21" : month21st.setSelected(true);break;
				case "22" : month22nd.setSelected(true);break;
				case "23" : month23rd.setSelected(true);break;
				case "24" : month24th.setSelected(true);break;
				case "25" : month25th.setSelected(true);break;
				case "26" : month26th.setSelected(true);break;
				case "27" : month27th.setSelected(true);break;
				case "28" : month28th.setSelected(true);break;
				case "29" : month29th.setSelected(true);break;
				case "30" : month30th.setSelected(true);break;
				case "31" : month31st.setSelected(true);break;
				}
			}
			monthFirstMon.addActionListener(this);
			monthLastFri.addActionListener(this);
			monthLastDay.addActionListener(this);
			month1st.addActionListener(this);
			month2nd.addActionListener(this);
			month3rd.addActionListener(this);
			month4th.addActionListener(this);
			month5th.addActionListener(this);
			month6th.addActionListener(this);
			month7th.addActionListener(this);
			month8th.addActionListener(this);
			month9th.addActionListener(this);
			month10th.addActionListener(this);
			month11th.addActionListener(this);
			month12th.addActionListener(this);
			month13th.addActionListener(this);
			month14th.addActionListener(this);
			month15th.addActionListener(this);
			month16th.addActionListener(this);
			month17th.addActionListener(this);
			month18th.addActionListener(this);
			month19th.addActionListener(this);
			month20th.addActionListener(this);
			month21st.addActionListener(this);
			month22nd.addActionListener(this);
			month23rd.addActionListener(this);
			month24th.addActionListener(this);
			month25th.addActionListener(this);
			month26th.addActionListener(this);
			month27th.addActionListener(this);
			month28th.addActionListener(this);
			month29th.addActionListener(this);
			month30th.addActionListener(this);
			month31st.addActionListener(this);
			int ix = 0;
			int iy =0;
			JLabel dayLbl = new JLabel("<html><b>  Select the day of the month to run  </b></html>");
			add(dayLbl,GridC.getc(ix,iy++).colspan(4));
			add(monthFirstMon,GridC.getc(ix,iy).west().colspan(2));
			add(monthLastFri,GridC.getc(ix+2,iy).west().colspan(2));
			add(monthLastDay,GridC.getc(ix+4,iy++).west().colspan(2));
			ix=0;
			add(month1st,GridC.getc(ix++,iy).west());
			add(month2nd,GridC.getc(ix++,iy).west());
			add(month3rd,GridC.getc(ix++,iy).west());
			add(month4th,GridC.getc(ix++,iy).west());
			add(month5th,GridC.getc(ix++,iy).west());
			add(month6th,GridC.getc(ix++,iy).west());
			add(month7th,GridC.getc(ix++,iy).west());
			add(month8th,GridC.getc(ix,iy++).west());
			ix=0;
			add(month9th,GridC.getc(ix++,iy).west());
			add(month10th,GridC.getc(ix++,iy).west());
			add(month11th,GridC.getc(ix++,iy).west());
			add(month12th,GridC.getc(ix++,iy).west());
			add(month13th,GridC.getc(ix++,iy).west());
			add(month14th,GridC.getc(ix++,iy).west());
			add(month15th,GridC.getc(ix++,iy).west());
			add(month16th,GridC.getc(ix,iy++).west());
			ix=0;
			add(month17th,GridC.getc(ix++,iy).west());
			add(month18th,GridC.getc(ix++,iy).west());
			add(month19th,GridC.getc(ix++,iy).west());
			add(month20th,GridC.getc(ix++,iy).west());
			add(month21st,GridC.getc(ix++,iy).west());
			add(month22nd,GridC.getc(ix++,iy).west());
			add(month23rd,GridC.getc(ix++,iy).west());
			add(month24th,GridC.getc(ix,iy++).west());
			ix=0;
			add(month25th,GridC.getc(ix++,iy).west());
			add(month26th,GridC.getc(ix++,iy).west());
			add(month27th,GridC.getc(ix++,iy).west());
			add(month28th,GridC.getc(ix++,iy).west());
			add(month29th,GridC.getc(ix++,iy).west());
			add(month30th,GridC.getc(ix++,iy).west());
			add(month31st,GridC.getc(ix++,iy).west());
			return;
		}
		@Override
		public void actionPerformed (ActionEvent e){
			JRadioButton button = (JRadioButton)e.getSource();
			String day = button.getText();
			if (day.contains("Monday")) {setResult(Constants.SCHFIRSTMON);return;}
			if (day.contains("Friday")) {setResult(Constants.SCHLASTFRI);return;}
			if (day.contains("Day")) {setResult(Constants.SCHLASTDAY);return;}
			if (day.equals("1st")) {setResult(Constants.SCHMONTHDAY+"01");return;}
			if (day.equals("2nd")) {setResult(Constants.SCHMONTHDAY+"02");return;}
			if (day.equals("3rd")) {setResult(Constants.SCHMONTHDAY+"03");return;}
			if (day.equals("4th")) {setResult(Constants.SCHMONTHDAY+"04");return;}
			if (day.equals("5th")) {setResult(Constants.SCHMONTHDAY+"05");return;}
			if (day.equals("6th")) {setResult(Constants.SCHMONTHDAY+"06");return;}
			if (day.equals("7th")) {setResult(Constants.SCHMONTHDAY+"07");return;}
			if (day.equals("8th")) {setResult(Constants.SCHMONTHDAY+"08");return;}
			if (day.equals("9th")) {setResult(Constants.SCHMONTHDAY+"09");return;}
			if (day.equals("10th")) {setResult(Constants.SCHMONTHDAY+"10");return;}
			if (day.equals("11th")) {setResult(Constants.SCHMONTHDAY+"11");return;}
			if (day.equals("12th")) {setResult(Constants.SCHMONTHDAY+"12");return;}
			if (day.equals("13th")) {setResult(Constants.SCHMONTHDAY+"13");return;}
			if (day.equals("14th")) {setResult(Constants.SCHMONTHDAY+"14");return;}
			if (day.equals("15th")) {setResult(Constants.SCHMONTHDAY+"15");return;}
			if (day.equals("16th")) {setResult(Constants.SCHMONTHDAY+"16");return;}
			if (day.equals("17th")) {setResult(Constants.SCHMONTHDAY+"17");return;}
			if (day.equals("18th")) {setResult(Constants.SCHMONTHDAY+"18");return;}
			if (day.equals("19th")) {setResult(Constants.SCHMONTHDAY+"19");return;}
			if (day.equals("20th")) {setResult(Constants.SCHMONTHDAY+"20");return;}
			if (day.equals("21st")) {setResult(Constants.SCHMONTHDAY+"21");return;}
			if (day.equals("22nd")) {setResult(Constants.SCHMONTHDAY+"22");return;}
			if (day.equals("23rd")) {setResult(Constants.SCHMONTHDAY+"23");return;}
			if (day.equals("24th")) {setResult(Constants.SCHMONTHDAY+"24");return;}
			if (day.equals("25th")) {setResult(Constants.SCHMONTHDAY+"25");return;}
			if (day.equals("26th")) {setResult(Constants.SCHMONTHDAY+"26");return;}
			if (day.equals("27th")) {setResult(Constants.SCHMONTHDAY+"27");return;}
			if (day.equals("28th")) {setResult(Constants.SCHMONTHDAY+"28");return;}
			if (day.equals("29th")) {setResult(Constants.SCHMONTHDAY+"29");return;}
			if (day.equals("30th")) {setResult(Constants.SCHMONTHDAY+"30");return;}
			if (day.equals("31st")) {setResult(Constants.SCHMONTHDAY+"31");return;}
		}
		private void setResult(String resultp){
			resultParam = resultp;
		}
		@Override
		public boolean validateFields() {
			if (monthFirstMon.isSelected())return true;
			if (monthLastFri.isSelected())return true;
			if (monthLastDay.isSelected())return true;
			if (month1st.isSelected())return true;
			if (month2nd.isSelected())return true;
			if (month3rd.isSelected())return true;
			if (month4th.isSelected())return true;
			if (month5th.isSelected())return true;
			if (month6th.isSelected())return true;
			if (month7th.isSelected())return true;
			if (month8th.isSelected())return true;
			if (month9th.isSelected())return true;
			if (month10th.isSelected())return true;
			if (month11th.isSelected())return true;
			if (month12th.isSelected())return true;
			if (month13th.isSelected())return true;
			if (month14th.isSelected())return true;
			if (month15th.isSelected())return true;
			if (month16th.isSelected())return true;
			if (month17th.isSelected())return true;
			if (month18th.isSelected())return true;
			if (month19th.isSelected())return true;
			if (month20th.isSelected())return true;
			if (month21st.isSelected())return true;
			if (month22nd.isSelected())return true;
			if (month23rd.isSelected())return true;
			if (month24th.isSelected())return true;
			if (month25th.isSelected())return true;
			if (month26th.isSelected())return true;
			if (month27th.isSelected())return true;
			if (month28th.isSelected())return true;
			if (month29th.isSelected())return true;
			if (month30th.isSelected())return true;
			if (month31st.isSelected())return true;
			JOptionPane.showMessageDialog(null, "Please select an option or a specific day to run");
			return false;
	}
	}
	private class setupQuarterly extends DetailPanel implements ActionListener{
		private String crntMonth;
		private String crntParam;
		private String crntDay;
		public setupQuarterly (String crntParamp) {
			crntParam = crntParamp;
			setResult(crntParam);
			setLayout(new GridBagLayout());
			quarterlyGroup = new ButtonGroup();
			quarterlyGroup.add (quarterFirst);
			quarterlyGroup.add (quarterLast);
			quarterlyGroup.add (quarterSpecific);
			quarterlyGroupMonth = new ButtonGroup();
			quarterlyGroupMonth.add (quarterMonth1);
			quarterlyGroupMonth.add (quarterMonth2);
			quarterlyGroupMonth.add (quarterMonth3);
			quarterlyGroupDay = new ButtonGroup();
			quarterlyGroupDay.add (quarter1st);
			quarterlyGroupDay.add (quarter2nd);
			quarterlyGroupDay.add (quarter3rd);
			quarterlyGroupDay.add (quarter4th);
			quarterlyGroupDay.add (quarter5th);
			quarterlyGroupDay.add (quarter6th);
			quarterlyGroupDay.add (quarter7th);
			quarterlyGroupDay.add (quarter8th);
			quarterlyGroupDay.add (quarter9th);
			quarterlyGroupDay.add (quarter10th);
			quarterlyGroupDay.add (quarter11th);
			quarterlyGroupDay.add (quarter12th);
			quarterlyGroupDay.add (quarter13th);
			quarterlyGroupDay.add (quarter14th);
			quarterlyGroupDay.add (quarter15th);
			quarterlyGroupDay.add (quarter16th);
			quarterlyGroupDay.add (quarter17th);
			quarterlyGroupDay.add (quarter18th);
			quarterlyGroupDay.add (quarter19th);
			quarterlyGroupDay.add (quarter20th);
			quarterlyGroupDay.add (quarter21st);
			quarterlyGroupDay.add (quarter22nd);
			quarterlyGroupDay.add (quarter23rd);
			quarterlyGroupDay.add (quarter24th);
			quarterlyGroupDay.add (quarter25th);
			quarterlyGroupDay.add (quarter26th);
			quarterlyGroupDay.add (quarter27th);
			quarterlyGroupDay.add (quarter28th);
			quarterlyGroupDay.add (quarter29th);
			quarterlyGroupDay.add (quarter30th);
			quarterlyGroupDay.add (quarter31st);
			disableButtons();
			if(crntParam.equals(Constants.SCHQUARTFIRST)) quarterFirst.setSelected(true);
			if(crntParam.equals(Constants.SCHQUARTLAST)) quarterLast.setSelected(true);
			if(crntParam.contains(Constants.SCHQUARTDATE)) { 
				enableButtons();
				quarterSpecific.setSelected(true);
				quarterMonth1.setSelected(true);
				quarter1st.setSelected(true);
				crntMonth = crntParam.substring(Constants.SCHQUARTDATE.length(),
						  Constants.SCHQUARTDATE.length()+1);
				switch (crntMonth) {
				case "1": quarterMonth1.setSelected(true); crntMonth = "1";break;
				case "2": quarterMonth2.setSelected(true); crntMonth = "2";break;
				case "3": quarterMonth3.setSelected(true); crntMonth = "3";break;
				}
				crntDay = crntParam.substring(Constants.SCHQUARTDATE.length()+1);
				switch (crntDay){
				case "01" : quarter1st.setSelected(true);break;
				case "02" : quarter2nd.setSelected(true);break;
				case "03" : quarter3rd.setSelected(true);break;
				case "04" : quarter4th.setSelected(true);break;
				case "05" : quarter5th.setSelected(true);break;
				case "06" : quarter6th.setSelected(true);break;
				case "07" : quarter7th.setSelected(true);break;
				case "08" : quarter8th.setSelected(true);break;
				case "09" : quarter9th.setSelected(true);break;
				case "10" : quarter10th.setSelected(true);break;
				case "11" : quarter11th.setSelected(true);break;
				case "12" : quarter12th.setSelected(true);break;
				case "13" : quarter13th.setSelected(true);break;
				case "14" : quarter14th.setSelected(true);break;
				case "15" : quarter15th.setSelected(true);break;
				case "16" : quarter16th.setSelected(true);break;
				case "17" : quarter17th.setSelected(true);break;
				case "18" : quarter18th.setSelected(true);break;
				case "19" : quarter19th.setSelected(true);break;
				case "20" : quarter20th.setSelected(true);break;
				case "21" : quarter21st.setSelected(true);break;
				case "22" : quarter22nd.setSelected(true);break;
				case "23" : quarter23rd.setSelected(true);break;
				case "24" : quarter24th.setSelected(true);break;
				case "25" : quarter25th.setSelected(true);break;
				case "26" : quarter26th.setSelected(true);break;
				case "27" : quarter27th.setSelected(true);break;
				case "28" : quarter28th.setSelected(true);break;
				case "29" : quarter29th.setSelected(true);break;
				case "30" : quarter30th.setSelected(true);break;
				case "31" : quarter31st.setSelected(true);break;
				}
			}
			quarterFirst.addActionListener(this);
			quarterLast.addActionListener(this);
			quarterSpecific.addActionListener(this);
			quarterMonth1.addActionListener(this);
			quarterMonth2.addActionListener(this);
			quarterMonth3.addActionListener(this);
			quarter1st.addActionListener(this);
			quarter2nd.addActionListener(this);
			quarter3rd.addActionListener(this);
			quarter4th.addActionListener(this);
			quarter5th.addActionListener(this);
			quarter6th.addActionListener(this);
			quarter7th.addActionListener(this);
			quarter8th.addActionListener(this);
			quarter9th.addActionListener(this);
			quarter10th.addActionListener(this);
			quarter11th.addActionListener(this);
			quarter12th.addActionListener(this);
			quarter13th.addActionListener(this);
			quarter14th.addActionListener(this);
			quarter15th.addActionListener(this);
			quarter16th.addActionListener(this);
			quarter17th.addActionListener(this);
			quarter18th.addActionListener(this);
			quarter19th.addActionListener(this);
			quarter20th.addActionListener(this);
			quarter21st.addActionListener(this);
			quarter22nd.addActionListener(this);
			quarter23rd.addActionListener(this);
			quarter24th.addActionListener(this);
			quarter25th.addActionListener(this);
			quarter26th.addActionListener(this);
			quarter27th.addActionListener(this);
			quarter28th.addActionListener(this);
			quarter29th.addActionListener(this);
			quarter30th.addActionListener(this);
			quarter31st.addActionListener(this);
			int ix = 0;
			int iy =0;
			JLabel dayLbl = new JLabel("<html><b>  Select the day of the quarter to run  </b></html>");
			add(dayLbl,GridC.getc(ix,iy++).colspan(4));
			add(quarterFirst,GridC.getc(ix,iy).west().colspan(2));
			add(quarterLast,GridC.getc(ix+2,iy).west().colspan(2));
			add(quarterSpecific,GridC.getc(ix+4,iy++).west().colspan(2));
			ix=0;
			add(quarterMonth1,GridC.getc(ix,iy).west().colspan(2));
			add(quarterMonth2,GridC.getc(ix+2,iy).west().colspan(2));
			add(quarterMonth3,GridC.getc(ix+4,iy++).west().colspan(2));
			ix=0;
			add(quarter1st,GridC.getc(ix++,iy).west());
			add(quarter2nd,GridC.getc(ix++,iy).west());
			add(quarter3rd,GridC.getc(ix++,iy).west());
			add(quarter4th,GridC.getc(ix++,iy).west());
			add(quarter5th,GridC.getc(ix++,iy).west());
			add(quarter6th,GridC.getc(ix++,iy).west());
			add(quarter7th,GridC.getc(ix++,iy).west());
			add(quarter8th,GridC.getc(ix,iy++).west());
			ix=0;
			add(quarter9th,GridC.getc(ix++,iy).west());
			add(quarter10th,GridC.getc(ix++,iy).west());
			add(quarter11th,GridC.getc(ix++,iy).west());
			add(quarter12th,GridC.getc(ix++,iy).west());
			add(quarter13th,GridC.getc(ix++,iy).west());
			add(quarter14th,GridC.getc(ix++,iy).west());
			add(quarter15th,GridC.getc(ix++,iy).west());
			add(quarter16th,GridC.getc(ix,iy++).west());
			ix=0;
			add(quarter17th,GridC.getc(ix++,iy).west());
			add(quarter18th,GridC.getc(ix++,iy).west());
			add(quarter19th,GridC.getc(ix++,iy).west());
			add(quarter20th,GridC.getc(ix++,iy).west());
			add(quarter21st,GridC.getc(ix++,iy).west());
			add(quarter22nd,GridC.getc(ix++,iy).west());
			add(quarter23rd,GridC.getc(ix++,iy).west());
			add(quarter24th,GridC.getc(ix,iy++).west());
			ix=0;
			add(quarter25th,GridC.getc(ix++,iy).west());
			add(quarter26th,GridC.getc(ix++,iy).west());
			add(quarter27th,GridC.getc(ix++,iy).west());
			add(quarter28th,GridC.getc(ix++,iy).west());
			add(quarter29th,GridC.getc(ix++,iy).west());
			add(quarter30th,GridC.getc(ix++,iy).west());
			add(quarter31st,GridC.getc(ix++,iy).west());
			return;
		}
		@Override
		public void actionPerformed (ActionEvent e){
			JRadioButton button = (JRadioButton)e.getSource();
			String day = button.getText();
			if (day.contains("First")) {disableButtons();setResult(Constants.SCHQUARTFIRST);return;}
			if (day.contains("Last")) {disableButtons();setResult(Constants.SCHQUARTLAST);return;}
			if (day.contains("Set")) {
				enableButtons();
				setResult(Constants.SCHQUARTDATE+"101");
				quarterMonth1.setSelected(true);
				quarter1st.setSelected(true);
				return;
			}
			if (day.equals("Month 1")){setMonth("1");return;}
			if (day.equals("Month 2")){setMonth("2");return;}
			if (day.equals("Month 3")){setMonth("3");return;}
			if (day.equals("1st")) {setDay("01");return;}
			if (day.equals("2nd")) {setDay("02");return;}
			if (day.equals("3rd")) {setDay("03");return;}
			if (day.equals("4th")) {setDay("04");return;}
			if (day.equals("5th")) {setDay("05");return;}
			if (day.equals("6th")) {setDay("06");return;}
			if (day.equals("7th")) {setDay("07");return;}
			if (day.equals("8th")) {setDay("08");return;}
			if (day.equals("9th")) {setDay("09");return;}
			if (day.equals("10th")) {setDay("10");return;}
			if (day.equals("11th")) {setDay("11");return;}
			if (day.equals("12th")) {setDay("12");return;}
			if (day.equals("13th")) {setDay("13");return;}
			if (day.equals("14th")) {setDay("14");return;}
			if (day.equals("15th")) {setDay("15");return;}
			if (day.equals("16th")) {setDay("16");return;}
			if (day.equals("17th")) {setDay("17");return;}
			if (day.equals("18th")) {setDay("18");return;}
			if (day.equals("19th")) {setDay("19");return;}
			if (day.equals("20th")) {setDay("20");return;}
			if (day.equals("21st")) {setDay("21");return;}
			if (day.equals("22nd")) {setDay("22");return;}
			if (day.equals("23rd")) {setDay("23");return;}
			if (day.equals("24th")) {setDay("24");return;}
			if (day.equals("25th")) {setDay("25");return;}
			if (day.equals("26th")) {setDay("26");return;}
			if (day.equals("27th")) {setDay("27");return;}
			if (day.equals("28th")) {setDay("28");return;}
			if (day.equals("29th")) {setDay("29");return;}
			if (day.equals("30th")) {setDay("30");return;}
			if (day.equals("31st")) {setDay("31");return;}
		}
		private void setResult(String resultp){
			resultParam = resultp;
		}
		private void setDay(String dayp){
			crntDay = dayp;
			setResult(Constants.SCHQUARTDATE+crntMonth+crntDay);
			
		}
		private void setMonth(String monthp){
			crntMonth = monthp;
			setResult(Constants.SCHQUARTDATE+crntMonth+crntDay);
		}
		private void enableButtons() {
			Enumeration<AbstractButton> enumeration = quarterlyGroupMonth.getElements();
			while (enumeration.hasMoreElements()) {
			    enumeration.nextElement().setEnabled(true);
			}
			Enumeration<AbstractButton> enumeration2 = quarterlyGroupDay.getElements();
			while (enumeration2.hasMoreElements()) {
			    enumeration2.nextElement().setEnabled(true);
			}			
		}
		private void disableButtons() {
			Enumeration<AbstractButton> enumeration = quarterlyGroupMonth.getElements();
			while (enumeration.hasMoreElements()) {
			    enumeration.nextElement().setEnabled(false);
			}
			Enumeration<AbstractButton> enumeration2 = quarterlyGroupDay.getElements();
			while (enumeration2.hasMoreElements()) {
			    enumeration2.nextElement().setEnabled(false);
			}			
		}
		@Override
		public boolean validateFields() {
			if (quarterFirst.isSelected())return true;
			if (quarterLast.isSelected())return true;
			if (!quarterSpecific.isSelected()) {
				JOptionPane.showMessageDialog(null, "Please select First Day, Last Day or Set Date");
				return false;
			}
			if (quarterMonth1.isSelected())return true;
			if (quarterMonth2.isSelected())return true;
			if (!quarterMonth3.isSelected()){
				JOptionPane.showMessageDialog(null, "Please select which Month the date is for");
				return false;
			}
			if (quarter1st.isSelected())return true;
			if (quarter2nd.isSelected())return true;
			if (quarter3rd.isSelected())return true;
			if (quarter4th.isSelected())return true;
			if (quarter5th.isSelected())return true;
			if (quarter6th.isSelected())return true;
			if (quarter7th.isSelected())return true;
			if (quarter8th.isSelected())return true;
			if (quarter9th.isSelected())return true;
			if (quarter10th.isSelected())return true;
			if (quarter11th.isSelected())return true;
			if (quarter12th.isSelected())return true;
			if (quarter13th.isSelected())return true;
			if (quarter14th.isSelected())return true;
			if (quarter15th.isSelected())return true;
			if (quarter16th.isSelected())return true;
			if (quarter17th.isSelected())return true;
			if (quarter18th.isSelected())return true;
			if (quarter19th.isSelected())return true;
			if (quarter20th.isSelected())return true;
			if (quarter21st.isSelected())return true;
			if (quarter22nd.isSelected())return true;
			if (quarter23rd.isSelected())return true;
			if (quarter24th.isSelected())return true;
			if (quarter25th.isSelected())return true;
			if (quarter26th.isSelected())return true;
			if (quarter27th.isSelected())return true;
			if (quarter28th.isSelected())return true;
			if (quarter29th.isSelected())return true;
			if (quarter30th.isSelected())return true;
			if (quarter31st.isSelected())return true;
			JOptionPane.showMessageDialog(null, "Please select the day of the month");
			return false;
		}
	}	
	private class TransRadio extends JRadioButton {
		public TransRadio (String label){
			super(label);
			setOpaque(false);
		}
	}
}
