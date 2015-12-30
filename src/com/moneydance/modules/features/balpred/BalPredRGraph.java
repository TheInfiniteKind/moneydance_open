/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.balpred;

import com.moneydance.awt.graph.*;
import java.awt.*;
import java.awt.event.*;
import java.util.*;

public class BalPredRGraph 
  extends BalPredGraph 
{
  protected int leftMargin=80;
  protected int rightMargin=40;
  protected int topMargin=10;
  protected int bottomMargin=30;
  protected int lineWidth = 1;
  protected double xScale = 1.0;
  protected double yScale = 1.0;
  protected double minX = 0;
  protected double minY = 0;
  protected double maxX = 0;
  protected double maxY = 0;
  
  public BalPredRGraph(LineGraphModel model, Resources rr) {
    super(model,rr);
  }

  public void setModel(LineGraphModel model) {
    super.setNewModel(model);
  }

  public int getLeftMargin() {
    return leftMargin;
  }

  public int getBottomMargin() {
    return bottomMargin;
  }

  public double getXScale() {
    return xScale;
  }

  public double getYScale() {
    return yScale;
  }

  public double getMinY() {
    return minY;
  }

  public double getMinX() {
    return minX;
  }

  /** This method actually renders the graph data onto graphImage.
    */
  public synchronized void drawGraph(Graphics g, int w, int h, boolean printing) {
    if(g==null)
      return;

    if(g instanceof Graphics2D) {
      Graphics2D g2 = (Graphics2D)g;
      g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
      g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
    }
    
    g.setColor(Color.white);
    g.fillRect(0,0,w,h);
    
    if(model==null)
      return;

    LineGraphModel model = (LineGraphModel)this.model;
    
    int numSets = model.getDataSetCount();
    int xOffset=0;  // The number of pixels that the coordinates will be shifted for each set.
    int yOffset=0;

    if(numSets<=0)
      return;

    lineWidth = 1;

    FontMetrics fm = g.getFontMetrics();
    leftMargin = 40;
    rightMargin = 20;
    bottomMargin = 20;
    topMargin = 40;

    double yTicks[] = model.getYTickValues(fm.getMaxAscent()+fm.getMaxDescent()+3,
                                           h-bottomMargin-topMargin);

    double xTicks[] = model.getXTickValues();

    if(xTicks==null) xTicks = new double[0];
    if(yTicks==null) yTicks = new double[0];

    minY = model.getMinYValue();
    maxY = model.getMaxYValue();
    minX = model.getMinXValue();
    maxX = model.getMaxXValue();
    
    if(yTicks.length>0) {
      minY = Math.min(yTicks[0], minY);
      maxY = Math.max(yTicks[yTicks.length-1], maxY);
    }
    if(xTicks.length>0) {
      minX = Math.min(xTicks[0], minX);
      maxX = Math.max(xTicks[xTicks.length-1], maxX);
    }

    if(yTicks.length <= 1 || xTicks.length <= 1) {
      return;
    }
    
    leftMargin =
      Math.max(fm.stringWidth(model.getLabelForValue((maxY)))+3,
               Math.max(fm.stringWidth(model.getLabelForValue(minY)+3), leftMargin));
    
    if((h-bottomMargin)<=topMargin || 
       (w-rightMargin)<=leftMargin)
      return;

    double xRange = maxX-minX;
    double yRange = maxY-minY;

    if(xRange==0.0 || yRange==0.0) {
      System.err.println("Nothing to graph - the available range is zero!");
      return;
    }

    xScale = (w-rightMargin-leftMargin)/xRange;
    yScale = (h-bottomMargin-topMargin)/yRange;

    // Draw a few tick marks.
    String tempString;
    int strWidth, strHeight;

    for(int tickNum=0; tickNum < yTicks.length; tickNum++) {
      tempString = model.getLabelForValue(yTicks[tickNum]);
      strWidth = fm.stringWidth(tempString);
      int tickPosition = h-bottomMargin-
        ((h-bottomMargin-topMargin)*tickNum)/(yTicks.length-1);
      g.setColor(Color.black);
      g.drawString(tempString, leftMargin-strWidth-2, tickPosition-2);

      g.setColor(Color.lightGray);
      g.drawLine(2, tickPosition, leftMargin, tickPosition);
      g.drawLine(leftMargin, tickPosition, leftMargin+1,
                 tickPosition);
      g.drawLine(leftMargin+1,
                 tickPosition,
                 w-rightMargin+1,
                 tickPosition);
    }

    // draw the tick marks along the x axis
    int lastTickEnding = -1;
    boolean showTicks = ((w-(rightMargin+leftMargin))/(float)xTicks.length)>=3.0;
    for(int tickNum=0; tickNum < xTicks.length; tickNum++) {
      tempString = model.getLabelForXAxis(xTicks[tickNum]); 
      strHeight = fm.getMaxDescent()+fm.getMaxAscent(); 
      strWidth = fm.stringWidth(tempString);
      int tickPosition = (int)((xTicks[tickNum]-minX)*xScale);
      
      if(tickPosition > lastTickEnding && 
         (tickPosition+strWidth+leftMargin) < (w-rightMargin)) {
        g.drawLine(leftMargin+tickPosition, h-bottomMargin,
                   leftMargin+tickPosition, h-bottomMargin+strHeight+2);
        g.setColor(Color.blue);
        g.drawString(tempString,leftMargin+tickPosition+2,
                     h-bottomMargin+strHeight);
      
        lastTickEnding = tickPosition+strWidth;

        g.setColor(Color.lightGray);
        g.drawLine(leftMargin+tickPosition, h-bottomMargin,
                   leftMargin+tickPosition,
                   h-bottomMargin-1);
        g.drawLine(leftMargin+tickPosition,
                   h-bottomMargin-1,
                   leftMargin+tickPosition,
                   topMargin-1);
      } else if(showTicks) {
        g.setColor(Color.lightGray);
        g.drawLine(leftMargin+tickPosition, h-bottomMargin,
                   leftMargin+tickPosition,
                   h-bottomMargin-1);
        g.drawLine(leftMargin+tickPosition,
                   h-bottomMargin-1,
                   leftMargin+tickPosition,
                   topMargin-1);
      }
    }

    // Draw the axes
    g.setColor(Color.black);
    g.drawLine(leftMargin,topMargin,leftMargin,h-bottomMargin);
    g.drawLine(leftMargin,h-bottomMargin,
               w-rightMargin,h-bottomMargin);
    g.drawLine(leftMargin+20,
               fm.getMaxAscent(),
               leftMargin+60,
               fm.getMaxAscent());
    g.drawString(getResources().getString("two_weeks"),
      leftMargin+70,fm.getMaxDescent()+fm.getMaxAscent());
    g.setColor(Color.blue);
    g.drawLine(leftMargin+20,
               fm.getMaxAscent()+fm.getMaxAscent()+fm.getMaxDescent(),
               leftMargin+60,
               fm.getMaxAscent()+fm.getMaxAscent()+fm.getMaxDescent());
    g.drawString(getResources().getString("future_balance"),
      leftMargin+70,2*(fm.getMaxDescent()+fm.getMaxAscent()));
    
    XYGraphDataSet currentSet = null;
    for(int i=0;i<numSets;i++) {
      currentSet = (XYGraphDataSet)model.getDataSet(i);
      Color currentColor = currentSet.getColor();
      boolean firstVal=true;
      double lastX=0,lastY=0,thisX=0,thisY=0;
      g.setColor(currentColor);
      int numValues = currentSet.getNumValues();
      for(int j=0;j<numValues;j++) {
        g.setColor(Color.black);
        g.drawLine(leftMargin,topMargin,leftMargin,h-bottomMargin);
        g.drawLine(leftMargin,h-bottomMargin,
                   w-rightMargin,h-bottomMargin);
        thisX = leftMargin+(model.getDataSetXValue(i,j)-minX)*xScale;
        thisY = h-bottomMargin-(model.getDataSetYValue(i,j)-minY)*yScale;
        if(!firstVal) {
          g.setColor(currentColor);
          g.drawLine((int)lastX,(int)lastY,(int)thisX,(int)thisY);
        }
        firstVal=false;
        lastX = thisX;
        lastY = thisY;
      }
    }
    
  }
  
}

