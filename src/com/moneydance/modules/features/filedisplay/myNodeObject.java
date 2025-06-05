package com.moneydance.modules.features.filedisplay;

import com.infinitekind.moneydance.model.Account;
/*
 * Class used to hold user data of each node within the tree
 */
public class myNodeObject {
		private int mynodetype;
		private String mynodename;
		private Object myobject;
		public myNodeObject(int nodetype, String nodename) {
			mynodetype = nodetype;
			mynodename = nodename;
		}
		public void setnodetype (int nodetype) {
			mynodetype = nodetype;
		}
		public int getnodetype () {
			return mynodetype;
		}
		public void setaccount (Account acct) {
			myobject = acct;
		}
		public void setobject (Object obj) {
			myobject = obj;
		}
		public Account getaccount () {
			return (Account)myobject;
		}
		public Object getobject () {
			return myobject;
		}
		public String toString() {
			return mynodename;
		}
			
}
