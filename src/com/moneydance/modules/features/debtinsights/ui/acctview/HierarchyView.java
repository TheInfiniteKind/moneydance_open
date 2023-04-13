/*
 * HierarchyView.java
 *
 * Created on Oct 20, 2013
 * Last Modified: 27th March 2023
 * Last Modified By: Stuart Beesley
 *
 *
 */

package com.moneydance.modules.features.debtinsights.ui.acctview;

import javax.swing.Icon;
import com.moneydance.apps.md.view.gui.MDImages;

public enum HierarchyView implements IconToggle {
    EXPAND_ALL("+", "/com/moneydance/apps/md/view/gui/images/plus-8.png"),              // \u2795"),
    COLLAPSE_ALL("-", "/com/moneydance/apps/md/view/gui/images/minus-8.png"),          // \u2796"),
    FLATTEN("\u21DA", "/com/moneydance/apps/md/view/gui/icons/close_toolbar_14.png");   // \u20E0

    private final String label;
    private final Icon icon;

    HierarchyView(String label, String iconPath) {
        this.label = label;
        this.icon = MDImages.getMDIcon(iconPath);
    }

//    public static HierarchyView getNextState(HierarchyView view) {
//        int i = view.ordinal() + 1;
//        return values()[i % 3];
//    }

    @Override
    public HierarchyView getNextState() {
        int i = ordinal() + 1;
        return values()[i % values().length];
    }

    @Override
    public String getLabel() {
        return this.label;
    }

    @Override
    public Icon getIcon() {
        return this.icon;
    }

    @Override
    public IconToggle getState(DebtAccountView acctView) {
        return acctView.getHierarchyView();
    }
}


