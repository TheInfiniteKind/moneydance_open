/*
 * Copyright (c) 2020, Michael Bray.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */
package com.moneydance.modules.features.reportwriter.view;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.FileTime;
import java.util.Date;
import java.util.SortedMap;
import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.google.gson.stream.JsonReader;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;

public class DataDataRow {
	private String name;
	private String fileName;
	private String selectionGroup;
	private SortedMap<String,DataParameter> parameters;
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getSelectionGroup() {
		return selectionGroup;
	}
	public void setSelectionGroup(String selectionGroup) {
		this.selectionGroup = selectionGroup;
	}
	public SortedMap<String, DataParameter> getParameters() {
		return parameters;
	}
	public void setParameters(SortedMap<String, DataParameter> parameters) {
		this.parameters = parameters;
	}
	public boolean loadRow(String name,Parameters paramsp) {
		String dir = paramsp.getDataDirectory();
		fileName = dir+"/"+name+Constants.DATAEXTENSION;
		DataDataRow row;
		try {
			JsonReader reader = new JsonReader(new FileReader(fileName));
			row = new Gson().fromJson(reader,DataDataRow.class);
			reader.close();
			setName(row.getName());
			setSelectionGroup(row.getSelectionGroup());
			setParameters(row.getParameters());
			Main.rwDebugInst.debug("DataDataRow", "loadRow", MRBDebug.DETAILED, "Row loaded "+name);
		}
		catch (JsonParseException e) {
			Main.rwDebugInst.debug("DataDataRow", "loadRow", MRBDebug.DETAILED, "Parse Exception "+e.getMessage());
			return false;
		}
		catch (IOException e){
			return false;
		}
		return true;
	}
	public void touchFile() {
		Path touchFile = Paths.get(fileName);
		try {
			Files.setAttribute(touchFile, "basic:lastAccessTime", FileTime.fromMillis(new Date().getTime()));
		}
		catch (IOException e) {}
		
	}
	public void renameRow(String newName,Parameters paramsp) {
		delete(paramsp);
		name = newName;
		saveRow(paramsp);
	}
	public void saveRow(Parameters paramsp) {
		String dir = paramsp.getDataDirectory();
		String fileName = dir+"/"+getName()+Constants.DATAEXTENSION;
		try {
			   FileWriter writer = new FileWriter(fileName);
			   String jsonString = new Gson().toJson(this);
			   writer.write(jsonString);
			   writer.close();	
			   Main.rwDebugInst.debug("DataDataRow", "saveRow", MRBDebug.DETAILED, "Row Saved "+name);
          }
			 catch (IOException i) {
				 Main.rwDebugInst.debug("DataDataRow", "saveRow", MRBDebug.DETAILED, "IO Exception "+i.getMessage());
					   i.printStackTrace();
          }
	}
	public void delete(Parameters paramsp) {
		String dir = paramsp.getDataDirectory();
		String fileName = dir+"/"+getName()+Constants.DATAEXTENSION;
		Main.rwDebugInst.debug("DataDataRow", "delete", MRBDebug.SUMMARY, "Delete "+fileName);
		File file = new File(fileName);
		if (file.delete())
			Main.rwDebugInst.debug("DataDataRow", "delete", MRBDebug.SUMMARY, "Deleted "+fileName);
		else
			Main.rwDebugInst.debug("DataDataRow", "delete", MRBDebug.SUMMARY, "Delete failed "+fileName);

	}

}
