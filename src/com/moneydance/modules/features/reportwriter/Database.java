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
package com.moneydance.modules.features.reportwriter;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;


import org.h2.tools.Server;

import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.databeans.DataBean;

public class Database {
	private Connection conn;
	private Statement stmt;
	private Parameters params;
	private String outputDirectory;
	private Server server;
	private Boolean alreadyRunning = false;
	private int rs;

	public Database(Parameters paramsp,String filename, Boolean overwrite) throws RWException {
		params = paramsp;
		outputDirectory = params.getOutputDirectory();
		File db = new File(outputDirectory+"/"+filename+".mv.db");
		if (overwrite) {
			if (db.exists())
				db.delete();
		}
		else {
			if (db.exists())
				throw new RWException ("Database file already exists");
		}
	
		try {
			copyBlankDatabase(outputDirectory+"/"+filename+".mv.db");
			Class.forName("org.h2.Driver");
			server=Server.createTcpServer(new String[] {"-tcpAllowOthers"});
			if (!server.isRunning(false))
				server.start();
			else
				alreadyRunning = true;
			conn = DriverManager.getConnection("jdbc:h2:tcp://localhost/"+outputDirectory+"/"+filename+";AUTOCOMMIT=OFF", "sa","sa");
		}
		catch (ClassNotFoundException |SQLException e) {
			Main.rwDebugInst.debug("Database", "Init", MRBDebug.DETAILED, "SQL exception connecting to database");
			e.printStackTrace();
			throw new RWException ("Could not connect to database"+e.getLocalizedMessage());
		}
	}
	public void copyBlankDatabase(String database) throws RWException {
		try {
			java.io.InputStream in = 
					getClass().getResourceAsStream(Constants.RESOURCES+Constants.DEFAULTDATABASE);
			byte[] buffer= new byte[in.available()];
			in.read(buffer);
			File outputFile = new File(database);
			OutputStream outStream = new FileOutputStream(outputFile);
			outStream.write(buffer);
			outStream.close();
		} catch (Throwable e) { 
			e.printStackTrace();
			Main.rwDebugInst.debug("Database", "copyBlankDatabase", MRBDebug.DETAILED, "Error copying default database ");
			throw new RWException("Error copying blank database");
		}
	}
	public void createTable(DataBean bean) throws RWException{
		String sql;
		sql = "Drop Table "+bean.getTableName()+" if exists";
		try {
			stmt = conn.createStatement();
			rs = stmt.executeUpdate(sql);
			stmt.close();
		}
		catch (SQLException e) {
			OptionMessage.displayMessage("Could not drop "+bean.getTableName()+" Table");
			e.printStackTrace();
			Main.rwDebugInst.debug("Database", "createTable", MRBDebug.DETAILED, "SQL exception "+sql);
			throw new RWException("Could not create "+bean.getTableName()+" Table");
		}
		sql = bean.createTable();
		try {
			stmt = conn.createStatement();
			rs = stmt.executeUpdate(sql);
			stmt.close();
		}
		catch (SQLException e) {
			OptionMessage.displayMessage("Could not create "+bean.getTableName()+" Table");
			e.printStackTrace();
			Main.rwDebugInst.debug("Database", "createTable", MRBDebug.DETAILED, "SQL exception "+sql);
			throw new RWException("Could not create "+bean.getTableName()+" Table");
		}
	}
	public int executeUpdate(String sql) throws RWException {
		try {
			stmt = conn.createStatement();
			rs = stmt.executeUpdate(sql);
			stmt.close();
		}
		catch (SQLException e) {
			OptionMessage.displayMessage("SQL failed. See error log for more dewtails ");
			e.printStackTrace();
			rs = 0;
			Main.rwDebugInst.debug("Database", "executeUpdate", MRBDebug.DETAILED, "SQL exception "+sql);
			throw new RWException ("Database error on update "+e.getLocalizedMessage());
		}
		return rs;
	}
	public Connection getConnection() {
		return conn;
	}
	public void commit() throws RWException  {
		try {
				stmt = conn.createStatement();
				rs = stmt.executeUpdate("commit;");
				stmt.close();
		}
		catch (SQLException e) {
			e.printStackTrace();
			rs = 0;
			throw new RWException ("Database error on Commit "+e.getLocalizedMessage());
		}
	}
	public void close() throws RWException{
		try {
			conn.close();
			if (!alreadyRunning)
				server.stop();
		}
		catch (SQLException e) {
			e.printStackTrace();	
			throw new RWException ("Error closing database "+e.getLocalizedMessage());

		}
	}
}
