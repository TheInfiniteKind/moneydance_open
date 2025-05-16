package com.moneydance.modules.features.securityquoteload.view;

import com.moneydance.modules.features.securityquoteload.Main;

import java.util.Comparator;

public class DoubleComparator implements Comparator<String> {
    public int compare(String o1, String o2) {
        if (o1.isBlank())
            o1="-999999999.99";
        if (o2.isBlank())
            o2="-999999999.99";
        try {
            Double d1 = Double.valueOf(stripNonNum(o1));
            Double d2=Double.valueOf(stripNonNum(o2));
            return d1.compareTo(d2);
        }
        catch (NumberFormatException e) {
            return 0;
        }
    }
    private String stripNonNum(String number) {
        String output="";
        for (int i=0;i<number.length();i++) {
            if (number.charAt(i)== Main.decimalChar) {
                output+=number.charAt(i);
                continue;
            }
            switch (number.charAt(i)) {
                case '0':
                case '1':
                case '2':
                case '3':
                case '4':
                case '5':
                case '6':
                case '7':
                case '8':
                case '9':
                case '-':
                case '+':
                    output+=number.charAt(i);
            }
        }
        return output;
    }
}