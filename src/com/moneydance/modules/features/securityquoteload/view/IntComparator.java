package com.moneydance.modules.features.securityquoteload.view;

import java.util.Comparator;

public class IntComparator implements Comparator<String> {
    public int compare(String o1, String o2) {
        Integer d1;
        Integer d2;
        if (o1.isBlank() || o2.isBlank())
            return 0;
        try {
            d1= Integer.valueOf(o1);
            d2=Integer.valueOf(o2);
        }
        catch (NumberFormatException e) {
            return 0;
        }
        return d1.compareTo(d2);
    }
}
