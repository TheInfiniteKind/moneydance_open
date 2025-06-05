package com.moneydance.modules.features.reportwriter.view;


import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.loadsectrans.FieldLine;
import com.moneydance.modules.features.loadsectrans.Parameters2;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.OptionMessage;
import com.moneydance.util.Platform;
import org.apache.commons.io.FilenameUtils;

import java.io.IOException;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.reportwriter.samples.HttpDownloadUtility;
import com.moneydance.modules.features.reportwriter.samples.DownloadException;

import javax.swing.*;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.filechooser.FileNameExtensionFilter;


public class FirstRun {
    private Parameters params;
    private MyReport myReport;
    private JFileChooser fileChooser;
    private int ix=0;
    private int iy=0;
    private JDialog stage;
    private JPanel pane;
    private int maxWidth = 40;
    private JTextField dataDirName;
    private JTextField outputDirName;
	private ZipFile zipFile;
	private String samplesFile;
	private String tempDirName;
	private JLabel progressLbl;
	private JPanel samplesBox;
   public FirstRun( MyReport myReport, Parameters params)
    {
		this.params = params;
		stage = new JDialog();
		stage.setModalityType(Dialog.ModalityType.APPLICATION_MODAL);
		pane = new JPanel(new GridBagLayout());
		
		stage.add(pane);
		stage.setTitle("Parameter Settings");
		this.params = params;
		this.myReport = myReport;
    	Main.rwDebugInst.debug("FirstRun", "FirstRun", MRBDebug.SUMMARY, "started ");
		Label dataDirLbl = new Label("Parameters Folder : ");
		pane.add(dataDirLbl, GridC.getc(ix++,iy).insets(10, 10, 10, 10));
		dataDirName = new JTextField();
		dataDirName.setText(params.getDataDirectory());
		dataDirName.setToolTipText("Enter the folder name, or click on button to the right to find the folder");
		dataDirName.setMinimumSize(new Dimension(maxWidth*7,20));
		dataDirName.setPreferredSize(new Dimension(maxWidth*7,20));
		dataDirName.getDocument().addDocumentListener(new DocumentListener(){
			public void changedUpdate(DocumentEvent e){
				int width = dataDirName.getText()==null?0:dataDirName.getText().length();
				if (width > maxWidth) {
					maxWidth = width;
					dataDirName.setPreferredSize(new Dimension(maxWidth*7,20));
					outputDirName.setPreferredSize(new Dimension(maxWidth*7,20));
				}

			}
			public void insertUpdate(DocumentEvent e){}
			public void removeUpdate(DocumentEvent e){}
		});
		pane.add(dataDirName,GridC.getc(ix,iy).insets(10, 10, 10, 10));

		JButton dataChoose = new JButton();
		if (Main.loadedIcons.searchImg == null)
			dataChoose.setText("Search Folder");
		else
			dataChoose.setIcon(new ImageIcon(Main.loadedIcons.searchImg));
		ix+=3;
		pane.add(dataChoose,GridC.getc(ix, iy++).insets(10, 10, 10, 10));
		dataChoose.setToolTipText("Click to open file dialog to find required folder");
		dataChoose.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				String directory = chooseFile();
				dataDirName.setText(directory);
			}
        });  
		ix=0;
		JLabel outputDirLbl = new JLabel("Data Output Folder : ");
		pane.add(outputDirLbl,GridC.getc(ix++,iy).insets(10, 10, 10, 10));
		outputDirName = new JTextField();
		outputDirName.setText(params.getOutputDirectory());
		outputDirName.setToolTipText("Enter the folder name, or click on button to the right to find the folder");
		outputDirName.setMinimumSize(new Dimension(maxWidth*7,20));
		outputDirName.setPreferredSize(new Dimension(maxWidth*7,20));
		outputDirName.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				int width = outputDirName.getText() == null ? 0 : outputDirName.getText().length();
				if (width > maxWidth) {
					maxWidth = width;
					dataDirName.setPreferredSize(new Dimension(maxWidth * 7, 20));
					outputDirName.setPreferredSize(new Dimension(maxWidth * 7, 20));
				}
			}
        });
		pane.add(outputDirName,GridC.getc(ix,iy).insets(10, 10, 10, 10));

		JButton outputChoose = new JButton();
		if (Main.loadedIcons.searchImg == null)
			outputChoose.setText("Search Folder");
		else
			outputChoose.setIcon(new ImageIcon(Main.loadedIcons.searchImg));
		ix+=3;
		pane.add(outputChoose,GridC.getc(ix, iy++).insets(10, 10, 10, 10));
		outputChoose.setToolTipText("Click to open file dialog to find required folder");
		outputChoose.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				String directory = chooseFile();
				outputDirName.setText(directory);
			}
        });  
		ix=0;
		samplesBox = new JPanel();
		samplesBox.setLayout(new BoxLayout(samplesBox,BoxLayout.X_AXIS));
		JLabel sampleLbl = new JLabel("Download Samples");
		JButton sampleBtn = new JButton();
		if (Main.loadedIcons.downloadImg == null)
			sampleBtn.setText("Download Samples");
		else
			sampleBtn.setIcon(new ImageIcon(Main.loadedIcons.downloadImg));
		sampleBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				if (dataDirName.getText() == null ||
						dataDirName.getText().isEmpty()) {
					OptionMessage.displayErrorMessage("Please set the directories");
					return;
				}
				try {
					downloadSamples();
				} catch (DownloadException e2) {
					OptionMessage.displayErrorMessage("Error downloading samples");
				}
			}
        });	
		progressLbl = new JLabel();
		samplesBox.add(sampleBtn);
		samplesBox.add(Box.createRigidArea(new Dimension(10,0)));
		samplesBox.add(progressLbl);
		ix=0;
		pane.add(sampleLbl, GridC.getc(ix++, iy));
		pane.add(samplesBox, GridC.getc(ix, iy++));
        JButton okBtn = new JButton();
		if (Main.loadedIcons.okImg == null)
			okBtn.setText("Ok");
		else
			okBtn.setIcon(new ImageIcon(Main.loadedIcons.okImg));
		okBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				saveData();
			}
		});
        JButton cancelBtn = new JButton();
		if (Main.loadedIcons.cancelImg == null)
			cancelBtn.setText("Cancel");
		else
			cancelBtn.setIcon(new ImageIcon(Main.loadedIcons.cancelImg));
		cancelBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				stage.setVisible(false);
			}
		});		ix = 0;
        pane.add(okBtn,GridC.getc(ix++,iy).insets(10,10,10,10));
        pane.add(cancelBtn,GridC.getc(ix,iy).insets(10,10,10,10));
		stage.pack();
		stage.setLocationRelativeTo(null);
		stage.setVisible(true);
    }

   private void saveData() {
		if (dataDirName.getText() == null || 
				dataDirName.getText().isEmpty() ||
				outputDirName.getText() == null ||
				outputDirName.getText().isEmpty()) {
			OptionMessage.displayErrorMessage("Please set the directories");
			return;
		}
		params.setOutputDirectory(outputDirName.getText());
		params.setDataDirectory(dataDirName.getText());
		params.setDataTemplates();
		try {
			myReport.createAdapter(params.getOutputDirectory());
		}
		catch (DownloadException | RWException e2) {
			Main.rwDebugInst.debug("FirstRun", "FirstRun", MRBDebug.INFO, "IO Error downloading files");
			OptionMessage.displayErrorMessage("Error downloading files "+e2.getLocalizedMessage());
		}
;
		stage.setVisible(false);
   }
   private void downloadSamples() throws DownloadException{
	   String zipFileName;
  		tempDirName = System.getProperty("java.io.tmpdir");
  		samplesFile = Constants.REPOSITORY+"/"+Constants.SAMPLESFILE;
		if (MRBPlatform.isFreeBSD()|| MRBPlatform.isUnix())
			tempDirName +="/";
		Main.rwDebugInst.debug("FirstRun", "downloadSamples", MRBDebug.SUMMARY, "Downloading "+samplesFile);
	   try {
   			zipFileName = HttpDownloadUtility.downloadFile(samplesFile, tempDirName);
   			Main.rwDebugInst.debug("FirstRun", "downloadSamples", MRBDebug.SUMMARY, "File "+samplesFile+" downloaded");
   			progressLbl.setText("Samples file downloaded");
  			} 
	   catch (DownloadException e) {
			Main.rwDebugInst.debug("FirstRun", "downloadSamples", MRBDebug.INFO, "Error downloading "+samplesFile);
			throw e;
		} 
	    catch (IOException e) {
			Main.rwDebugInst.debug("FirstRun", "downloadSamples", MRBDebug.INFO, "IO Error downloading "+samplesFile);
			throw new DownloadException(e.getLocalizedMessage());
 		}
	   try {
		   loadZipFile(zipFileName);
 			progressLbl.setText("Sample files extracted");
	   }
	   catch (DownloadException e2) {
		   throw new DownloadException (e2.getLocalizedMessage());
	   }
   }	
	private void loadZipFile(String zipFileName) throws DownloadException {
		File foundFile = new File(zipFileName);
		if (!foundFile.exists()) {
			Main.rwDebugInst.debug("FirstRun", "loadZipFile", MRBDebug.INFO, "Zip file does not exist "+zipFileName);
			throw new DownloadException("Can not open zip file "+zipFileName);
		}
		try {
			Main.rwDebugInst.debug("FirstRun", "loadZipFile", MRBDebug.SUMMARY, "Opening zip file "+zipFileName);
			zipFile = new ZipFile(foundFile);
			Enumeration<? extends ZipEntry> entries = zipFile.entries();
			List<? extends ZipEntry> listIt = Collections.list(entries);
			boolean found=false; 
			for (ZipEntry entry :listIt) {
				String fileName = entry.getName();
				String extension = "."+FilenameUtils.getExtension(fileName);
				String directory="";
				if (extension.contentEquals(Constants.DATAEXTENSION))
					directory = dataDirName.getText();
				else if (extension.contentEquals(Constants.SELEXTENSION))
						directory = dataDirName.getText();
				else if (extension.contentEquals(Constants.REPORTEXTENSION))
						directory = dataDirName.getText();
				if (!directory.isEmpty()) {
					File testFile = new File(directory + "/"+fileName);
					if (testFile.exists())
						found=true;
				}
			}
			if (found) {
				boolean askOverwrite = OptionMessage.yesnoMessage("Sample files already exist.  Do you wish to Overwrite?");
				if (askOverwrite)
					return;

			}
			for (ZipEntry entry :listIt) {
				copyZipFileEntry(entry);
			}
		}
		catch (IOException e) {
			Main.rwDebugInst.debug("FirstRun", "loadZipFile", MRBDebug.INFO, "Error opening "+zipFileName+" "+e.getMessage());
			throw new DownloadException(e.getMessage());
		}
		try {
			zipFile.close();
		}
		catch (IOException e) {
			Main.rwDebugInst.debug("FirstRun", "loadZipFile", MRBDebug.INFO, "Error closing "+zipFileName+" "+e.getMessage());
		}

	}


	private void copyZipFileEntry(ZipEntry zipEntry) throws DownloadException{
		Main.rwDebugInst.debug("FirstRun", "copyZipFileEntry", MRBDebug.DETAILED, "Copying file "+zipEntry.getName());
		String extName = new File(zipEntry.getName()).getName();
		String extension = "."+FilenameUtils.getExtension(extName);
		String directory="";
		if (extension.contentEquals(Constants.DATAEXTENSION))
			directory = dataDirName.getText();
		else if (extension.contentEquals(Constants.SELEXTENSION))
				directory = dataDirName.getText();
		else if (extension.contentEquals(Constants.REPORTEXTENSION))
			directory = dataDirName.getText();
		if (directory.isEmpty())
			return;
		String outFile = directory+"/"+extName;
		FileOutputStream outStream;
		InputStream inStream;
		byte[] buffer = new byte[1024];
		int noOfBytes;
		try {
			outStream = new FileOutputStream(outFile);
			try {
				inStream = zipFile.getInputStream(zipEntry);
				while ((noOfBytes = inStream.read(buffer)) !=-1) {
					outStream.write(buffer, 0, noOfBytes);
				}
				outStream.close();
				inStream.close();
				Main.rwDebugInst.debug("CopyFile", "copyZipFileEntry", MRBDebug.SUMMARY, "File "+extName+" extracted");
				progressLbl.setText("File "+extName+" extracted");
			}
			catch (IOException e) {
				Main.rwDebugInst.debug("CopyFile", "copyZipFileEntry", MRBDebug.INFO, "Error extracting "+extName+" "+e.getMessage());
				progressLbl.setText("Error extracting "+extName);
				throw new DownloadException(e.getMessage());
			}
		}
		catch (FileNotFoundException e) {
			Main.rwDebugInst.debug("CopyFile", "copyZipFileEntry", MRBDebug.INFO, "Zip entry not found "+extName+" "+e.getMessage());
			progressLbl.setText("Zip entry not found "+extName);
			throw new DownloadException(e.getMessage());
		}

	}


	/*
	 * Select a file
	 */
	private String chooseFile() {
		FileDialog dialog;
		String strDirectory = Main.preferences.getString(Constants.PROGRAMNAME+"."+Constants.FIRSTRUNDIR,System.getProperty("user.home"));
		if (Platform.isMac()) {
			JFrame parent = null;
			String oldValue = System.getProperty("apple.awt.fileDialogForDirectories");
			System.setProperty("apple.awt.fileDialogForDirectories","true");
			dialog = new FileDialog(parent, "Choose a Directory", FileDialog.LOAD);
			if (!(strDirectory == null || strDirectory.isEmpty()))
				dialog.setDirectory(strDirectory);
			dialog.setVisible(true);
			strDirectory = dialog.getDirectory()+dialog.getFile();
			System.setProperty("apple.awt.fileDialogForDirectories",oldValue);
		}
		else {
			fileChooser = new JFileChooser();
			fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
			if (!(strDirectory == null || strDirectory.isEmpty())) {
				try {
					fileChooser.setCurrentDirectory(new File(strDirectory));
				} catch (Exception e) {
					Main.rwDebugInst.debug("FirstRun", "chooseFile", MRBDebug.DETAILED, "Error browsing " + strDirectory);
					e.printStackTrace();
				}
			}
			int result = fileChooser.showDialog(null, "Select Directory");
			if (result == JFileChooser.APPROVE_OPTION)
				strDirectory = fileChooser.getSelectedFile().getAbsolutePath();
			else
				strDirectory = null;
		}

		Main.preferences.put(Constants.PROGRAMNAME+"."+Constants.FIRSTRUNDIR, strDirectory);
		Main.preferences.isDirty();
		return strDirectory;
	}

}
