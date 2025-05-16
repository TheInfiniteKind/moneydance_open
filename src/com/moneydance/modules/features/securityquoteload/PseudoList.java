/*
 * Copyright (c) 2018, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.securityquoteload;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;
import java.util.SortedMap;
import java.util.TreeMap;

import com.google.gson.Gson;
import com.google.gson.JsonSyntaxException;
import com.google.gson.reflect.TypeToken;
import com.moneydance.modules.features.mrbutil.MRBDebug;

public class PseudoList {
	private SortedMap<String,PseudoCurrency> mapCurrencies;
	private List<PseudoCurrency> listCurrencies;
	public PseudoList () {
		
	}
	public PseudoList getData(){


		MRBDebug debugInst = Main.debugInst;
		mapCurrencies = new TreeMap<>();
		/*
		 * Determine if the new file exists
		 */
		boolean copyFile = false;
		String buildString ="{\"build\":\"";
		String endBuildString = "\"}";
		String fileName = DirectoryUtil.getMetaDirectory()+"/"+Constants.CURRENCYFILE;
		try {
				BufferedReader file = new BufferedReader(new FileReader(fileName));
				/*
				 * file found is the first line build number
				 */
				String line = file.readLine();
				int fileBuild=0;
				if (line.startsWith(buildString)) {
					if (line.endsWith(endBuildString))
						fileBuild = Integer.parseInt(line.substring(buildString.length(),line.length()-2));
					else
						fileBuild = Integer.parseInt(line.substring(buildString.length(),line.length()));
				}
				file.close();
				int resourceBuild = 0;
				InputStream input = this.getClass().getClassLoader().getResourceAsStream(Constants.RESOURCEPATH+"/"+Constants.CURRENCYFILE);
				if (input !=null) {
					debugInst.debug("PseudoList", "getData", MRBDebug.SUMMARY, "Input stream found");
					byte [] buffer = new byte[100];
					int bytesRead = input.read(buffer);
					String line2 = "";
					for (int i=0;i<bytesRead;i++)
						line2+=(char)buffer[i];
					if (line2.startsWith(buildString)) {
						String buildNumber = "";
						if (line2.contains(endBuildString)) 
							buildNumber = line2.substring(buildString.length(),line2.indexOf(endBuildString));
						else 
							buildNumber = line2.substring(buildString.length(),buildString.length()+4);
						try {
							resourceBuild = Integer.parseInt(buildNumber);
						}
						catch (NumberFormatException e){
							resourceBuild = 0;
						}
					}
					input.close();
				}
				if (resourceBuild > fileBuild)
					copyFile = true;
		}
		catch (IOException e){
			copyFile = true;
		}
		if (copyFile) {
			try {
				InputStream input = this.getClass().getClassLoader().getResourceAsStream(Constants.RESOURCEPATH+"/"+Constants.CURRENCYFILE);
				if (input == null) {
					debugInst.debug("PseudoList", "getData", MRBDebug.INFO, "Problem creating pseudocurrency.dict file");		
				}
				else {
					FileOutputStream output = new FileOutputStream(fileName);
					byte [] buffer = new byte[4096];
					int bytesRead = input.read(buffer);
					while (bytesRead != -1) {
					    output.write(buffer, 0, bytesRead);
					    bytesRead = input.read(buffer);
					}
					output.close();
					input.close();
				}
			}
			catch (IOException f) {
				debugInst.debug("PseudoList", "getData", MRBDebug.DETAILED, "Problem copying default file"+f.getMessage());		
				f.printStackTrace();
			}
			
		}
		try {
				BufferedReader file2 = new BufferedReader(new FileReader(fileName));
				String wholeFile;
				String fileLine = file2.readLine();
				if (fileLine.startsWith(buildString))
					wholeFile = "";
				else
					wholeFile = fileLine;
				while ((fileLine =file2.readLine())!= null){
					wholeFile += fileLine;
				}
				file2.close();
				Type listType = new TypeToken<ArrayList<PseudoCurrency>>(){}.getType();
				listCurrencies = new Gson().fromJson(wholeFile,listType);
				for (PseudoCurrency line : listCurrencies){
					mapCurrencies.put(line.getPseudo(), line);
				}
		}
		catch (JsonSyntaxException e){
			debugInst.debug("PseudoList", "getData", MRBDebug.INFO, "Syntax Error"+e.getMessage());		
		}
		catch (IOException e) {
			debugInst.debug("PseudoList", "getData", MRBDebug.INFO, "IO Exception "+e.getMessage());
			
		}
		return this;
	}
	public SortedMap<String,PseudoCurrency> getList()
	{
		return mapCurrencies;
	}
}
