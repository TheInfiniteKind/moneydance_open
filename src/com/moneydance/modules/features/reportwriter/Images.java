package com.moneydance.modules.features.reportwriter;

import java.io.IOException;
import java.io.InputStream;
import java.awt.Image;

public class Images {
	public Image editImg=null;
	public Image deleteImg = null;
//	public Image viewImg = null;
	public Image okImg = null;
	public Image cancelImg = null;
	public Image closeImg = null;
	public Image settingsImg = null;
	public Image helpImg = null;
	public Image addImg = null;
	public Image searchImg=null;
	public Image downloadImg = null;
	public Image csvImg = null;
	public Image spreadImg = null;
	public Image dbImg = null;
	public Image copyImg = null;
	public Image mainImg = null;
	private Main main;
	public Images(Main main) {
		this.main = main;
		editImg = main.getIcon("edit_node_32px.png");
		deleteImg = main.getIcon("delete_node_32px.png");
		okImg = main.getIcon("ok_32px.png");
		cancelImg = main.getIcon("cancel_32px.png");
		closeImg = main.getIcon("exit_32px.png");
		settingsImg = main.getIcon("settings_32px.png");
		addImg = main.getIcon("add_node_32px.png");
		helpImg = main.getIcon("help_32px.png");
		searchImg = main.getIcon("search_folder_32px.png");
		downloadImg = main.getIcon("download_from_cloud_32px.png");
		spreadImg = main.getIcon("icons8-spreadsheet-file-32.png");
		csvImg = main.getIcon("icons8-export-csv-32.png");
		dbImg = main.getIcon("icons8-add-database-32.png");
		copyImg = main.getIcon("icons8-replicate-rows-32.png");
		mainImg = main.getIcon("mrb icon2.png");
	}

}
