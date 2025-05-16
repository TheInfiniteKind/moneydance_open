package com.moneydance.modules.features.securityquoteload.view;

import com.moneydance.modules.features.securityquoteload.Main;

import java.util.Comparator;

public class DateComparator implements Comparator<String> {
    public int compare(String o1, String o2) {
        if (o1.endsWith("++"))
            o1=o1.substring(0,o1.length()-2);
        if (o2.endsWith("++"))
            o2=o2.substring(0,o2.length()-2);
        Integer i1 = 0;
        Integer i2 = 0;;
        if (o1.isBlank())
            i1=19000101;
        else {
            i1= Main.cdate.parseInt(o1);
        }
        if (o2.isBlank())
            i2=19000101;
        else {
            i2=Main.cdate.parseInt(o2);
        }
        return i1.compareTo(i2);
    }
}
