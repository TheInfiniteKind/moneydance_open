/************************************************************\
 *        Copyright 2017 The Infinite Kind, Limited         *
\************************************************************/

package com.moneydance.modules.features.balpred;

import com.moneydance.awt.*;
import com.moneydance.awt.graph.*;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.*;
import java.io.*;

public abstract class BalPredGraph
  extends JComponent
  implements MouseMotionListener,
             MouseListener
{
  private Image bufferImage=null;
  protected Image graphImage=null;
  protected Dimension graphSize=null;
  protected Graphics bufferG;
  private Point mousePosition=null;
  private boolean dirty=true;
  private Resources rr = null;
  protected GraphModel model;
  
  /** Construct a graph with the specified initial size. */
  public BalPredGraph (GraphModel model, Resources rr) {
    this.model = model;
    this.rr = rr;
    setBackground(Color.white);
    graphSize = new Dimension(0,0);
    addMouseListener(this);
    addMouseMotionListener(this);
    setBackground(Color.white);
    setOpaque(true);
    repaint();
  }
  
  public GraphModel getModel() {
    return model;
  }

  public Resources getResources() {
    return rr;
  }

  protected void setNewModel(GraphModel model) {
    this.model = model;
    renderGraph();
  }

  /** Save this graph as a GIF image to the specified output stream */
  public synchronized void writeGIF(OutputStream out) throws AWTException, IOException {
    (new GIFEncoder(bufferImage)).Write(out);
  }

  public void setBounds(int x, int y, int w, int h) {
    super.setBounds(x,y,w,h);
    this.graphSize = getSize();
    renderGraph();
  }

  /** Redraw the graph onto the buffered image and update the screen. */
  public synchronized final void renderGraph() {
    if(graphSize.width<=0 || graphSize.height<=0)
      return;
    graphImage = createImage(graphSize.width, graphSize.height);
    if(graphImage==null)
      return;
    bufferG = graphImage.getGraphics();
    super.paint(bufferG);
    drawGraph(bufferG, graphSize.width, graphSize.height, false);
    bufferImage = createImage(graphSize.width, graphSize.height);
    bufferImage.getGraphics().drawImage(graphImage, 0, 0, null);
    repaint();
  }

  /** This method must be over-ridden by the different types of graph in order to
    * render the given datasets onto the graphImage. */
  public abstract void drawGraph(Graphics g, int width, int height, boolean printing);
  
  /** ignore this.  Required to receive mouse events. */
  public void mouseClicked(MouseEvent e) { }
  /** ignore this.  Required to receive mouse events. */
  public void mousePressed(MouseEvent e) { }
  /** ignore this.  Required to receive mouse events. */
  public void mouseReleased(MouseEvent e) { }

  /** ignore this.  Required to receive mouse events. */
  public void mouseMoved(MouseEvent e) {
    mousePosition = e.getPoint();
    repaint();
  }

  /** ignore this.  Required to receive mouse events. */
  public void mouseDragged(MouseEvent e) {
    mousePosition = e.getPoint();
    repaint();
  }

  /** ignore this.  Required to receive mouse events. */
  public void mouseEntered(MouseEvent e) {
    mousePosition = e.getPoint();
    repaint();
  }

  /** ignore this.  Required to receive mouse events. */
  public void mouseExited(MouseEvent e) {
    mousePosition=null;
    repaint();
  }
  
  public final void paint(Graphics g) {
    update(g);
  }

  public final void update(Graphics g) {
    if(graphImage==null || bufferImage==null) {
      renderGraph();
      if(graphImage==null || bufferImage==null)
        return;
    }
    if(mousePosition!=null) {
      Graphics bufferGraphics = bufferImage.getGraphics();
      bufferGraphics.drawImage(graphImage,0,0,null);
      g.drawImage(bufferImage,0,0,null);
    } else {
      g.drawImage(graphImage,0,0,null);
    }
  }

  public Dimension getPreferredSize() {
    return new Dimension(300,300);
  }

  public abstract int getLeftMargin();
  public abstract int getBottomMargin();
  public abstract double getXScale();
  public abstract double getYScale();
  public abstract double getMinX();
  public abstract double getMinY();
}

