# extract_reminders_to_csv.py (version 3)
# Thanks to allangdavies adgetreminderstocsv.py
# Stuart Beesley 2020-06-18 tested on MacOS - MD2019.4 - StuWareSoftSystems....
# v3 upgraded script to ask for extract filename and extract date formats in pop up windows; also fix amounts less than 1

# Extracts all Moneydance reminders to a csv file compatible with Excel

# Use in Moneydance Menu Window->Show Moneybot Console >> Open Script >> RUN
# This script will pop up windows and ask for file extract name/location and date formats

# I haven't tested on Windows, may or may not need tweaking if you set the file/pathnames

# This script accesses Moneydance reminders and write the details to a csv file

from com.infinitekind.moneydance.model import *

import sys
reload(sys)                         # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')      # Dirty hack to eliminate UTF-8 coding errors

import os
import os.path
import datetime
import java.io.File
import javax.swing.filechooser.FileNameExtensionFilter
from javax.swing import JButton, JFrame, JScrollPane, JTextArea, BoxLayout, BorderFactory, JOptionPane, JPanel, JRadioButton, ButtonGroup, JButton, JLabel, JFileChooser

# function to output the amount (held as integer in cents) to 2 dec place amount field
def formatasnumberforExcel(amountInt):

    amount = amountInt                      # Temporarily convert to a positive and then ensure always three digits
    if amountInt < 0:   amount *= -1
    str_amount = str(amount)
    if len(str_amount)<3: str_amount = ("0"+str_amount) # PAD with zeros to ensure whole number exists
    if len(str_amount)<3: str_amount = ("0"+str_amount)
        
    wholeportion    = str_amount[0:-2]
    placesportion   = str_amount[-2:]
    
    if amountInt < 0: wholeportion = '-'+wholeportion       # Put the negative back
    
    outputfield=wholeportion+'.'+placesportion
    return outputfield

# Moneydance dates  are int yyyymmddd - convert to locale date string for CSV format
def dateoutput(dateinput,theformat):
	if 		dateinput == "EXPIRED": dateoutput=dateinput
	elif 		dateinput == "": dateoutput="" 	
	elif		dateinput == 0: dateoutput=""
	elif		dateinput == "0": dateoutput=""
	else:
			dateasdate=datetime.datetime.strptime(str(dateinput),"%Y%m%d") # Convert to Date field
			dateoutput=dateasdate.strftime(theformat)
	
	#print "Input: ",dateinput,"  Format: ",theformat,' Output: ',dateoutput
	return dateoutput

# ========= MAIN PROGRAM =============

