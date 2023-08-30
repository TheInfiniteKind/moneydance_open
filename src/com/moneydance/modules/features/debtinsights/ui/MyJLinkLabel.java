// This simply extends JLinkLabel and stops the widths / heights from constantly changing...

package com.moneydance.modules.features.debtinsights.ui;

import com.moneydance.awt.JLinkLabel;

import javax.swing.*;
import java.awt.*;

public class MyJLinkLabel extends JLinkLabel {
    private int maxWidth = -1;
    private int maxHeight =  -1;

    public MyJLinkLabel(Action action) {
        super(action);
    }

    public MyJLinkLabel(String text, Icon icon, Object linkTarget, int alignment) {
        super(text, icon, linkTarget, alignment);
    }

    public MyJLinkLabel(String text, Object linkTarget, int alignment) {
        super(text, linkTarget, alignment);
    }
    
    @Override
    public Dimension getPreferredSize() {
        Dimension dim = super.getPreferredSize();
        this.maxWidth = Math.max(this.maxWidth, dim.width);
        dim.width = this.maxWidth;
        this.maxHeight = Math.max(this.maxHeight, dim.height);
        dim.height = this.maxHeight;
        return dim;
    }
}




