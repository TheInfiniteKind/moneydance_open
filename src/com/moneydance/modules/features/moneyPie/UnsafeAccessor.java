package com.moneydance.modules.features.moneyPie;

import com.moneydance.apps.md.controller.FeatureModuleContext; 
import com.infinitekind.moneydance.model.*; 
import com.moneydance.awt.DatePicker;
import java.awt.Color; 

public class UnsafeAccessor { 
    private final com.moneydance.apps.md.view.gui.MoneydanceGUI mdg; 
 
    public UnsafeAccessor(FeatureModuleContext fmc) { 
       com.moneydance.apps.md.controller.Main main 
           = (com.moneydance.apps.md.controller.Main) fmc; 
       this.mdg = (com.moneydance.apps.md.view.gui.MoneydanceGUI) 
           main.getUI(); 
    } 
 
    public void showTxn(AbstractTxn txn) { 
       mdg.showTxn(txn); 
    } 
 
    public Color stripeColor() { 
       return mdg.getColors().homePageAltBG; 
    } 
 
    public char getDecimalChar() { 
       return mdg.getMain().getPreferences().getDecimalChar(); 
    } 
    
    public DatePicker getDatePicker(int dateInt)
    {
    	return new DatePicker(this.mdg, dateInt);
    }
} 
