package com.moneydance.modules.features.mrbutil;

import java.util.Map.Entry;

public class MRBMyEntry implements Entry<String, MRBListItem>{
	  private final String key;
	    private MRBListItem value;
	    public MRBMyEntry(final String key) {
	        this.key = key;
	    }
	    public MRBMyEntry(final String key, final MRBListItem value) {
	        this.key = key;
	        this.value = value;
	    }
	    @Override
		public String getKey() {
	        return key;
	    }
	    @Override
		public MRBListItem getValue() {
	        return value;
	    }
	    @Override
		public MRBListItem setValue(final MRBListItem valuep) {
	        final MRBListItem oldValue = this.value;
	        this.value = valuep;
	        return oldValue;
	    }	
}