def Main():

    print "StuWareSoftSystems..."
    print "Export reminders to csv file"

    scriptpath = moneydance_data.getRootFolder().getParent()        # Path to Folder holding MD Datafile
    
    filename = JFileChooser(scriptpath)
    
    filename.setSelectedFile(java.io.File(scriptpath+os.path.sep+'extract_reminders.csv'))

    extfilter = javax.swing.filechooser.FileNameExtensionFilter("CSV file (CSV,TXT)", ["csv","TXT"])

    filename.setMultiSelectionEnabled(False)
    filename.setFileFilter(extfilter)
    filename.setDialogTitle("Select/Choose/Create CSV file for Reminders extract")

    returnvalue = filename.showDialog(None,"Extract")
 
    if returnvalue==JFileChooser.CANCEL_OPTION:
        print "User chose to cancel Extract... Exiting...."
        print "Goodbye..."
        return(1)
            
    if filename.selectedFile==None:
        print "User chose no filename... Exiting...."
        print "Goodbye..."
        return(1)
    
    csvfilename = str(filename.selectedFile)
    print 'Reading Reminders and extracting to file: ', csvfilename
    print 'NOTE: Should drop non utf8 characters...'

    if os.path.exists(csvfilename) and os.path.isfile(csvfilename):
        # Uh-oh file exists - overwrite?
        print "File already exists... Confirm..."
        if (JOptionPane.showConfirmDialog(None, "File '"+os.path.basename(csvfilename)+"' exists... Press YES to overwrite and proceed, NO to Abort?","WARNING",JOptionPane.YES_NO_OPTION,JOptionPane.WARNING_MESSAGE)==JOptionPane.YES_OPTION):
            print "User agreed to overwrite file..."
        else:
            print "User does not want to overwrite file... Aborting..."
            return(1)
    
    userdateformat = (JOptionPane.showInputDialog(None,
                                             "Type 1 or 2 or 3\n1=dd/mm/yyyy\n2=mm/dd/yyyy\n3=yyyy/mm/dd (default)\n4=yyyymmdd",
                                             "CHOOSE OUTPUT DATEFORMAT?",JOptionPane.OK_CANCEL_OPTION,None,None,'3'))
    
    if not userdateformat in ["1","2","3","4"]:
        print "User did not choose dateformat... Exiting...."
        print "Goodbye..."
        return(1)
    else: userdateformat = int(userdateformat)
    
    print "User's Date Choice: ", ["","dd/mm/yy","mm/dd/yy","yy/mm/dd","yyyymmdd"][userdateformat]

    if	    userdateformat==1:	userdateformat="%d/%m/%Y"
    elif	userdateformat==2: 	userdateformat="%m/%d/%Y"
    elif	userdateformat==3: 	userdateformat="%Y/%m/%d"
    elif	userdateformat==4: 	userdateformat="%Y%m%d"
    else:
		#PROBLEM /  default
		userdateformat="%Y%m%d"

    root=moneydance.getCurrentAccountBook()

    rems = root.getReminders().getAllReminders()
    print 'Success: read ',rems.size(),'reminders'
    print
    csvheaderline="NextDue,Number#,ReminderType,Frequency,AutoCommitDays,LastAcknowledged,FirstDate,EndDate,ReminderDecription,NetAmount,TxfrType,Account,MainDescription,Split#,SplitAmount,Category,Description,Memo\n"

	# Read each reminder and create a csv line for each in the csvlines array
    csvlines=[]		# Set up an ampty array
    csvlines.append(csvheaderline)
	
    for index in range(0,int(rems.size())):

	    rem=rems[index]									# Get the reminder

	    remtype=rem.getReminderType()                     #NOTE or TRANSACTION
	    desc=rem.getDescription().replace(","," ")        	#remove commas to keep csv format happy
	    memo=str(rem.getMemo()).replace(","," ").strip() #remove commas to keep csv format happy
	    memo=str(memo).replace("\n","*").strip()  		#remove newlines to keep csv format happy

	    print index+1,rem.getDescription() 			# Name of Reminder

	    #determine the frequency of the transaction
	    daily=rem.getRepeatDaily()
	    weekly=rem.getRepeatWeeklyModifier()
	    monthly=rem.getRepeatMonthlyModifier()
	    yearly=rem.getRepeatYearly()
	    numperiods=0
	    countfreqs=0

	    remfreq=''

	    if daily>0:
        		remfreq+='DAILY'
        		remfreq+='(every '+str(daily)+' days)'
        		countfreqs+=1

	    if len( rem.getRepeatWeeklyDays())>0 and rem.getRepeatWeeklyDays()[0] > 0:
        		for freq in range(0,len(rem.getRepeatWeeklyDays())):
					if len(remfreq)>0: remfreq += " & "
					if weekly  == Reminder.WEEKLY_EVERY:			    remfreq += 'WEEKLY_EVERY'
					if weekly  == Reminder.WEEKLY_EVERY_FIFTH:			remfreq += 'WEEKLY_EVERY_FIFTH'
					if weekly  == Reminder.WEEKLY_EVERY_FIRST:			remfreq += 'WEEKLY_EVERY_FIRST'
					if weekly  == Reminder.WEEKLY_EVERY_FOURTH:		    remfreq += 'WEEKLY_EVERY_FOURTH'
					if weekly  == Reminder.WEEKLY_EVERY_LAST:			remfreq += 'WEEKLY_EVERY_LAST'
					if weekly  == Reminder.WEEKLY_EVERY_SECOND:		    remfreq += 'WEEKLY_EVERY_SECOND'
					if weekly  == Reminder.WEEKLY_EVERY_THIRD:			remfreq += 'WEEKLY_EVERY_THIRD'

					if rem.getRepeatWeeklyDays()[freq] == 1: remfreq+='(on Sunday)'
					if rem.getRepeatWeeklyDays()[freq] == 2: remfreq+='(on Monday)'
					if rem.getRepeatWeeklyDays()[freq] == 3: remfreq+='(on Tuesday)'
					if rem.getRepeatWeeklyDays()[freq] == 4: remfreq+='(on Wednesday)'
					if rem.getRepeatWeeklyDays()[freq] == 5: remfreq+='(on Thursday)'
					if rem.getRepeatWeeklyDays()[freq] == 6: remfreq+='(on Friday)'
					if rem.getRepeatWeeklyDays()[freq] == 7: remfreq+='(on Saturday)'
					if rem.getRepeatWeeklyDays()[freq] <1 or rem.getRepeatWeeklyDays()[freq] > 7: remfreq+='(*ERROR*)'
					countfreqs+=1

	    if len(rem.getRepeatMonthly())>0 and rem.getRepeatMonthly()[0] > 0 :
        		for freq in range(0,len(rem.getRepeatMonthly())):
					if len(remfreq)>0: remfreq += " & "
					if monthly  == Reminder.MONTHLY_EVERY: 				 remfreq += 'MONTHLY_EVERY' 
					if monthly  == Reminder.MONTHLY_EVERY_FOURTH:	     remfreq += 'MONTHLY_EVERY_FOURTH'
					if monthly  == Reminder.MONTHLY_EVERY_OTHER: 	     remfreq += 'MONTHLY_EVERY_OTHER'
					if monthly  == Reminder.MONTHLY_EVERY_SIXTH: 		 remfreq += 'MONTHLY_EVERY_SIXTH' 
					if monthly  == Reminder.MONTHLY_EVERY_THIRD: 		 remfreq += 'MONTHLY_EVERY_THIRD' 

					theday = rem.getRepeatMonthly()[freq]
					if theday == Reminder.LAST_DAY_OF_MONTH:
						remfreq+='(on LAST_DAY_OF_MONTH)'
					else:

						if 4 <= theday <= 20 or 24 <= theday <= 30: 		suffix = "th"
						else:    													suffix = ["st", "nd", "rd"][theday % 10 - 1]

						remfreq+='(on '+str(theday)+suffix+')'

					countfreqs+=1

	    if yearly:
			   if len(remfreq)>0: remfreq += " & "
 	  		   remfreq+='YEARLY'
 	  		   countfreqs+=1

	    if len(remfreq) < 1 or countfreqs==0:         remfreq='!ERROR! NO ACTUAL FREQUENCY OPTIONS SET PROPERLY '+remfreq
	    if countfreqs>1: remfreq = "**MULTI** "+remfreq

	    lastdate=rem.getLastDateInt()		
	    if lastdate < 1:   															# Detect if an enddate is set
				remdate=str(rem.getNextOccurance( 20991231 ))				# Use cutoff  far into the future
	    else:		remdate=str(rem.getNextOccurance( rem.getLastDateInt() ))	# Stop at enddate

	    if lastdate <1: lastdate=''

	    if remdate =='0': remdate="EXPIRED"

	    lastack = rem.getDateAcknowledgedInt()
	    if lastack == 0 or lastack == 19700101: lastack=''
				
	    auto = rem.getAutoCommitDays()
	    if auto>= 0: 	auto='YES: ('+str(auto)+' days before scheduled)'
	    else:				auto='NO'

	    if str(remtype)=='NOTE':
			csvline='%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %(
					dateoutput(remdate,userdateformat),
					index+1,
					rem.getReminderType(),
					remfreq,
					auto,
					dateoutput(lastack,userdateformat),
					dateoutput(rem.getInitialDateInt(),userdateformat),
					dateoutput(lastdate,userdateformat),
					desc,
					'',					# NetAmount
					'',					# TxfrType
					'',					# Account
					'',					# MainDescription
					str(index+1)+'.0',	# Split#
					'',					# SplitAmount
					'',					# Category
					'',					# Description
					'"'+memo+'"'		# Memo
			)
			csvlines.append(csvline)



	    elif str(remtype)=='TRANSACTION':
      
    			txnparent=rem.getTransaction()
    			amount=formatasnumberforExcel(int(txnparent.getValue()))
        
 			for index2 in range(0,int(txnparent.getOtherTxnCount())): 
				splitdesc=txnparent.getOtherTxn(index2).getDescription().replace(","," ")        		#remove commas to keep csv format happy
				splitmemo=txnparent.getMemo().replace(","," ")        									#remove commas to keep csv format happy
 				maindesc=txnparent.getDescription().replace(","," ").strip()

				if index2>0: amount='' 																	# Don't repeat the new amount on subsequent split lines (so you can total column). The split amount will be correct

				stripacct = str(txnparent.getAccount()).replace(","," ").strip() 							#remove commas to keep csv format happy
				stripcat = str(txnparent.getOtherTxn(index2).getAccount()).replace(","," ").strip() 	#remove commas to keep csv format happy

		
				csvline='%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %(
					dateoutput(remdate,userdateformat),
					index+1,
					rem.getReminderType(),
					remfreq,
					auto,
					dateoutput(lastack,userdateformat),
					dateoutput(rem.getInitialDateInt(),userdateformat),
					dateoutput(lastdate,userdateformat),
					desc,
					amount,
					txnparent.getTransferType(),
					stripacct,
					maindesc,
					str(index+1)+'.'+str(index2+1),
					formatasnumberforExcel(int(txnparent.getOtherTxn(index2).getValue())*-1),
					stripcat,
					splitdesc,
					splitmemo 
				)
				csvlines.append(csvline)

    index+=1

    # Write the csvlines to a file
    f=open(csvfilename,"w")
    for csvline in csvlines: f.write(csvline)
    print 'CSV file '+csvfilename+' created'
    print 'Done'
    f.close()


    return( 0 )
# END OF FUNCTION

Main()

