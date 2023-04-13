/*
 * SortView.java
 *
 * Created on Oct 20, 2013
 * Last Modified: 27th March 2023
 * Last Modified By: Stuart Beesley
 *
 *
 */
package com.moneydance.modules.features.debtinsights.ui.acctview;

import javax.swing.Icon;

import com.moneydance.awt.ArrowIcon;
import com.moneydance.modules.features.debtinsights.Strings;


public enum SortView implements IconToggle {
    ASC(Strings.BLANK, new ArrowIcon(ArrowIcon.NORTH, true), 1),
    DESC(Strings.BLANK, new ArrowIcon(ArrowIcon.SOUTH, true), -1),
    OFF(Strings.BLANK, null, 0);

    private final String label;
    private final Icon icon;
    public int direction;

    SortView(String label, Icon icon, int order) {
        this.label = label;
        this.icon = icon;
        this.direction = order;
    }

    @Override
    public String getLabel() {
        return this.label;
    }

    @Override
    public SortView getNextState() {
        int i = ordinal() + 1;
        return values()[i % values().length];
    }

    @Override
    public Icon getIcon() {
        return this.icon;
    }

    public SortView toggleOrder() {
        SortView order = getNextState();
        return (order == OFF ? order.getNextState() : order);
    }


    @Override
    public IconToggle getState(DebtAccountView acctView) {
        return (acctView.getAcctComparator() != null
                ? acctView.getAcctComparator().getOrder()
                : null);
    }

}
