/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import java.util.Hashtable;
import java.util.Observable;

import com.moneydance.apps.md.controller.Main;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.infinitekind.util.StreamTable;
import java.awt.Color;

/**
 * This preferences class contains the values the user can control in the
 * application. It serves as a facade abstracting Moneydance's
 * <code>UserPreferences</code> (received from the
 * <code>FeatureModuleContext</code>).
 */
public final class BudgetPreferences extends Observable {
	private         Main            mainContext;
    private         UserPreferences userPreferences;

    private         StreamTable     defaults;
    private final   StreamTable     nullDefaults;
    private         StreamTable     publishDefaults;
    private         StreamTable     publishDetails;
    
    /**
     * The constructor must be called exactly once before using the only
     * instance of this class.
     */
    BudgetPreferences() {
    	this.nullDefaults = new StreamTable();
        this.nullDefaults.put("budget", "");
        this.nullDefaults.put("large", "");
        this.nullDefaults.put("taxIsIncome", "");

        this.publishDefaults = new StreamTable();
        this.publishDefaults.put("ftpHost", "");
        this.publishDefaults.put("ftpUserName", "");
        this.publishDefaults.put("ftpPassword", "");
        this.publishDefaults.put("ftpRemoteDirectory", "");
    }

    public void reload() {
        this.notifyObservers(Boolean.TRUE);
    }

    public void setContext(final FeatureModuleContext context) {
    	this.mainContext = (com.moneydance.apps.md.controller.Main)
                context;
        this.userPreferences = this.mainContext.getPreferences();
        
        this.load();
    }

    private void load(){
    	this.defaults = this.getUserPreferences().getTableSetting(
                "ragebudget.default",
                this.nullDefaults);
    	
    	this.publishDetails = this.getUserPreferences().getTableSetting(
                "ragebudget.publish",
                this.publishDefaults);
    }
    
    private UserPreferences getUserPreferences() {
        if (this.userPreferences == null) {
            this.notifyObservers(Boolean.FALSE);
        }
        return this.userPreferences;
    }

    public Color getBackground() {
        int backgroundValue = this.getUserPreferences().getIntSetting(UserPreferences.GUI_HOMEPG_BG, -1);
        return new Color(backgroundValue);
    }
    
    public Color getAltBackground() {
        int backgroundValue = this.getUserPreferences().getIntSetting(UserPreferences.GUI_HOMEPGALT_BG, -657931);
        return new Color(backgroundValue);
    }
    
    /*
    public void setAllWritablePreferencesToNull() {
        this.savePublishDetails((Hashtable<String, String>) null);
    }
    */
    
    protected String getDefaults(final String key) {
        return this.defaults.getStr(key, null);
    }
    
    protected String getPublishDetails(final String key) {
        return this.publishDetails.getStr(key, null);
    }

    private void savePreferences(){
    	try {
    		this.mainContext.savePreferences();
		} catch (Exception e) {
			e.printStackTrace();
		}
    }
    
    protected void saveDefaults(final Hashtable<String, String> hashtable) {
        if (hashtable != null) {
        	//thisTable = new StreamTable();
        	this.defaults.merge(hashtable);
        }

        this.getUserPreferences().setSetting("ragebudget.default", this.defaults);
        savePreferences();
    }
    
    protected void savePublishDetails(final Hashtable<String, String> hashtable) {
        StreamTable thisTable = null;
        if (hashtable != null) {
        	thisTable = new StreamTable();
            thisTable.merge(hashtable);
        }

        this.getUserPreferences().setSetting("ragebudget.publish", thisTable);
        savePreferences();
    }
 
}
