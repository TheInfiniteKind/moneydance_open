#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# net_account_balances_extra_code.py build: 1001 - February 2026 - Stuart Beesley StuWareSoftSystems

# To avoid the dreaded issue below, moving some code here....:
# java.lang.RuntimeException: java.lang.RuntimeException: For unknown reason, too large method code couldn't be resolved

# build: 1000 - NEW SCRIPT
# build: 1001 - Updated MyCostCalculation(v10) - in line with MD2026(5500)
###############################################################################
# MIT License
#
# Copyright (c) 2020-2026 Stuart Beesley - StuWareSoftSystems & Infinite Kind (Moneydance)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

# Just copy these as needed from main script - do not redefine....

# Common definitions

# My definitions
global net_account_balances_frame_
global MD_REF, GlobalVars, debug, myPrint, QuickAbortThisScriptException
global myPopupInformationBox, getFileFromFileChooser, get_home_dir, myPopupAskQuestion
global invokeMethodByReflection, getFieldByReflection, setFieldByReflection
global MyPopUpDialogBox, dump_sys_error_to_md_console_and_errorlog
global pad, rpad, cpad, setDisplayStatus, doesUserAcceptDisclaimer, get_time_stamp_as_nice_text
global getMDIcon, QuickJFrame
global genericSwingEDTRunner, genericThreadRunner
global getColorBlue, getColorRed, getColorDarkGreen, MoneybotURLDebug
global confirm_backup_confirm_disclaimer, play_the_money_sound
global safeStr, convertStrippedIntDateFormattedText

# MyDateRangeChooser & AsOfDateChooser definitions
from javax.swing.event import SwingPropertyChangeSupport
from java.awt.event import ItemListener, MouseAdapter, ItemEvent

global copy                                                                                                             # python definitions
global DateUtil, DateRange, DateRangeChooser, DateRangeOption, JDateField, MDURLUtil, Util, MoneydanceGUI, SyncRecord   # Moneydance definitions
global PropertyChangeListener, DefaultComboBoxModel, GridBagLayout, GridC, Integer, SwingUtilities, JComboBox           # Java
global isDateRangeChooserUpgradedBuild, MyJComboBox, MyJLabel, MyJTextFieldAsInt, MyJPanel                              # mine

# MyCostCalculation globals / definitions
from java.util import HashMap, HashSet, Hashtable, LinkedHashSet
from com.infinitekind.moneydance.model import CapitalGainResult, InvestFields, InvestTxnType
global Account, AbstractTxn, SplitTxn, InvestUtil, TxnSet
global CurrencyUtil, CurrencyType, TxnUtil
global ArrayList, Math, StringBuilder, Long, String

try:
    if GlobalVars.EXTRA_CODE_INITIALISED: raise QuickAbortThisScriptException

    myPrint("DB", "Extra Code Initialiser loading....")

    def _extra_code_initialiser():
        GlobalVars.EXTRA_CODE_INITIALISED = True
        myPrint("B", ">> extra_code script initialised <<")

    #### EXTRA CODE HERE ####


    class MyBasePropertyChangeReporter:     # Copies: com.moneydance.util.BasePropertyChangeReporter
        ALL_PROPERTIES = "UpdateAll"
        def __init__(self): self.eventNotify = SwingPropertyChangeSupport(self)
        def addPropertyChangeListener(self, listener): self.eventNotify.addPropertyChangeListener(listener)
        def removePropertyChangeListener(self, listener): self.eventNotify.removePropertyChangeListener(listener)
        def notifyPropertyChanged(self, propertyName, oldValue, newValue): self.eventNotify.firePropertyChange(propertyName, oldValue, newValue)
        def notifyAllListeners(self): self.eventNotify.firePropertyChange(self.ALL_PROPERTIES, None, None)

    class MyDateRangeChooser(MyBasePropertyChangeReporter, ItemListener, PropertyChangeListener):    # Based on: com.moneydance.apps.md.view.gui.DateRangeChooser
        """Class that allows selection of a Date Range. Listen to changes using java.beans.PropertyChangeListener() on "dateRangeChanged"""

        DATE_RANGE_VALID = 19000101

        DRC_DR_ENABLED_IDX = 0
        DRC_DR_KEY_IDX = 1
        DRC_DR_START_KEY_IDX = 2
        DRC_DR_END_KEY_IDX = 3
        DRC_DR_OFFSETPERIODS_IDX = 4
        DRC_DR_PERIODMULTIPLIER_IDX = 5     # for compatibility with MD2024(5119) - enhanced DRC
        DRC_DR_SYNCRECORD_IDX = 6           # for compatibility with MD2024(5119) - enhanced DRC

        PROP_DATE_RANGE_CHANGED = "dateRangeChanged"
        DR_TODAY = "last_1_day"
        KEY_CUSTOM_DATE_RANGE = "custom_date"
        KEY_DR_ALL_DATES = "all_dates"
        KEY_DR_YEAR_TO_DATE = "year_to_date"

        # NOTE: These need to exactly match the resource keys in DateRangeOption Enum.. Especially the resource key strings!
        # ... column[3] = legacy key of there is one....
        DR_DATE_OPTIONS = [
                            ["year_to_date",                 "Year to date",                  41,   None],
                            ["fiscal_year_to_date",          "Fiscal Year to date",           61,   None],
                            ["quarter_to_date",              "Quarter to date",               31,   None],
                            ["month_to_date",                "Month to date",                 22,   None],
                            ["this_year",                    "This year",                     40,   None],
                            ["this_fiscal_year",             "This Fiscal Year",              60,   None],
                            ["this_quarter",                 "This quarter",                  30,   None],
                            ["this_month",                   "This month",                    21,   None],
                            ["last_year",                    "Last year",                     42,   None],
                            ["dr_last_two_years",            "Last 2 years",                  43,   None],
                            ["dr_last_three_years",          "Last 3 years",                  44,   None],
                            ["dr_last_five_years",           "Last 5 years",                  45,   None],
                            ["last_fiscal_year",             "Last Fiscal Year",              63,   None],
                            ["dr_last_two_fiscal_years",     "Last 2 Fiscal Years",           64,   None],
                            ["dr_last_three_fiscal_years",   "Last 3 Fiscal Years",           65,   None],
                            ["dr_last_five_fiscal_years",    "Last 5 Fiscal Years",           66,   None],
                            ["last_fiscal_quarter",          "Last Fiscal Quarter",           62,   None],
                            ["last_quarter",                 "Last quarter",                  32,   None],
                            ["last_month",                   "Last month",                    23,   None],
                            ["last_12_months",               "Last 12 months",                24,   None],
                            ["dr_last_18_months",            "Last 18 months",                25,   None],
                            ["dr_last_24_months",            "Last 24 months",                26,   None],
                            ["all_dates",                    "All dates",                      0,   None],
                            ["custom_date",                  "Custom dates",                  99,   None],
                            ["this_week",                    "This week",                     10,   None],
                            ["last_30_days",                 "Last 30 days",                  51,   None],
                            ["dr_last_60_days",              "Last 60 days",                  52,   "last_60_days"],
                            ["dr_last_90_days",              "Last 90 days",                  53,   "last_90_days"],
                            ["dr_last_120_days",             "Last 120 days",                 54,   "last_120_days"],
                            ["dr_last_180_days",             "Last 180 days",                 55,   "last_180_days"],
                            ["last_365_days",                "Last 365 days",                 56,   None],
                            ["last_week",                    "Last week",                     11,   None],
                            ["last_1_day",                   "Last 1 day (yesterday & today)",50,   None],
                            ["dr_yesterday",                 "Yesterday",                      3,   "yesterday"],
                            ["dr_today",                     "Today",                          2,   "today"],
                            ["dr_next_month",                "Next month",                    20,   "next_month"]
                        ]
        LEGACY_DRO_KEYS = dict((droLegacyKey, droKey) for droKey, droName, droSort, droLegacyKey in DR_DATE_OPTIONS if droLegacyKey is not None)

        @staticmethod
        def upgradeLegacyResourceKey(resourceKey):
            """Takes a resource key for DR_DATE_OPTIONS and switches it to the proper / latest resource key
            ... MD2024(5100) included the upgraded DateRangeChooser/DateRangeOption and some of the resource keys changed..."""
            if (resourceKey not in MyDateRangeChooser.LEGACY_DRO_KEYS): return resourceKey
            upgradedKey = MyDateRangeChooser.LEGACY_DRO_KEYS[resourceKey]
            myPrint("B", "** Legacy DateRangeOption resource key '%s' upgraded in memory to '%s' **" %(resourceKey, upgradedKey))
            return upgradedKey

        class DateRangeChoice:
            def __init__(self, key, displayName, sortIdx):
                self.key = key
                self.displayName = displayName
                self.sortIdx = sortIdx
            def getKey(self):           return self.key
            def getDisplayName(self):   return self.displayName
            def getSortIdx(self):       return self.sortIdx
            def __str__(self):          return self.getDisplayName()
            def __repr__(self):         return self.__str__()
            def toString(self):         return self.__str__()

            @staticmethod
            def fixLegacyKeyValues(keyToCheck):
                return keyToCheck

            @staticmethod
            def internalCalculateDateRangeFromKey(forOptionKey, realTodayInt, calculatedTodayInt, offsetPeriods):
                # type: (str, int, int, int) -> DateRange

                if forOptionKey ==  "custom_date":                  rtnVal = (realTodayInt, realTodayInt)
                elif forOptionKey == "all_dates":                   rtnVal = (19600101, DateRange().getEndDateInt())
                elif forOptionKey == "year_to_date":                rtnVal = (DateUtil.firstDayInYear(calculatedTodayInt), calculatedTodayInt)
                elif forOptionKey == "quarter_to_date":             rtnVal = (DateUtil.firstDayInQuarter(calculatedTodayInt), calculatedTodayInt)
                elif forOptionKey == "month_to_date":               rtnVal = (DateUtil.firstDayInMonth(calculatedTodayInt), calculatedTodayInt)
                elif forOptionKey == "this_year":                   rtnVal = (DateUtil.firstDayInYear(calculatedTodayInt), DateUtil.lastDayInYear(calculatedTodayInt))
                elif forOptionKey == "this_fiscal_year":            rtnVal = (DateUtil.firstDayInFiscalYear(calculatedTodayInt), DateUtil.lastDayInFiscalYear(calculatedTodayInt))
                elif forOptionKey == "fiscal_year_to_date":         rtnVal = (DateUtil.firstDayInFiscalYear(calculatedTodayInt), calculatedTodayInt)
                elif forOptionKey == "last_fiscal_year":            rtnVal = (DateUtil.firstDayInFiscalYear(DateUtil.decrementYear(calculatedTodayInt)), DateUtil.lastDayInFiscalYear(DateUtil.decrementYear(calculatedTodayInt)))
                elif forOptionKey == "dr_last_two_fiscal_years":    rtnVal = (DateUtil.firstDayInFiscalYear(DateUtil.incrementDate(calculatedTodayInt, -2, 0, 0)), DateUtil.lastDayInFiscalYear(DateUtil.decrementYear(calculatedTodayInt)))
                elif forOptionKey == "dr_last_three_fiscal_years":  rtnVal = (DateUtil.firstDayInFiscalYear(DateUtil.incrementDate(calculatedTodayInt, -3, 0, 0)), DateUtil.lastDayInFiscalYear(DateUtil.decrementYear(calculatedTodayInt)))
                elif forOptionKey == "dr_last_five_fiscal_years":   rtnVal = (DateUtil.firstDayInFiscalYear(DateUtil.incrementDate(calculatedTodayInt, -5, 0, 0)), DateUtil.lastDayInFiscalYear(DateUtil.decrementYear(calculatedTodayInt)))
                elif forOptionKey == "last_fiscal_quarter":         rtnVal = (DateUtil.firstDayInFiscalQuarter(DateUtil.incrementDate(calculatedTodayInt, 0, -3, 0)), DateUtil.lastDayInFiscalQuarter(DateUtil.incrementDate(calculatedTodayInt, 0, -3, 0)))
                elif forOptionKey == "this_quarter":                rtnVal = (DateUtil.firstDayInQuarter(calculatedTodayInt), DateUtil.lastDayInQuarter(calculatedTodayInt))
                elif forOptionKey == "this_month":                  rtnVal = (DateUtil.firstDayInMonth(calculatedTodayInt), DateUtil.lastDayInMonth(calculatedTodayInt))
                elif forOptionKey == "this_week":                   rtnVal = (DateUtil.firstDayInWeek(calculatedTodayInt), DateUtil.lastDayInWeek(calculatedTodayInt))
                elif forOptionKey == "last_year":                   rtnVal = (DateUtil.firstDayInYear(DateUtil.incrementDate(calculatedTodayInt, -1, 0, 0)), DateUtil.lastDayInYear(DateUtil.decrementYear(calculatedTodayInt)))
                elif forOptionKey == "dr_last_two_years":           rtnVal = (DateUtil.firstDayInYear(DateUtil.incrementDate(calculatedTodayInt, -2, 0, 0)), DateUtil.lastDayInYear(DateUtil.decrementYear(calculatedTodayInt)))
                elif forOptionKey == "dr_last_three_years":         rtnVal = (DateUtil.firstDayInYear(DateUtil.incrementDate(calculatedTodayInt, -3, 0, 0)), DateUtil.lastDayInYear(DateUtil.decrementYear(calculatedTodayInt)))
                elif forOptionKey == "dr_last_five_years":          rtnVal = (DateUtil.firstDayInYear(DateUtil.incrementDate(calculatedTodayInt, -5, 0, 0)), DateUtil.lastDayInYear(DateUtil.decrementYear(calculatedTodayInt)))
                elif forOptionKey == "last_quarter":                rtnVal = (DateUtil.firstDayInQuarter(DateUtil.incrementDate(calculatedTodayInt, 0, -3, 0)), DateUtil.lastDayInQuarter(DateUtil.incrementDate(calculatedTodayInt, 0, -3, 0)))
                elif forOptionKey == "last_month":                  rtnVal = (DateUtil.incrementDate(DateUtil.firstDayInMonth(calculatedTodayInt), 0, -1, 0), DateUtil.incrementDate(DateUtil.firstDayInMonth(calculatedTodayInt), 0, 0, -1))
                elif forOptionKey == "last_week":                   rtnVal = (DateUtil.incrementDate(DateUtil.firstDayInWeek(calculatedTodayInt), 0, 0, -7), DateUtil.incrementDate(DateUtil.firstDayInWeek(calculatedTodayInt), 0, 0, -1))
                elif forOptionKey == "last_12_months":              rtnVal = (DateUtil.incrementDate(DateUtil.firstDayInMonth(realTodayInt), 0, -12 * (offsetPeriods + 1), 0), DateUtil.incrementDate(DateUtil.firstDayInMonth(realTodayInt), 0, -12 * (offsetPeriods), -1))
                elif forOptionKey == "dr_last_18_months":           rtnVal = (DateUtil.incrementDate(DateUtil.firstDayInMonth(realTodayInt), 0, -18 * (offsetPeriods + 1), 0), DateUtil.incrementDate(DateUtil.firstDayInMonth(realTodayInt), 0, -18 * (offsetPeriods), -1))
                elif forOptionKey == "dr_last_24_months":           rtnVal = (DateUtil.incrementDate(DateUtil.firstDayInMonth(realTodayInt), 0, -24 * (offsetPeriods + 1), 0), DateUtil.incrementDate(DateUtil.firstDayInMonth(realTodayInt), 0, -24 * (offsetPeriods), -1))
                elif forOptionKey == "last_1_day":                  rtnVal = (DateUtil.incrementDate(realTodayInt, 0, 0, -1), realTodayInt)
                elif forOptionKey == "last_30_days":                rtnVal = (DateUtil.incrementDate(realTodayInt, 0, 0, (-29  * (offsetPeriods + 1)) -offsetPeriods), DateUtil.incrementDate(realTodayInt, 0, 0, (-29  * (offsetPeriods)) -offsetPeriods))
                elif forOptionKey == "dr_last_60_days":             rtnVal = (DateUtil.incrementDate(realTodayInt, 0, 0, (-59  * (offsetPeriods + 1)) -offsetPeriods), DateUtil.incrementDate(realTodayInt, 0, 0, (-59  * (offsetPeriods)) -offsetPeriods))
                elif forOptionKey == "dr_last_90_days":             rtnVal = (DateUtil.incrementDate(realTodayInt, 0, 0, (-89  * (offsetPeriods + 1)) -offsetPeriods), DateUtil.incrementDate(realTodayInt, 0, 0, (-89  * (offsetPeriods)) -offsetPeriods))
                elif forOptionKey == "dr_last_120_days":            rtnVal = (DateUtil.incrementDate(realTodayInt, 0, 0, (-119 * (offsetPeriods + 1)) -offsetPeriods), DateUtil.incrementDate(realTodayInt, 0, 0, (-119 * (offsetPeriods)) -offsetPeriods))
                elif forOptionKey == "dr_last_180_days":            rtnVal = (DateUtil.incrementDate(realTodayInt, 0, 0, (-179 * (offsetPeriods + 1)) -offsetPeriods), DateUtil.incrementDate(realTodayInt, 0, 0, (-179 * (offsetPeriods)) -offsetPeriods))
                elif forOptionKey == "last_365_days":               rtnVal = (DateUtil.incrementDate(realTodayInt, 0, 0, (-364 * (offsetPeriods + 1)) -offsetPeriods), DateUtil.incrementDate(realTodayInt, 0, 0, (-364 * (offsetPeriods)) -offsetPeriods))
                elif forOptionKey == "dr_next_month":               rtnVal = (DateUtil.firstDayInMonth(DateUtil.incrementDate(calculatedTodayInt, 0, 1, 0)), DateUtil.lastDayInMonth(DateUtil.incrementDate(calculatedTodayInt, 0, 1, 0)))
                elif forOptionKey == "dr_yesterday":                rtnVal = (DateUtil.incrementDate(calculatedTodayInt, 0, 0, -1), DateUtil.incrementDate(calculatedTodayInt, 0, 0, -1))
                elif forOptionKey == "dr_today":                    rtnVal = (DateUtil.incrementDate(calculatedTodayInt, 0, 0, -0), DateUtil.incrementDate(calculatedTodayInt, 0, 0, -0))
                else: raise Exception("Error: date range key ('%s') invalid?!" %(forOptionKey))

                return DateRange(Integer(rtnVal[0]), Integer(rtnVal[1]))  # Integer() wrappers needed in Jython to resolve overload ambiguity

            @staticmethod
            def getDateRangeFromKey(forOptionKey, offsetPeriods):
                # type: (str, int) -> DateRange

                if offsetPeriods is None: offsetPeriods = 0

                offsetPeriods *= -1

                todayInt = DateUtil.getStrippedDateInt()

                multiOffset = 1
                if forOptionKey ==  "xx_marker_xx":                 pass
                elif forOptionKey == "dr_last_two_fiscal_years":    multiOffset = 2
                elif forOptionKey == "dr_last_three_fiscal_years":  multiOffset = 3
                elif forOptionKey == "dr_last_five_fiscal_years":   multiOffset = 5
                elif forOptionKey == "dr_last_two_years":           multiOffset = 2
                elif forOptionKey == "dr_last_three_years":         multiOffset = 3
                elif forOptionKey == "dr_last_five_years":          multiOffset = 5

                offsetDayTodayInt  = DateUtil.incrementDate(todayInt, 0, 0, -offsetPeriods)
                offsetWeekTodayInt = DateUtil.incrementDate(todayInt, 0, 0, 7 * -offsetPeriods)
                offsetMnthTodayInt = DateUtil.incrementDate(todayInt, 0, -offsetPeriods, 0)
                offsetQrtrTodayInt = DateUtil.incrementDate(todayInt, 0, 3 * -offsetPeriods, 0)
                offsetYearTodayInt = DateUtil.incrementDate(todayInt, multiOffset * -offsetPeriods, 0, 0)

                if forOptionKey ==  "custom_date":                  calculatedTodayInt = None
                elif forOptionKey == "all_dates":                   calculatedTodayInt = None
                elif forOptionKey == "year_to_date":                calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "quarter_to_date":             calculatedTodayInt = offsetQrtrTodayInt
                elif forOptionKey == "month_to_date":               calculatedTodayInt = offsetMnthTodayInt
                elif forOptionKey == "this_year":                   calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "this_fiscal_year":            calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "fiscal_year_to_date":         calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "last_fiscal_year":            calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "dr_last_two_fiscal_years":    calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "dr_last_three_fiscal_years":  calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "dr_last_five_fiscal_years":   calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "last_fiscal_quarter":         calculatedTodayInt = offsetQrtrTodayInt
                elif forOptionKey == "this_quarter":                calculatedTodayInt = offsetQrtrTodayInt
                elif forOptionKey == "this_month":                  calculatedTodayInt = offsetMnthTodayInt
                elif forOptionKey == "this_week":                   calculatedTodayInt = offsetWeekTodayInt
                elif forOptionKey == "last_year":                   calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "dr_last_two_years":           calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "dr_last_three_years":         calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "dr_last_five_years":          calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "last_quarter":                calculatedTodayInt = offsetQrtrTodayInt
                elif forOptionKey == "last_month":                  calculatedTodayInt = offsetMnthTodayInt
                elif forOptionKey == "last_week":                   calculatedTodayInt = offsetWeekTodayInt
                elif forOptionKey == "last_12_months":              calculatedTodayInt = None
                elif forOptionKey == "dr_last_18_months":           calculatedTodayInt = None
                elif forOptionKey == "dr_last_24_months":           calculatedTodayInt = None
                elif forOptionKey == "last_1_day":                  calculatedTodayInt = None
                elif forOptionKey == "last_30_days":                calculatedTodayInt = None
                elif forOptionKey == "dr_last_60_days":             calculatedTodayInt = None
                elif forOptionKey == "dr_last_90_days":             calculatedTodayInt = None
                elif forOptionKey == "dr_last_120_days":            calculatedTodayInt = None
                elif forOptionKey == "dr_last_180_days":            calculatedTodayInt = None
                elif forOptionKey == "last_365_days":               calculatedTodayInt = None
                elif forOptionKey == "dr_next_month":               calculatedTodayInt = offsetMnthTodayInt
                elif forOptionKey == "dr_yesterday":                calculatedTodayInt = offsetDayTodayInt
                elif forOptionKey == "dr_today":                    calculatedTodayInt = offsetDayTodayInt
                else: raise Exception("Error: date range key ('%s') invalid?!" %(forOptionKey))

                calculatedDateRange = MyDateRangeChooser.DateRangeChoice.internalCalculateDateRangeFromKey(forOptionKey, todayInt, calculatedTodayInt, offsetPeriods)

                if debug:
                    if offsetPeriods != 0:
                        originalDateRange = MyDateRangeChooser.DateRangeChoice.internalCalculateDateRangeFromKey(forOptionKey, todayInt, todayInt, 0)
                        myPrint("B", "@@ .getDateRangeFromKey('%s', offsetPeriods: %s): offsetDayTodayInt: %s, offsetWeekTodayInt: %s, offsetMnthTodayInt: %s, offsetQrtrTodayInt: %s, offsetYearTodayInt: %s"
                                %(forOptionKey, offsetPeriods, offsetDayTodayInt, offsetWeekTodayInt, offsetMnthTodayInt, offsetQrtrTodayInt, offsetYearTodayInt))
                        myPrint("B", "@@ originalDateRange: %s, calculatedDateRange: %s" %(originalDateRange, calculatedDateRange))
                    myPrint("B", "@@ .getDateRangeFromKey('%s', %s) returning %s" %(forOptionKey, offsetPeriods, calculatedDateRange))

                return calculatedDateRange

        class DateRangeClickListener(MouseAdapter):
            def __init__(self, callingClass): self.callingClass = callingClass
            def mouseClicked(self, event):
                if (SwingUtilities.isLeftMouseButton(event) and event.getClickCount() > 1):
                    self.callingClass.getChoiceCombo().setSelectedItem(self.callingClass.customOption)

        @staticmethod
        def createDateRangeChoiceFromKey(dateKey):
            # type: (str) -> MyDateRangeChooser.DateRangeChoice
            for optionKey, optionName, sortIdx, legacyKey in MyDateRangeChooser.DR_DATE_OPTIONS:
                if optionKey == dateKey: return MyDateRangeChooser.DateRangeChoice(optionKey, optionName, sortIdx)
            return MyDateRangeChooser.DateRangeChoice("unknown", "Unknown Date Range Name", 0)

        def __init__(self, mdGUI, defaultKey, excludeKeys=None):
            # type: (MoneydanceGUI, str, [str]) -> None
            super(self.__class__, self).__init__()
            if isinstance(excludeKeys, str): excludeKeys = [excludeKeys]
            if excludeKeys is None or not isinstance(excludeKeys, list): excludeKeys = []
            for checkKey in [self.KEY_CUSTOM_DATE_RANGE, self.KEY_DR_ALL_DATES]:
                if checkKey in excludeKeys: excludeKeys.remove(checkKey)
            self.mdGUI = mdGUI
            self.customOption = None
            self.excludeKeys = excludeKeys
            self.name = "MyDateRangeChooser"
            self.defaultKey = defaultKey
            self.allDatesOption = None
            self.dateRangeResult = None                                                                                 # type: DateRange
            self.selectedOptionKeyResult = None
            self.offsetPeriodsResult = 0
            self.lastDeselectedOptionKey = None
            self.ignoreDateChanges = False
            self.isEnabled = True
            self.dateRangeOptions = self.createDateRangeOptions()                                                       # type: [MyDateRangeChooser.DateRangeChoice]

            clickListener = self.DateRangeClickListener(self)

            self.startIntField_JDF = JDateField(mdGUI)
            self.startIntField_JDF.addPropertyChangeListener(JDateField.PROP_DATE_CHANGED, self)                        # noqa
            self.startIntField_JDF.addMouseListener(clickListener)                                                      # noqa

            self.endIntField_JDF = JDateField(mdGUI)
            self.endIntField_JDF.addPropertyChangeListener(JDateField.PROP_DATE_CHANGED, self)                          # noqa
            self.endIntField_JDF.addMouseListener(clickListener)                                                        # noqa

            self.offsetPeriods_JTF = MyJTextFieldAsInt(2, self.mdGUI.getPreferences().getDecimalChar())
            self.offsetPeriods_JTF.addPropertyChangeListener(MyJTextFieldAsInt.PROP_OFFSET_PERIODS_CHANGED, self)

            self.startIntField_LBL = MyJLabel(" ", 4)
            self.endIntField_LBL = MyJLabel(" ", 4)
            self.dateRangeChoice_LBL = MyJLabel(" ", 4)
            self.dateRangeChoice_COMBO = MyJComboBox()
            self.offsetPeriods_LBL = MyJLabel(" ", 4)
            self.preferencesUpdated()
            self.dateRangeSelected()
            self.dateRangeChoice_COMBO.addItemListener(self)

        def setDefaultKey(self, newDefault): self.defaultKey = newDefault
        def getDefaultKey(self): return self.defaultKey
        def setName(self, newName): self.name = newName
        def getName(self): return self.name
        def getActionListeners(self): return []
        def getFocusListeners(self): return []
        def getPropertyChangeListeners(self): return self.eventNotify.getPropertyChangeListeners()
        # def getPropertyChangeListeners(self): return getFieldByReflection(self, getEventNotifyName()).getPropertyChangeListeners()

        def createDateRangeOptions(self):
            choices = [MyDateRangeChooser.DateRangeChoice(choice[0], choice[1], choice[2]) for choice in sorted(self.DR_DATE_OPTIONS, key=lambda x: (x[2])) if choice[0] not in self.excludeKeys]
            for choice in choices:
                if choice.getKey() == self.KEY_CUSTOM_DATE_RANGE: self.customOption = choice
                if choice.getKey() == self.KEY_DR_ALL_DATES: self.allDatesOption = choice
            return choices

        def getStartLabel(self):            return self.startIntField_LBL
        def getEndLabel(self):              return self.endIntField_LBL
        def getStartField(self):            return self.startIntField_JDF
        def getEndField(self):              return self.endIntField_JDF
        def getChoiceLabel(self):           return self.dateRangeChoice_LBL
        def getChoiceCombo(self):           return self.dateRangeChoice_COMBO
        def getOffsetPeriodsLabel(self):    return self.offsetPeriods_LBL
        def getOffsetPeriodsField(self):    return self.offsetPeriods_JTF
        def getAllSwingComponents(self):    return [self.getStartLabel(), self.getEndLabel(), self.getStartField(), self.getEndField(), self.getChoiceLabel(), self.getChoiceCombo(), self.getOffsetPeriodsLabel(), self.getOffsetPeriodsField()]

        def isCustomAsOfDatesSelected(self): return self.getChoiceCombo().getSelectedItem().equals(self.customOption)
        def isAllAsOfDatesSelected(self): return self.getChoiceCombo().getSelectedItem().equals(self.allDatesOption)

        def selectAllAsOfDates(self):
            self.getChoiceCombo().setSelectedItem(self.allDatesOption)
            self.dateRangeSelected()

        def preferencesUpdated(self):
            prefs = self.mdGUI.getPreferences()
            self.getStartField().setDateFormat(prefs.getShortDateFormatter())
            self.getEndField().setDateFormat(prefs.getShortDateFormatter())
            self.getStartLabel().setText("Start date:")
            self.getEndLabel().setText("End date:")
            self.getChoiceLabel().setText("Date range:")
            self.getOffsetPeriodsLabel().setText("offset:")
            self.getOffsetPeriodsField().setValueInt(self.getOffsetPeriodsField().defaultValue)
            dateRangeSel = self.getSelectedIndex()
            self.getChoiceCombo().setModel(DefaultComboBoxModel(self.dateRangeOptions))
            prototypeText = ""
            # protoChoice = None
            # for choice in self.dateRangeOptions:
            #     text = choice.getDisplayName()
            #     if len(text) <= len(prototypeText): continue
            #     prototypeText = text
            #     protoChoice = choice
            # if protoChoice is None: protoChoice = self.dateRangeOptions[0]
            # self.getChoiceCombo().setPrototypeDisplayValue(self.DateRangeChoice(protoChoice.getKey(), protoChoice.getDisplayName(), protoChoice.getSortIdx()))
            for choice in self.DR_DATE_OPTIONS:
                text = choice[1]
                if len(text) <= len(prototypeText): continue
                prototypeText = text
            self.getChoiceCombo().setPrototypeDisplayValue(prototypeText)
            self.getChoiceCombo().setMaximumRowCount(len(self.dateRangeOptions))
            if (dateRangeSel >= 0): self.getChoiceCombo().setSelectedIndex(dateRangeSel)

        def getPanel(self, includeChoiceLabel=True, horizontal=True):
            p = MyJPanel(GridBagLayout())
            x = 0; y = 0
            vertInc = 0 if horizontal else 1
            if includeChoiceLabel:
                p.add(self.getChoiceLabel(),        GridC.getc(x, y).label()); x += 1
            p.add(self.getChoiceCombo(),            GridC.getc(x, y).field()); x += 1; y += vertInc
            if not horizontal: x = 0
            p.add(self.getStartLabel(),          GridC.getc(x, y).label()); x += 1
            p.add(self.getStartField(),          GridC.getc(x, y).field()); x += 1; y += vertInc
            if not horizontal: x = 0
            p.add(self.getEndLabel(),            GridC.getc(x, y).label()); x += 1
            p.add(self.getEndField(),            GridC.getc(x, y).field()); x += 1; y += vertInc
            if not horizontal: x = 0
            p.add(self.getOffsetPeriodsLabel(),   GridC.getc(x, y).label()); x += 1
            p.add(self.getOffsetPeriodsField(),   GridC.getc(x, y).field()); x += 1; y += vertInc
            return p

        def setSelectedOptionKey(self, dateOptionKey):
            # type: (str) -> bool
            lSetOption = False
            for choice in self.dateRangeOptions:
                if choice.getKey() == dateOptionKey:
                    lSetOption = True
                    self.getChoiceCombo().setSelectedItem(choice)
                    break
            if lSetOption: self.dateRangeSelected()
            return lSetOption

        def getSelectedOptionKey(self, position): return self.dateRangeOptions[position].getKey()

        def getSelectedIndex(self):
            sel = self.getChoiceCombo().getSelectedIndex()
            if sel < 0: sel = 0
            return sel

        def setStartDate(self, startDateInt):
            self.getChoiceCombo().setSelectedItem(self.customOption)
            self.getStartField().setDateInt(startDateInt)
            self.dateRangeSelected()

        def setEndDate(self, endDateInt):
            self.getChoiceCombo().setSelectedItem(self.customOption)
            self.getEndField().setDateInt(endDateInt)
            self.dateRangeSelected()

        def getDateRange(self):
            # type: () -> DateRange
            if self.dateRangeResult is None: self.dateRangeSelected()
            return self.dateRangeResult

        def setOffsetPeriods(self, offsetPeriods):
            self.getOffsetPeriodsField().setValueInt(offsetPeriods)
            self.dateRangeSelected()

        def getOffsetPeriods(self):
            # if self.offsetPeriodsResult is None: self.dateRangeSelected()
            return self.offsetPeriodsResult

        def dateRangeSelected(self):
            dr = self.getDateRangeFromSelectedOption()
            offsetPeriods = self.getOffsetPeriodsField().getValueInt()
            # myPrint("B", "@@ MyDateRangeChooser:%s:dateRangeSelected() - getDateRangeFromSelectedOption() reports: '%s'" %(self.getName(), dr))
            self.ignoreDateChanges = True
            self.getStartField().setDateInt(dr.getStartDateInt())
            self.getEndField().setDateInt(dr.getEndDateInt())
            self.getOffsetPeriodsField().setValueInt(offsetPeriods)
            self.ignoreDateChanges = False
            self.setDateRange(dr, offsetPeriods)
            self.updateEnabledStatus()

        @staticmethod
        def convertSettingsToSyncRecord(drSettings):                   # For use with MD2024(5100) enhanced DRC class...
            if not isDateRangeChooserUpgradedBuild(): raise Exception("Error: convertSettingsToSyncRecord() can only be used on MD2024(5100) onwards!")
            syncRecord = SyncRecord()
            drOptionKey = drSettings[MyDateRangeChooser.DRC_DR_KEY_IDX]
            drStartDateInt = drSettings[MyDateRangeChooser.DRC_DR_START_KEY_IDX]
            drEndDateInt = drSettings[MyDateRangeChooser.DRC_DR_END_KEY_IDX]
            offsetPeriods = drSettings[MyDateRangeChooser.DRC_DR_OFFSETPERIODS_IDX]
            syncRecord.put(DateRangeOption.CONFIG_KEY, drOptionKey)
            MDURLUtil.putDate(syncRecord, DateRangeChooser.PARAM_START_DATE, Integer(drStartDateInt))
            MDURLUtil.putDate(syncRecord, DateRangeChooser.PARAM_END_DATE, Integer(drEndDateInt))
            MDURLUtil.putInt(syncRecord, DateRangeChooser.PARAM_OFFSET_PERIODS, Integer(offsetPeriods))                 # noqa
            if True or debug: myPrint("B", "convertSettingsToSyncRecord: '%s' converted to: '%s'" %(drSettings, syncRecord))
            return syncRecord

        @staticmethod
        def convertSyncRecordToSettings(syncRecord, defaultSettings):  # For use with MD2024(5100) enhanced DRC class...
            if not isDateRangeChooserUpgradedBuild(): raise Exception("Error: convertSyncRecordToSettings() can only be used on MD2024(5100) onwards!")
            drOptionKey = syncRecord.getString(DateRangeOption.CONFIG_KEY, defaultSettings[MyDateRangeChooser.DRC_DR_KEY_IDX])
            drStartDateInt = MDURLUtil.getDate(syncRecord, DateRangeChooser.PARAM_START_DATE, defaultSettings[MyDateRangeChooser.DRC_DR_START_KEY_IDX])
            drEndDateInt = MDURLUtil.getDate(syncRecord, DateRangeChooser.PARAM_END_DATE, defaultSettings[MyDateRangeChooser.DRC_DR_END_KEY_IDX])
            offsetPeriods = MDURLUtil.getInt(syncRecord, DateRangeChooser.PARAM_OFFSET_PERIODS, defaultSettings[MyDateRangeChooser.DRC_DR_OFFSETPERIODS_IDX])   # noqa
            newSettings = copy.deepcopy(defaultSettings)
            newSettings[MyDateRangeChooser.DRC_DR_KEY_IDX] = drOptionKey
            newSettings[MyDateRangeChooser.DRC_DR_START_KEY_IDX] = drStartDateInt
            newSettings[MyDateRangeChooser.DRC_DR_END_KEY_IDX] = drEndDateInt
            newSettings[MyDateRangeChooser.DRC_DR_OFFSETPERIODS_IDX] = offsetPeriods
            if True or debug: myPrint("B", "convertSyncRecordToSettings: '%s' converted to: '%s'" %(syncRecord, newSettings))
            return newSettings

        def loadFromParameters(self, drSettings, defaultKey):
            # type: ([bool, str, int, int, int], str) -> bool

            # todo - the original 'setOption(defaultKey)' was recently moved to only run when the settings don't contain this date config key...
            if not self.setSelectedOptionKey(defaultKey): raise Exception("ERROR: Default i/e date range option/key ('%s') not found?!" %(defaultKey))

            # drOptionEnabled = drSettings[MyDateRangeChooser.DRC_DR_ENABLED_IDX]
            drOptionKey = drSettings[MyDateRangeChooser.DRC_DR_KEY_IDX]
            drStartDateInt = drSettings[MyDateRangeChooser.DRC_DR_START_KEY_IDX]
            drEndDateInt = drSettings[MyDateRangeChooser.DRC_DR_END_KEY_IDX]
            offsetPeriods = drSettings[MyDateRangeChooser.DRC_DR_OFFSETPERIODS_IDX]

            if drOptionKey is None or drOptionKey == "": drOptionKey = defaultKey
            drSettings[MyDateRangeChooser.DRC_DR_KEY_IDX] = drOptionKey

            foundSetting = False
            self.getOffsetPeriodsField().setValueInt(offsetPeriods)
            if drOptionKey == self.KEY_CUSTOM_DATE_RANGE:
                if MyDateRangeChooser.isValidDateRange(drSettings):
                    self.setStartDate(drStartDateInt)
                    self.setEndDate(drEndDateInt)
                    foundSetting = True
            else:
                foundSetting = self.setSelectedOptionKey(drOptionKey)
            if not foundSetting:
                myPrint("B", "@@ %s::loadFromParameters() - date range settings ('%s %s') not found / invalid?! Loaded default ('%s')"
                        %(self.getName(), drOptionKey, drSettings, defaultKey))
            else:
                if debug: myPrint("B", "Successfully loaded date range date settings ('%s %s')" %(drOptionKey, drSettings))
            return foundSetting

        def returnStoredParameters(self, defaultDRSettings):
            # type: ([bool, str, int, int, int]) -> ([bool, str, int, int, int])
            drSettings = copy.deepcopy(defaultDRSettings)
            dr = self.getDateRange()
            selectedOptionKey = self.getSelectedOptionKey(self.getSelectedIndex())
            startDateInt = dr.getStartDateInt()
            endDateInt = dr.getEndDateInt()
            offsetPeriods = self.getOffsetPeriodsField().getValueInt()
            # leave settings[MyDateRangeChooser.DRC_DR_ENABLED_IDX] untouched
            drSettings[MyDateRangeChooser.DRC_DR_KEY_IDX] = selectedOptionKey
            drSettings[MyDateRangeChooser.DRC_DR_START_KEY_IDX] = startDateInt if (selectedOptionKey == self.KEY_CUSTOM_DATE_RANGE) else 0
            drSettings[MyDateRangeChooser.DRC_DR_END_KEY_IDX] = endDateInt if (selectedOptionKey == self.KEY_CUSTOM_DATE_RANGE) else 0
            drSettings[MyDateRangeChooser.DRC_DR_OFFSETPERIODS_IDX] = offsetPeriods
            if debug: myPrint("B", "%s::returnStoredParameters() - Returning stored date range parameters settings ('%s')" %(self.getName(), drSettings))
            return drSettings

        @staticmethod
        def isValidDateRange(drSettings):
            # type: ([bool, str, int, int, int]) -> bool
            _startInt = drSettings[MyDateRangeChooser.DRC_DR_START_KEY_IDX]
            _endInt = drSettings[MyDateRangeChooser.DRC_DR_END_KEY_IDX]
            _offsetPeriods = drSettings[MyDateRangeChooser.DRC_DR_OFFSETPERIODS_IDX]
            if not isinstance(_startInt, (int, Integer)):               return False
            if not isinstance(_endInt, (int, Integer)):                 return False
            if not isinstance(_offsetPeriods, (int, Integer, long)):    return False
            if _startInt <= MyDateRangeChooser.DATE_RANGE_VALID:        return False
            if _endInt   <= MyDateRangeChooser.DATE_RANGE_VALID:        return False
            if _startInt > _endInt:                                     return False
            return True

        def setDateRange(self, dr, offsetPeriods):
            # type: (DateRange, int) -> None
            oldDateRange = self.dateRangeResult
            oldSelectedKey = self.selectedOptionKeyResult
            oldOffsetPeriods = self.offsetPeriodsResult
            selectedOptionKey = self.getSelectedOptionKey(self.getSelectedIndex())
            # myPrint("B", "@@ MyDateRangeChooser:%s:setDateRange(%s) (old asof date: %s), selectedKey: '%s' (old key: '%s')" %(self.getName(), dr, oldDateRange, selectedOptionKey, oldSelectedKey));
            if not dr.equals(oldDateRange) or selectedOptionKey != oldSelectedKey or offsetPeriods != oldOffsetPeriods:
                self.dateRangeResult = dr
                self.selectedOptionKeyResult = selectedOptionKey
                self.offsetPeriodsResult = offsetPeriods
                if not dr.equals(oldDateRange):
                    # if debug:
                    #     myPrint("B", "@@ MyDateRangeChooser:%s:setDateRange(%s).firePropertyChange(%s) >> asof date changed (from: %s to %s) <<" %(self.getName(), dr, self.PROP_DATE_RANGE_CHANGED, oldDateRange, dr))
                    self.eventNotify.firePropertyChange(self.PROP_DATE_RANGE_CHANGED, oldDateRange, dr)
                elif selectedOptionKey != oldSelectedKey:
                    # if debug:
                    #     myPrint("B", "@@ MyDateRangeChooser:%s:setDateRange(%s).firePropertyChange(%s) >> selected key changed (from: '%s' to '%s') <<" %(self.getName(), dr, self.PROP_DATE_RANGE_CHANGED, oldSelectedKey, selectedOptionKey))
                    self.eventNotify.firePropertyChange(self.PROP_DATE_RANGE_CHANGED, oldSelectedKey, selectedOptionKey)
                elif offsetPeriods != oldOffsetPeriods:
                    # if debug:
                    #     myPrint("B", "@@ MyDateRangeChooser:%s:setDateRange(%s).firePropertyChange(%s) >> selected key changed (from: '%s' to '%s') <<" %(self.getName(), dr, self.PROP_DATE_RANGE_CHANGED, oldOffsetPeriods, offsetPeriods))
                    self.eventNotify.firePropertyChange(self.PROP_DATE_RANGE_CHANGED, oldOffsetPeriods, offsetPeriods)

        def setEnabled(self, isEnabled, shouldHide=False):
            self.isEnabled = isEnabled
            self.updateEnabledStatus(shouldHide=shouldHide)

        def updateEnabledStatus(self, shouldHide=False):
            for comp in self.getAllSwingComponents():
                comp.setEnabled(self.isEnabled)
                if shouldHide: comp.setVisible(self.isEnabled)

        def itemStateChanged(self, evt):
            src = evt.getItemSelectable()                                                                               # type: JComboBox
            paramString = evt.paramString()
            state = evt.getStateChange()
            changedItem = evt.getItem()                                                                                 # type: MyDateRangeChooser.DateRangeChoice

            myClazzName = "MyDateRangeChooser"
            propKey = self.PROP_DATE_RANGE_CHANGED
            onSelectionMethod = self.dateRangeSelected

            defaultLast = "<unknown>"
            if self.lastDeselectedOptionKey is None: self.lastDeselectedOptionKey = defaultLast

            if src is self.getChoiceCombo():

                if state == ItemEvent.DESELECTED:
                    oldDeselected = self.lastDeselectedOptionKey
                    newDeselected = changedItem.getKey()
                    self.lastDeselectedOptionKey = newDeselected
                    if debug:
                        myPrint("B", "@@ %s:%s:itemStateChanged(%s).firePropertyChange(%s) >> last deselected changed (from: '%s' to '%s') (paramString: '%s') <<"
                                %(myClazzName, self.getName(), state, propKey, oldDeselected, newDeselected, paramString))

                elif state == ItemEvent.SELECTED:
                    lastDeselected = self.lastDeselectedOptionKey
                    newSelected = changedItem.getKey()
                    if debug:
                        myPrint("B", "@@ %s:%s:itemStateChanged(%s).firePropertyChange(%s) >> selection changed (from: '%s' to '%s') (paramString: '%s') <<"
                                %(myClazzName, self.getName(), state, propKey, lastDeselected, newSelected, paramString))
                    self.eventNotify.firePropertyChange(propKey,  lastDeselected, newSelected)
                    onSelectionMethod()
                    self.lastDeselectedOptionKey = None

        def propertyChange(self, event):
            # myPrint("B", "@@ MyDateRangeChooser:%s:propertyChange('%s') - .getSelectedOptionKey() reports: '%s'" %(self.getName(), event.getPropertyName(), self.getSelectedOptionKey(self.getSelectedIndex())));
            if (event.getPropertyName() == JDateField.PROP_DATE_CHANGED and not self.ignoreDateChanges):
                selectedOptionKey = self.getSelectedOptionKey(self.getSelectedIndex())
                if (selectedOptionKey != self.KEY_CUSTOM_DATE_RANGE and self.datesVaryFromSelectedOption()):
                    self.getChoiceCombo().setSelectedItem(self.customOption)
                if (selectedOptionKey == self.KEY_CUSTOM_DATE_RANGE):
                    self.setDateRange(DateRange(Integer(self.getStartField().getDateInt()), Integer(self.getEndField().getDateInt())), self.getOffsetPeriodsField().getValueInt())  # Integer() wrappers needed in Jython to resolve overload ambiguity
            if (event.getPropertyName() == MyJTextFieldAsInt.PROP_OFFSET_PERIODS_CHANGED and not self.ignoreDateChanges):
                self.setDateRange(DateRange(Integer(self.getStartField().getDateInt()), Integer(self.getEndField().getDateInt())), self.getOffsetPeriodsField().getValueInt())  # Integer() wrappers needed in Jython to resolve overload ambiguity
                self.dateRangeSelected()

        def datesVaryFromSelectedOption(self):
            startDateInt = self.getStartField().getDateInt()
            endDateInt = self.getEndField().getDateInt()
            dr = self.getDateRangeFromSelectedOption()
            return (startDateInt != dr.getStartDateInt() or endDateInt != dr.getEndDateInt())

        def getDateRangeFromSelectedOption(self):
            selectedOptionKey = self.getSelectedOptionKey(self.getSelectedIndex())
            if (selectedOptionKey == self.KEY_CUSTOM_DATE_RANGE):
                return DateRange(Integer(self.getStartField().parseDateInt()), Integer(self.getEndField().parseDateInt()))  # Integer() wrappers needed in Jython to resolve overload ambiguity
            return self.DateRangeChoice.getDateRangeFromKey(selectedOptionKey, self.getOffsetPeriods())

        def toString(self):  return self.__str__()
        def __repr__(self):  return self.__str__()
        def __str__(self):
            return "MyDateRangeChooser::%s - key: '%s' startInt: %s, endInt: %s, offset: %s" %(self.getName(), self.getSelectedOptionKey(self.getSelectedIndex()), self.getStartField().getDateInt(), self.getEndField().getDateInt(), self.getOffsetPeriodsField().getValueInt())

    class AsOfDateChooser(MyBasePropertyChangeReporter, ItemListener, PropertyChangeListener):    # Based on: com.moneydance.apps.md.view.gui.DateRangeChooser
        """Class that allows selection of an AsOf date. Listen to changes using java.beans.PropertyChangeListener() on "asOfChanged
        Version 1 (v1: initial release)"""

        ASOF_DATE_VALID = 19000101

        ASOF_DRC_ENABLED_IDX = 0
        ASOF_DRC_KEY_IDX = 1
        ASOF_DRC_DATEINT_IDX = 2
        ASOF_DRC_OFFSETPERIODS_IDX = 3

        PROP_ASOF_CHANGED = "asOfChanged"
        ASOF_TODAY = "asof_today"
        KEY_CUSTOM_ASOF = "custom_asof"
        KEY_ASOF_END_FUTURE = "asof_end_future"
        KEY_ASOF_END_THIS_MONTH = "asof_end_this_month"
        ASOF_DATE_OPTIONS = [
                              ["asof_today",                    "asof today",                      1],
                              ["asof_yesterday",                "asof yesterday",                  2],
                              ["asof_end_last_fiscal_quarter",  "asof end last Fiscal Quarter",   31],
                              ["asof_end_this_fiscal_year",     "asof end this Fiscal Year",      30],
                              ["asof_end_this_year",            "asof end this year",             13],
                              ["asof_end_this_quarter",         "asof end this quarter",          12],
                              ["asof_end_this_month",           "asof end this month",            11],
                              ["asof_end_this_week",            "asof end this week",             10],
                              ["asof_end_next_month",           "asof end next month",             3],
                              ["asof_end_last_year",            "asof end last year",             23],
                              ["asof_end_last_fiscal_year",     "asof end last Fiscal Year",      32],
                              ["asof_end_last_quarter",         "asof end last quarter",          22],
                              ["asof_end_last_month",           "asof end last month",            21],
                              ["asof_end_last_week",            "asof end last week",             20],
                              ["asof_30_days_ago",              "asof 30 days ago",               40],
                              ["asof_60_days_ago",              "asof 60 days ago",               41],
                              ["asof_90_days_ago",              "asof 90 days ago",               42],
                              ["asof_120_days_ago",             "asof 120 days ago",              43],
                              ["asof_180_days_ago",             "asof 180 days ago",              44],
                              ["asof_365_days_ago",             "asof 365 days ago",              45],
                              ["asof_end_future",               "asof end future (all dates)",     0],
                              ["custom_asof",                   "Custom asof date",               99]
                            ]

        class AsOfDateChoice:
            def __init__(self, key, displayName, sortIdx):
                self.key = key
                self.displayName = displayName
                self.sortIdx = sortIdx
            def getKey(self):           return self.key
            def getDisplayName(self):   return self.displayName
            def getSortIdx(self):       return self.sortIdx
            def __str__(self):          return self.getDisplayName()
            def __repr__(self):         return self.__str__()
            def toString(self):         return self.__str__()

            @staticmethod
            def internalCalculateAsOfDateFromKey(forOptionKey, realTodayInt, calculatedTodayInt, offsetPeriods):
                # type: (str, int, int, int) -> int
                if forOptionKey == "custom_asof":                    rtnVal = realTodayInt
                elif forOptionKey ==  "asof_end_future":             rtnVal = DateRange().getEndDateInt()
                elif forOptionKey == "asof_today":                   rtnVal = DateUtil.incrementDate(calculatedTodayInt, 0, 0, -0)
                elif forOptionKey == "asof_yesterday":               rtnVal = DateUtil.incrementDate(calculatedTodayInt, 0, 0, -1)
                elif forOptionKey == "asof_end_this_fiscal_year":    rtnVal = DateUtil.lastDayInFiscalYear(calculatedTodayInt)
                elif forOptionKey == "asof_end_last_fiscal_year":    rtnVal = DateUtil.decrementYear(DateUtil.lastDayInFiscalYear(calculatedTodayInt))
                elif forOptionKey == "asof_end_last_fiscal_quarter": rtnVal = DateUtil.lastDayInFiscalQuarter(DateUtil.incrementDate(calculatedTodayInt, 0, -3, 0))
                elif forOptionKey == "asof_end_this_quarter":        rtnVal = DateUtil.lastDayInQuarter(calculatedTodayInt)
                elif forOptionKey == "asof_end_this_year":           rtnVal = DateUtil.lastDayInYear(calculatedTodayInt)
                elif forOptionKey == "asof_end_this_month":          rtnVal = DateUtil.lastDayInMonth(calculatedTodayInt)
                elif forOptionKey == "asof_end_next_month":          rtnVal = DateUtil.lastDayInMonth(DateUtil.incrementDate(calculatedTodayInt, 0, 1, 0))
                elif forOptionKey == "asof_end_this_week":           rtnVal = DateUtil.lastDayInWeek(calculatedTodayInt)
                elif forOptionKey == "asof_end_last_year":           rtnVal = DateUtil.lastDayInYear(DateUtil.decrementYear(calculatedTodayInt))
                elif forOptionKey == "asof_end_last_quarter":        rtnVal = DateUtil.lastDayInQuarter(DateUtil.incrementDate(calculatedTodayInt, 0, -3, 0))
                elif forOptionKey == "asof_end_last_month":          rtnVal = DateUtil.incrementDate(DateUtil.firstDayInMonth(calculatedTodayInt), 0, 0, -1)
                elif forOptionKey == "asof_end_last_week":           rtnVal = DateUtil.incrementDate(DateUtil.firstDayInWeek(calculatedTodayInt), 0, 0, -1)
                elif forOptionKey == "asof_30_days_ago":             rtnVal = DateUtil.incrementDate(realTodayInt, 0, 0, (-29  * (offsetPeriods + 1)) -offsetPeriods)
                elif forOptionKey == "asof_60_days_ago":             rtnVal = DateUtil.incrementDate(realTodayInt, 0, 0, (-59  * (offsetPeriods + 1)) -offsetPeriods)
                elif forOptionKey == "asof_90_days_ago":             rtnVal = DateUtil.incrementDate(realTodayInt, 0, 0, (-89  * (offsetPeriods + 1)) -offsetPeriods)
                elif forOptionKey == "asof_120_days_ago":            rtnVal = DateUtil.incrementDate(realTodayInt, 0, 0, (-119 * (offsetPeriods + 1)) -offsetPeriods)
                elif forOptionKey == "asof_180_days_ago":            rtnVal = DateUtil.incrementDate(realTodayInt, 0, 0, (-179 * (offsetPeriods + 1)) -offsetPeriods)
                elif forOptionKey == "asof_365_days_ago":            rtnVal = DateUtil.incrementDate(realTodayInt, 0, 0, (-364 * (offsetPeriods + 1)) -offsetPeriods)
                else: raise Exception("Error: asof date key ('%s') invalid?!" %(forOptionKey))
                return rtnVal

            @staticmethod
            def getAsOfDateFromKey(forOptionKey, offsetPeriods):
                # type: (str, int) -> int

                if offsetPeriods is None: offsetPeriods = 0

                offsetPeriods *= -1

                todayInt = DateUtil.getStrippedDateInt()

                offsetDayTodayInt  = DateUtil.incrementDate(todayInt, 0, 0, -offsetPeriods)
                offsetWeekTodayInt = DateUtil.incrementDate(todayInt, 0, 0, 7 * -offsetPeriods)
                offsetMnthTodayInt = DateUtil.incrementDate(todayInt, 0, -offsetPeriods, 0)
                offsetQrtrTodayInt = DateUtil.incrementDate(todayInt, 0, 3 * -offsetPeriods, 0)
                offsetYearTodayInt = DateUtil.incrementDate(todayInt, -offsetPeriods, 0, 0)

                if forOptionKey == "custom_asof":                    calculatedTodayInt = None
                elif forOptionKey ==  "asof_end_future":             calculatedTodayInt = None
                elif forOptionKey == "asof_today":                   calculatedTodayInt = offsetDayTodayInt
                elif forOptionKey == "asof_yesterday":               calculatedTodayInt = offsetDayTodayInt
                elif forOptionKey == "asof_end_this_fiscal_year":    calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "asof_end_last_fiscal_year":    calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "asof_end_last_fiscal_quarter": calculatedTodayInt = offsetQrtrTodayInt
                elif forOptionKey == "asof_end_this_quarter":        calculatedTodayInt = offsetQrtrTodayInt
                elif forOptionKey == "asof_end_this_year":           calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "asof_end_this_month":          calculatedTodayInt = offsetMnthTodayInt
                elif forOptionKey == "asof_end_next_month":          calculatedTodayInt = offsetMnthTodayInt
                elif forOptionKey == "asof_end_this_week":           calculatedTodayInt = offsetWeekTodayInt
                elif forOptionKey == "asof_end_last_year":           calculatedTodayInt = offsetYearTodayInt
                elif forOptionKey == "asof_end_last_quarter":        calculatedTodayInt = offsetQrtrTodayInt
                elif forOptionKey == "asof_end_last_month":          calculatedTodayInt = offsetMnthTodayInt
                elif forOptionKey == "asof_end_last_week":           calculatedTodayInt = offsetWeekTodayInt
                elif forOptionKey == "asof_30_days_ago":             calculatedTodayInt = None
                elif forOptionKey == "asof_60_days_ago":             calculatedTodayInt = None
                elif forOptionKey == "asof_90_days_ago":             calculatedTodayInt = None
                elif forOptionKey == "asof_120_days_ago":            calculatedTodayInt = None
                elif forOptionKey == "asof_180_days_ago":            calculatedTodayInt = None
                elif forOptionKey == "asof_365_days_ago":            calculatedTodayInt = None
                else: raise Exception("Error: asof date key ('%s') invalid?!" %(forOptionKey))

                calculatedDateInt = AsOfDateChooser.AsOfDateChoice.internalCalculateAsOfDateFromKey(forOptionKey, todayInt, calculatedTodayInt, offsetPeriods)

                if debug:
                    if offsetPeriods != 0:
                        originalDateInt = AsOfDateChooser.AsOfDateChoice.internalCalculateAsOfDateFromKey(forOptionKey, todayInt, todayInt, 0)
                        myPrint("B", "@@ .getAsOfDateFromKey('%s', offsetPeriods: %s): offsetDayTodayInt: %s, offsetWeekTodayInt: %s, offsetMnthTodayInt: %s, offsetQrtrTodayInt: %s, offsetYearTodayInt: %s"
                                %(forOptionKey, offsetPeriods, offsetDayTodayInt, offsetWeekTodayInt, offsetMnthTodayInt, offsetQrtrTodayInt, offsetYearTodayInt))
                        myPrint("B", "@@ originalDateInt: %s, calculatedDateInt: %s" %(originalDateInt, calculatedDateInt))
                    myPrint("B", "@@ .getAsOfDateFromKey('%s', %s) returning %s" %(forOptionKey, offsetPeriods, calculatedDateInt))

                return calculatedDateInt

        class AsOfDateClickListener(MouseAdapter):
            def __init__(self, callingClass):   self.callingClass = callingClass
            def mouseClicked(self, event):
                if (SwingUtilities.isLeftMouseButton(event) and event.getClickCount() > 1):
                    self.callingClass.asOfChoice_COMBO.setSelectedItem(self.callingClass.customOption)

        @staticmethod
        def createAsOfDateChoiceFromKey(dateKey):
            # type: (str) -> AsOfDateChooser.AsOfDateChoice
            for optionKey, optionName, sortIdx in AsOfDateChooser.ASOF_DATE_OPTIONS:
                if optionKey == dateKey: return AsOfDateChooser.AsOfDateChoice(optionKey, optionName, sortIdx)
            return AsOfDateChooser.AsOfDateChoice("unknown", "Unknown AsOf Date Name", 0)

        def __init__(self, mdGUI, defaultKey, excludeKeys=None):
            # type: (MoneydanceGUI, str, [str]) -> None
            super(self.__class__, self).__init__()
            if isinstance(excludeKeys, str): excludeKeys = [excludeKeys]
            if excludeKeys is None or not isinstance(excludeKeys, list): excludeKeys = []
            for checkKey in [self.KEY_CUSTOM_ASOF, self.KEY_ASOF_END_FUTURE]:
                if checkKey in excludeKeys: excludeKeys.remove(checkKey)
            self.mdGUI = mdGUI
            self.customOption = None
            self.excludeKeys = excludeKeys
            self.name = "AsOfDateChooser"
            self.defaultKey = defaultKey
            self.allDatesOption = None
            self.asOfDateIntResult = None
            self.selectedOptionKeyResult = None
            self.offsetPeriodsResult = 0
            self.lastDeselectedOptionKey = None
            self.ignoreDateChanges = False
            self.isEnabled = True
            self.asOfOptions = self.createAsOfDateOptions()                                                             # type: [AsOfDateChooser.AsOfDateChoice]

            self.asOfDate_JDF = JDateField(mdGUI)
            self.asOfDate_JDF.addPropertyChangeListener(JDateField.PROP_DATE_CHANGED, self)                             # noqa
            self.asOfDate_JDF.addMouseListener(self.AsOfDateClickListener(self))                                        # noqa

            self.offsetPeriods_JTF = MyJTextFieldAsInt(2, self.mdGUI.getPreferences().getDecimalChar())
            self.offsetPeriods_JTF.addPropertyChangeListener(MyJTextFieldAsInt.PROP_OFFSET_PERIODS_CHANGED, self)

            # self.asOfDate_JDF.setFocusable(True)
            # self.asOfDate_JDF.addKeyListener(MyKeyAdapter())

            self.asOfDate_LBL = MyJLabel(" ", 4)
            self.asOfChoice_LBL = MyJLabel(" ", 4)
            self.asOfChoice_COMBO = MyJComboBox()
            self.offsetPeriods_LBL = MyJLabel(" ", 4)
            self.preferencesUpdated()
            self.asOfSelected()
            self.asOfChoice_COMBO.addItemListener(self)

        def setDefaultKey(self, newDefault): self.defaultKey = newDefault
        def getDefaultKey(self): return self.defaultKey
        def setName(self, newName): self.name = newName
        def getName(self): return self.name
        def getActionListeners(self): return []
        def getFocusListeners(self): return []
        def getPropertyChangeListeners(self): return self.eventNotify.getPropertyChangeListeners()
        # def getPropertyChangeListeners(self): return getFieldByReflection(self, getEventNotifyName()).getPropertyChangeListeners()

        def createAsOfDateOptions(self):
            choices = [AsOfDateChooser.AsOfDateChoice(choice[0], choice[1], choice[2]) for choice in sorted(self.ASOF_DATE_OPTIONS, key=lambda x: (x[2])) if choice[0] not in self.excludeKeys]
            for choice in choices:
                if choice.getKey() == self.KEY_CUSTOM_ASOF: self.customOption = choice
                if choice.getKey() == self.KEY_ASOF_END_FUTURE: self.allDatesOption = choice
            return choices

        def getAsOfLabel(self):             return self.asOfDate_LBL
        def getAsOfDateField(self):         return self.asOfDate_JDF
        def getChoiceLabel(self):           return self.asOfChoice_LBL
        def getChoiceCombo(self):           return self.asOfChoice_COMBO
        def getOffsetPeriodsLabel(self):    return self.offsetPeriods_LBL
        def getOffsetPeriodsField(self):    return self.offsetPeriods_JTF
        def getAllSwingComponents(self):    return [self.getAsOfLabel(), self.getAsOfDateField(), self.getChoiceLabel(), self.getChoiceCombo(), self.getOffsetPeriodsLabel(), self.getOffsetPeriodsField()]

        def isCustomAsOfDatesSelected(self): return self.getChoiceCombo().getSelectedItem().equals(self.customOption)
        def isAllAsOfDatesSelected(self): return self.getChoiceCombo().getSelectedItem().equals(self.allDatesOption)

        def selectAllAsOfDates(self):
            self.getChoiceCombo().setSelectedItem(self.allDatesOption)
            self.asOfSelected()

        def preferencesUpdated(self):
            prefs = self.mdGUI.getPreferences()
            self.asOfDate_JDF.setDateFormat(prefs.getShortDateFormatter())
            self.asOfDate_LBL.setText("date:")
            self.asOfChoice_LBL.setText("Balance:")
            self.offsetPeriods_LBL.setText("offset:")
            self.offsetPeriods_JTF.setValueInt(self.offsetPeriods_JTF.defaultValue)
            asOfSel = self.getSelectedIndex()
            self.getChoiceCombo().setModel(DefaultComboBoxModel(self.asOfOptions))
            prototypeText = ""
            # protoChoice = None
            # for choice in self.asOfOptions:
            #     text = choice.getDisplayName()
            #     if len(text) <= len(prototypeText): continue
            #     prototypeText = text
            #     protoChoice = choice
            # if protoChoice is None: protoChoice = self.asOfOptions[0]
            # self.getChoiceCombo().setPrototypeDisplayValue(self.AsOfDateChoice(protoChoice.getKey(), protoChoice.getDisplayName(), protoChoice.getSortIdx()))
            for choice in self.ASOF_DATE_OPTIONS:
                text = choice[1]
                if len(text) <= len(prototypeText): continue
                prototypeText = text
            self.getChoiceCombo().setPrototypeDisplayValue(prototypeText)
            self.getChoiceCombo().setMaximumRowCount(len(self.asOfOptions))
            if (asOfSel >= 0): self.getChoiceCombo().setSelectedIndex(asOfSel)

        def getPanel(self, includeChoiceLabel=True, horizontal=True):
            p = MyJPanel(GridBagLayout())
            x = 0; y = 0
            vertInc = 0 if horizontal else 1
            if includeChoiceLabel:
                p.add(self.getChoiceLabel(),        GridC.getc(x, y).label()); x += 1
            p.add(self.getChoiceCombo(),            GridC.getc(x, y).field()); x += 1; y += vertInc
            if not horizontal: x = 0
            p.add(self.getAsOfLabel(),              GridC.getc(x, y).label()); x += 1
            p.add(self.getAsOfDateField(),          GridC.getc(x, y).field()); x += 1; y += vertInc
            if not horizontal: x = 0
            p.add(self.getOffsetPeriodsLabel(),     GridC.getc(x, y).label()); x += 1
            p.add(self.getOffsetPeriodsField(),     GridC.getc(x, y).field()); x += 1; y += vertInc
            return p

        def setSelectedOptionKey(self, asOfOptionKey):
            lSetOption = False
            for choice in self.asOfOptions:
                if choice.getKey() == asOfOptionKey:
                    lSetOption = True
                    self.getChoiceCombo().setSelectedItem(choice)
                    break
            if lSetOption: self.asOfSelected()
            return lSetOption

        def getSelectedOptionKey(self, position): return self.asOfOptions[position].getKey()

        def getSelectedIndex(self):
            sel = self.getChoiceCombo().getSelectedIndex()
            if sel < 0: sel = 0
            return sel

        def setAsOfDateInt(self, asofDateInt):
            self.getChoiceCombo().setSelectedItem(self.customOption)
            self.asOfDate_JDF.setDateInt(asofDateInt)
            self.asOfSelected()

        def getAsOfDateInt(self):
            if self.asOfDateIntResult is None: self.asOfSelected()
            return Integer(self.asOfDateIntResult).intValue()

        def setOffsetPeriods(self, offsetPeriods):
            self.offsetPeriods_JTF.setValueInt(offsetPeriods)
            self.asOfSelected()

        def getOffsetPeriods(self):
            # if self.offsetPeriodsResult is None: self.asOfSelected()
            return self.offsetPeriodsResult

        def asOfSelected(self):
            asofDateInt = self.getAsOfDateIntFromSelectedOption()
            offsetPeriods = self.offsetPeriods_JTF.getValueInt()
            # myPrint("B", "@@ AsOfDateChooser:%s:asOfSelected() - getAsOfDateIntFromSelectedOption() reports: '%s'" %(self.getName(), asofDateInt))
            self.ignoreDateChanges = True
            self.asOfDate_JDF.setDateInt(asofDateInt)
            self.offsetPeriods_JTF.setValueInt(offsetPeriods)
            self.ignoreDateChanges = False
            self.setAsOfDateResult(asofDateInt, offsetPeriods)
            self.updateEnabledStatus()

        def loadFromParameters(self, settings, defaultKey):
            # type: ([bool, str, int, int], str) -> bool

            # todo - the original 'setOption(defaultKey)' was recently moved to only run when the settings don't contain this date config key...
            if not self.setSelectedOptionKey(defaultKey): raise Exception("ERROR: Default asof option/key ('%s') not found?!" %(defaultKey))

            foundSetting = False
            # asOfOptionSelected = settings[AsOfDateChooser.ASOF_DRC_ENABLED_IDX]
            asOfOptionKey = settings[AsOfDateChooser.ASOF_DRC_KEY_IDX]
            asOfDateInt = settings[AsOfDateChooser.ASOF_DRC_DATEINT_IDX]
            offsetPeriods = settings[AsOfDateChooser.ASOF_DRC_OFFSETPERIODS_IDX]
            self.offsetPeriods_JTF.setValueInt(offsetPeriods)
            if asOfOptionKey == self.KEY_CUSTOM_ASOF:
                if AsOfDateChooser.isValidAsOfDate(asOfDateInt):
                    self.setAsOfDateInt(asOfDateInt)
                    foundSetting = True
            else:
                foundSetting = self.setSelectedOptionKey(asOfOptionKey)
            if not foundSetting:
                myPrint("B", "@@ %s::loadFromParameters() - asof date settings ('%s') not found / invalid?! Loaded default ('%s')"
                        %(self.getName(), settings, defaultKey))
            else:
                if debug: myPrint("B", "Successfully loaded asof date settings ('%s')" %(settings))
            return foundSetting

        def returnStoredParameters(self, defaultSettings):
            # type: ([bool, str, int, int]) -> [bool, str, int, int]
            settings = copy.deepcopy(defaultSettings)
            asOfDateInt = self.getAsOfDateInt()
            selectedOptionKey = self.getSelectedOptionKey(self.getSelectedIndex())
            offsetPeriods = self.offsetPeriods_JTF.getValueInt()
            # leave settings[AsOfDateChooser.ASOF_DRC_ENABLED_IDX] untouched
            settings[AsOfDateChooser.ASOF_DRC_KEY_IDX] = selectedOptionKey
            settings[AsOfDateChooser.ASOF_DRC_DATEINT_IDX] = asOfDateInt if (selectedOptionKey == self.KEY_CUSTOM_ASOF) else 0
            settings[AsOfDateChooser.ASOF_DRC_OFFSETPERIODS_IDX] = offsetPeriods
            if debug: myPrint("B", "%s::returnStoredParameters() - Returning stored asof date parameters settings ('%s')" %(self.getName(), settings))
            return settings

        @staticmethod
        def isValidAsOfDate(_dateInt):
            # type: (int) -> bool
            if not isinstance(_dateInt, (int, Integer)):    return False
            if _dateInt < AsOfDateChooser.ASOF_DATE_VALID:  return False
            return True

        def setAsOfDateResult(self, asOfDateInt, offsetPeriods):
            oldAsOfDateInt = self.asOfDateIntResult
            oldSelectedKey = self.selectedOptionKeyResult
            oldOffsetPeriods = self.offsetPeriodsResult
            selectedOptionKey = self.getSelectedOptionKey(self.getSelectedIndex())
            # myPrint("B", "@@ AsOfDateChooser:%s:setAsOfDateResult(%s) (old asof date: %s), selectedKey: '%s' (old key: '%s')" %(self.getName(), asOfDateInt, oldAsOfDateInt, selectedOptionKey, oldSelectedKey));
            if asOfDateInt != oldAsOfDateInt or selectedOptionKey != oldSelectedKey or offsetPeriods != oldOffsetPeriods:
                self.asOfDateIntResult = asOfDateInt
                self.selectedOptionKeyResult = selectedOptionKey
                self.offsetPeriodsResult = offsetPeriods
                if asOfDateInt != oldAsOfDateInt:
                    # if debug:
                    #     myPrint("B", "@@ AsOfDateChooser:%s:setAsOfDateResult(%s).firePropertyChange(%s) >> asof date changed (from: %s to %s) <<" %(self.getName(), asOfDateInt, self.PROP_ASOF_CHANGED, oldAsOfDateInt, asOfDateInt))
                    self.eventNotify.firePropertyChange(self.PROP_ASOF_CHANGED, oldAsOfDateInt, asOfDateInt)
                elif selectedOptionKey != oldSelectedKey:
                    # if debug:
                    #     myPrint("B", "@@ AsOfDateChooser:%s:setAsOfDateResult(%s).firePropertyChange(%s) >> selected key changed (from: '%s' to '%s') <<" %(self.getName(), asOfDateInt, self.PROP_ASOF_CHANGED, oldSelectedKey, selectedOptionKey))
                    self.eventNotify.firePropertyChange(self.PROP_ASOF_CHANGED, oldSelectedKey, selectedOptionKey)
                elif offsetPeriods != oldOffsetPeriods:
                    # if debug:
                    #     myPrint("B", "@@ AsOfDateChooser:%s:setAsOfDateResult(%s).firePropertyChange(%s) >> selected key changed (from: '%s' to '%s') <<" %(self.getName(), asOfDateInt, self.PROP_ASOF_CHANGED, oldOffsetPeriods, offsetPeriods))
                    self.eventNotify.firePropertyChange(self.PROP_ASOF_CHANGED, oldOffsetPeriods, offsetPeriods)

        def setEnabled(self, isEnabled, shouldHide=False):
            self.isEnabled = isEnabled
            self.updateEnabledStatus(shouldHide=shouldHide)

        def updateEnabledStatus(self, shouldHide=False):
            for comp in self.getAllSwingComponents():
                comp.setEnabled(self.isEnabled)
                if shouldHide: comp.setVisible(self.isEnabled)

        def itemStateChanged(self, evt):
            src = evt.getItemSelectable()                                                                               # type: JComboBox
            paramString = evt.paramString()
            state = evt.getStateChange()
            changedItem = evt.getItem()                                                                                 # type: AsOfDateChooser.AsOfDateChoice

            myClazzName = "AsOfDateChooser"
            propKey = self.PROP_ASOF_CHANGED
            onSelectionMethod = self.asOfSelected

            defaultLast = "<unknown>"
            if self.lastDeselectedOptionKey is None: self.lastDeselectedOptionKey = defaultLast

            if src is self.getChoiceCombo():

                if state == ItemEvent.DESELECTED:
                    oldDeselected = self.lastDeselectedOptionKey
                    newDeselected = changedItem.getKey()
                    self.lastDeselectedOptionKey = newDeselected
                    if debug:
                        myPrint("B", "@@ %s:%s:itemStateChanged(%s).firePropertyChange(%s) >> last deselected changed (from: '%s' to '%s') (paramString: '%s') <<"
                                %(myClazzName, self.getName(), state, propKey, oldDeselected, newDeselected, paramString))

                elif state == ItemEvent.SELECTED:
                    lastDeselected = self.lastDeselectedOptionKey
                    newSelected = changedItem.getKey()
                    if debug:
                        myPrint("B", "@@ %s:%s:itemStateChanged(%s).firePropertyChange(%s) >> selection changed (from: '%s' to '%s') (paramString: '%s') <<"
                                %(myClazzName, self.getName(), state, propKey, lastDeselected, newSelected, paramString))
                    self.eventNotify.firePropertyChange(propKey,  lastDeselected, newSelected)
                    onSelectionMethod()
                    self.lastDeselectedOptionKey = None

        def propertyChange(self, event):
            # myPrint("B", "@@ AsOfDateChooser:%s:propertyChange('%s') - .getSelectedOptionKey() reports: '%s'" %(self.getName(), event.getPropertyName(), self.getSelectedOptionKey(self.getSelectedIndex())));
            if (event.getPropertyName() == JDateField.PROP_DATE_CHANGED and not self.ignoreDateChanges):
                selectedOptionKey = self.getSelectedOptionKey(self.getSelectedIndex())
                if (selectedOptionKey != self.KEY_CUSTOM_ASOF and self.asOfVariesFromSelectedOption()):
                    self.getChoiceCombo().setSelectedItem(self.customOption)
                if (selectedOptionKey == self.KEY_CUSTOM_ASOF):
                    self.setAsOfDateResult(self.asOfDate_JDF.getDateInt(), self.offsetPeriods_JTF.getValueInt())
            if (event.getPropertyName() == MyJTextFieldAsInt.PROP_OFFSET_PERIODS_CHANGED and not self.ignoreDateChanges):
                self.setAsOfDateResult(self.asOfDate_JDF.getDateInt(), self.offsetPeriods_JTF.getValueInt())
                self.asOfSelected()

        def asOfVariesFromSelectedOption(self):
            asOfDateInt = self.asOfDate_JDF.getDateInt()
            selectedAsOfDateInt = self.getAsOfDateIntFromSelectedOption()
            return asOfDateInt != selectedAsOfDateInt

        def getAsOfDateIntFromSelectedOption(self):
            selectedOptionKey = self.getSelectedOptionKey(self.getSelectedIndex())
            if (selectedOptionKey == self.KEY_CUSTOM_ASOF):
                return self.asOfDate_JDF.parseDateInt()
            return self.AsOfDateChoice.getAsOfDateFromKey(selectedOptionKey, self.getOffsetPeriods())

        def toString(self):  return self.__str__()
        def __repr__(self):  return self.__str__()
        def __str__(self):
            return "AsOfDateChooser::%s - key: '%s' asofDate: %s, offset: %s" %(self.getName(), self.getSelectedOptionKey(self.getSelectedIndex()), self.getAsOfDateField().getDateInt(), self.getOffsetPeriodsField().getValueInt())

    ####################################################################################################################
    # Copied from: com.infinitekind.moneydance.model.CostCalculation (quite inaccessible before build 5008, also buggy)
    ####################################################################################################################
    class MyCostCalculation:
        """CostBasis calculation engine (v10). Copies/enhances/fixes MD CostCalculation() (asof build 5064).
        Params asof:None or zero = asof the most recent (future)txn date that affected the shareholding/costbasis balance.
        preparedTxns is typically used by itself to recall the class to get the current cost basis
        obtainCurrentBalanceToo is used to request that the class calls itself to also get the current/today balance too
        # (v2: LOT control fixes, v3: added isCostBasisValid(), v4: don't incl. fees on misc inc/exp in cbasis with lots,
        # ...fixes for  capital gains to work, v5: added in short/long term support, v6: added unRealizedSaleTxn parameter
        support, v7: added SharesOwnedAsOf class to match MD's upgraded CostCalculation class), v8: fixed code to match
        MD2024(5119) - fixed endless loop, buy 60, split 7:1, sell 20, split 4:1, sell all for zero cost basis scenarios;
        v10: MD2026(5500) applied latest fixes"""

        ################################################################################################################
        # This is used to calculate the cost of a security using either the average cost or lot-based method.
        # This can be used to produce the cost and gains (both short and long-term) for the security or for individual
        # transactions on the security.
        #
        # Follows U.S. IRS 'single-category' average cost method specification. Gains are split short/long-term using FIFO.
        # From U.S. IRS Publication 564 for 2009, under Average Basis, for the 'single-category' method:
        #           "Even though you include all unsold shares of a fund in a single category to compute average
        #           basis, you may have both short-term and long-term gains or losses when you sell these shares.
        #           To determine your holding period, the shares disposed of are considered to be those acquired first."
        #           https://www.irs.gov/pub/irs-prior/p564--2009.pdf
        #
        # There was a 'double-category' method which allowed you to separate short-term and long-term average cost pools,
        # but the IRS eliminated that method on April 1, 2011. NOTE: Custom Balances does compute the available shares
        # in both short-term and long-term pools. However this data is only shown in console when COST_DEBUG is enabled).
        ################################################################################################################

        COST_DEBUG = False

        def __init__(self, secAccount, asOfDate=None, preparedTxns=None, obtainCurrentBalanceToo=False, unRealizedSaleTxn=None):
            # type: (Account, int, TxnSet, bool, SplitTxn) -> None

            if self.COST_DEBUG: myPrint("B", "** MyCostCalculation() initialising..... running asof: %s, for account: '%s' (%s) **"%(asOfDate, secAccount, "AvgCost" if secAccount.getUsesAverageCost() else "LotControl"))

            # prevent callers attempting to request impossible / illogical combinations of parameters
            # if the caller has prepared the txns, then they must also prepare any unRealizedSaleTxn too if they need it etc...
            # when calling obtainCurrentBalanceToo then cannot use preparedTxns or unRealizedSaleTxn
            if preparedTxns is not None and unRealizedSaleTxn is not None: raise Exception("Cannot supply both preparedTxns and unRealizedSaleTxn")
            if obtainCurrentBalanceToo and (preparedTxns is not None or unRealizedSaleTxn is not None): raise Exception("Cannot obtainCurrentBalanceToo when using preparedTxns / unRealizedSaleTxn")

            if unRealizedSaleTxn is not None:
                assert (isinstance(unRealizedSaleTxn, SplitTxn))
                if self.COST_DEBUG: myPrint("B", "... unrealized (sale txn) gain calculation requested for:", unRealizedSaleTxn)

            if preparedTxns is not None:
                if self.COST_DEBUG: myPrint("B", "... preparedTxns parameter specified (containing: %s txns)" %(preparedTxns.getSize()))

            todayInt = DateUtil.getStrippedDateInt()
            if (asOfDate is None or asOfDate < 19000000): asOfDate = None
            self.asOfDate = asOfDate
            self.unRealizedSaleTxn = unRealizedSaleTxn

            self.positions = ArrayList()            # Use java Class to exactly mirror original code (rather than [list])
            self.positionsByBuyID = HashMap()       # Use java Class to exactly mirror original code (rather than {dict})
            self.longTermCutoffDate = DateUtil.incrementDate(DateUtil.getStrippedDateInt(), -1, 0, 0)
            self.secAccount = secAccount
            self.investCurr = secAccount.getParentAccount().getCurrencyType()                                           # type: CurrencyType
            self.secCurr = secAccount.getCurrencyType()                                                                 # type: CurrencyType
            self.usesAverageCost = secAccount.getUsesAverageCost()

            # now detect invalid cost basis. Use preparedTxns if supplied, otherwise pass null which will analise all transactions...
            # perform this check before sorting, and before we add any (optional) unRealizedSaleTxn
            self._unmatchedSellTxns = MyCostCalculation.getInvalidLotMatchSellTxns(secAccount, preparedTxns, False, self.COST_DEBUG)
            if self.isCostBasisInvalid():
                myPrint("B", "@@ WARNING: INVALID Cost Basis for lot controlled security account: '%s' (%s sells not fully / properly lot matched to buys) >> - cost basis defaulting to ZERO"
                        %(self.getSecAccount().getFullAccountName(), len(self.getUnmatchedSellTxns())))
                invalidStr = "[%s]" % ", ".join("%s, %s, %s, %s" %(
                            it.getUUID(), it.getParentTxn().getInvestTxnType(),
                            it.getDateInt(), it.getSplitAmount()) for it in self.getUnmatchedSellTxns())
                myPrint("B", "... invalid cost basis txns: %s" %(invalidStr))

            self.txns = preparedTxns if (isinstance(preparedTxns, TxnSet))\
                else secAccount.getBook().getTransactionSet().getTransactionsForAccount(secAccount)

            self.txns.sortWithComparator(TxnUtil.DATE_THEN_AMOUNT_COMPARATOR.reversed())        # Most recent date first by index
            if unRealizedSaleTxn is not None: self.txns.insertTxnAt(unRealizedSaleTxn, 0)       # Always insert as first/most recent txn

            self.asOfDate = self.deriveRealBalanceDateInt()
            self._isAsOfToday = (self.asOfDate == todayInt)

            self.getPositions().add(MyCostCalculation.Position(self))               # Adds a dummy start Position

            for secTxn in self.getTxns():
                self.addTxn(secTxn)                                                 # Iterates in reverse = oldest first

            if self.getUsesAverageCost():
                self.allocateAverageCostSales()
            else:
                self.allocateLots()
                self.updateCostBasisForLots()

            if obtainCurrentBalanceToo:
                if self.getAsOfDate() > todayInt:
                    self.currentBalanceCostCalculation = MyCostCalculation(self.getSecAccount(), todayInt, self.getTxns(), False)
                else:
                    self.currentBalanceCostCalculation = self                                                           # type: MyCostCalculation
            else:
                self.currentBalanceCostCalculation = None                                                               # type: MyCostCalculation

        def isAsOfToday(self): return self._isAsOfToday

        def getCostBasisAsOfAsOf(self): return 0L if (self.isCostBasisInvalid()) else self.getMostRecentPosition().getRunningCost()

        def getLongTermCutoffDate(self): return self.longTermCutoffDate
        def getInvestCurr(self): return self.investCurr
        def getSecCurr(self): return self.secCurr

        def getUnRealizedSaleTxn(self): return self.unRealizedSaleTxn

        def getUnmatchedSellTxns(self):
            if (self._unmatchedSellTxns is None or len(self._unmatchedSellTxns) <1): return None
            return self._unmatchedSellTxns

        def isUnmatchedSellTxn(self, sellTxn): return (self.getUnmatchedSellTxns() is not None and sellTxn in self.getUnmatchedSellTxns())

        def deriveTxnDateRange(self, onlyCostImpactingTxns=True):
            if (self.getTxns().getSize() == 0): return None     # there can't be a date range with no transactions
            endDate = self.getAsOfDate()                        # the end / balance date was already pre-determined by `deriveRealBalanceDateInt` (!! should never happen)
            fields = InvestFields()
            for txn in self.getTxns():                          # TxnSet - iterates in reverse = oldest first
                fields.setFieldStatus(txn.getParentTxn())
                if (onlyCostImpactingTxns and not self.isCostBasisImpactingTxnType(fields.txnType)):
                    continue                                    # if we only wanted cost-impacting txns, then skip this one.. move on to next...
                startDate = txn.getDateInt()
                if (startDate > endDate): break
                return DateRange(Integer(startDate), Integer(endDate))    # Integer() wrappers needed in Jython to resolve overload ambiguity
            return None

        def isCostBasisImpactingTxnType(self, txnType):
            # type: (InvestTxnType) -> bool
            return txnType in [InvestTxnType.BUY, InvestTxnType.BUY_XFER, InvestTxnType.COVER, InvestTxnType.DIVIDEND_REINVEST,
                               InvestTxnType.SELL, InvestTxnType.SELL_XFER, InvestTxnType.SHORT, InvestTxnType.MISCINC,
                               InvestTxnType.MISCEXP]

        def isCostBasisInvalid(self): return (self._unmatchedSellTxns is not None and len(self._unmatchedSellTxns) > 0)
        def getUsesAverageCost(self): return self.usesAverageCost

        def getCurrentBalanceCostCalculation(self):
            # type: () -> MyCostCalculation
            return self.currentBalanceCostCalculation

        def getTxns(self): return self.txns

        def getSecAccount(self): return self.secAccount

        def getAsOfDate(self): return self.asOfDate

        def deriveRealBalanceDateInt(self):
            """When asof is None, you are requesting the Balance.. This determines the future date of that Balance"""
            if self.getAsOfDate() is not None: return self.getAsOfDate()        # If you specify a date, then just use that...
            todayInt = DateUtil.getStrippedDateInt()
            mostRecentDateInt = todayInt
            fields = InvestFields()                                                                                     # type: InvestFields
            txns = self.getTxns()
            for i in range(0, txns.getSize()):                                  # Iterate by index = newest first
                txn = txns.getTxnAt(i)
                dateInt = txn.getDateInt()
                if dateInt <= todayInt: break

                fields.setFieldStatus(txn.getParentTxn())

                # ie not [InvestTxnType.BANK, InvestTxnType.DIVIDEND, InvestTxnType.DIVIDENDXFR]
                if not self.isCostBasisImpactingTxnType(fields.txnType): continue  # Skip back in time....
                mostRecentDateInt = dateInt
                break

            if self.COST_DEBUG: myPrint("B", "@@ deriveRealBalanceDateInt().. sec: '%s' requested asof: %s, derived asof: %s"
                                             %(self.getSecAccount(), self.getAsOfDate(), mostRecentDateInt))
            return mostRecentDateInt

        def getPositions(self):
            # type: () -> [MyCostCalculation.Position]
            return self.positions

        def getPositionsByBuyID(self):
            # type: () -> {String: MyCostCalculation.Position}
            return self.positionsByBuyID

        # DEPRECATED: Please use getMostRecentPosition()
        def getCurrentPosition(self):
            # type: () -> MyCostCalculation.Position
            return self.getMostRecentPosition()

        def getMostRecentPosition(self):
            # type: () -> MyCostCalculation.Position
            """Returns the most recent Position. NOTE: This could in theory be future!"""
            return self.getPositions().get(self.getPositions().size() - 1)      # NOTE: There is always a dummy first position

        def getPositionForAsOf(self):
            # type: () -> MyCostCalculation.Position
            """Returns the most recent Position upto/asof requested"""
            rtnPos = self.getPositions().get(0)
            for pos in reversed(self.getPositions()):                           # Reversed puts most recent first
                if pos.getDate() > self.asOfDate: continue                      # Skip future posns
                rtnPos = pos
                if pos.getDate() <= self.asOfDate: break                        # Capture the most recent posn we find before/on asof
            return rtnPos

        def getSharesAndCostBasisForAsOf(self):
            # type: () -> (int, int)
            """Returns a tuple containing the (long) shares owned, (long) cost basis upto/asof the date requested"""
            if self.getAsOfDate() is None: return None
            asofPos = self.getPositionForAsOf()
            costBasisAsOf = 0L if self.isCostBasisInvalid() else asofPos.getRunningCost()
            return MyCostCalculation.SharesOwnedAsOf(self.getSecAccount(), self.getAsOfDate(), asofPos.getSharesOwnedAsOfAsOf(), costBasisAsOf, not self.isCostBasisInvalid())

        def addTxn(self, txn):
            # type: (AbstractTxn) -> None
            if isinstance(txn, SplitTxn) and txn.getDateInt() <= self.getAsOfDate():
                previousPos = self.getMostRecentPosition()
                newPos = MyCostCalculation.Position(self, txn, previousPos)
                # if self.COST_DEBUG: myPrint("B", "adding position to end of position table:", newPos)
                self.getPositions().add(newPos)
                # ptxn = txn.getParentTxn()                                                                             # type: ParentTxn
                self.getPositionsByBuyID().put(txn.getUUID(), newPos)  # MD Version used ptxn.getUUID()

        def allocateAverageCostSales(self):
            #type: () -> None

            buyIdx = 0
            sellIdx = 0
            numPositions = self.getPositions().size()

            # Step through sell transactions and allocate earlier buys to the sell in FIFO order.
            # This FIFO matching is used only to determine each share’s holding period (short-term vs long-term) under the U.S. IRS single-category average cost method.
            while (sellIdx < numPositions and buyIdx < numPositions):

                if (buyIdx > sellIdx):
                    myPrint("B", "Info: buy transactions overran sells; going short")

                sell = self.getPositions().get(sellIdx)                                                                 # type: MyCostCalculation.Position

                if (sell.getSharesAdded() >= 0):
                    sellIdx += 1
                    continue

                if (sell.getUnallottedSharesAdded() >= 0):
                    sellIdx += 1
                    continue

                # scan for buys while there are shares to allot in this sale
                while (buyIdx < numPositions and sell.getUnallottedSharesAdded() < 0):
                    buy = self.getPositions().get(buyIdx)                                                               # type: MyCostCalculation.Position

                    if (buy.getSharesAdded() < 0):
                        buyIdx += 1
                        continue

                    # allocate as many shares as possible from this buy transaction
                    # but first, un-apply any splits so that we're talking about the same number shares
                    unallottedSellShares = self.secCurr.unadjustValueForSplitsInt(buy.getDate(), -sell.getUnallottedSharesAdded(), sell.getDate())
                    sharesFromBuy = Math.min(unallottedSellShares, buy.getUnallottedSharesAdded())

                    allSellSharesConsumed = (unallottedSellShares <= buy.getUnallottedSharesAdded())  # was the whole sell consumed?
                    if (allSellSharesConsumed):
                        # MD2024(5118) fix to catch the 'Apple' buy 60, split 7:1, sell 20, split 4:1 issue... Can leave small amount stranded after unadjustValueForSplitsInt() then adjustValueForSplitsInt()
                        sharesFromBuyAdjusted = -sell.getUnallottedSharesAdded()   # don't allow rounding/truncation prevent the whole sell from being consumed
                    else:
                        # use the sell shares actually matched to the buy, converted back to the date of the sell
                        sharesFromBuyAdjusted = self.secCurr.adjustValueForSplitsInt(buy.getDate(), sharesFromBuy, sell.getDate())

                    if self.COST_DEBUG:
                        if (allSellSharesConsumed):  # SCB: MD2024(5118) fix (for avg cost, buy 60, split 7:1, sell 20, split 4:1 issue)
                            origConsumedCalc = self.secCurr.adjustValueForSplitsInt(buy.getDate(), sharesFromBuy, sell.getDate())
                            consumedStr = "<consumed values match ok>" if (sharesFromBuyAdjusted == origConsumedCalc) else "(would have been: %s)" %(origConsumedCalc)
                            myPrint("B", "** All this sell's shares consumed on this buy. Consumed: %s... reflecting sell: %s %s - (buyIdx: %s, sellIdx: %s)" %(sharesFromBuy, sharesFromBuyAdjusted, consumedStr, buyIdx, sellIdx))
                        else:
                            myPrint("B", "** Not enough buy shares for this sell... Consumed on buy: %s... reflecting sell: %s (buyIdx: %s, sellIdx: %s)" %(sharesFromBuy, sharesFromBuyAdjusted, buyIdx, sellIdx))

                    # ensure sharesFromBuyAdjusted never go to zero (for example, from adjusting a small amount from a split),
                    # because then no more allocations are made
                    if (sharesFromBuyAdjusted == 0 and sharesFromBuy != 0):
                        sharesFromBuyAdjusted = (-1 if (sharesFromBuy < 0) else 1)

                    if (sharesFromBuy != 0):
                        matchedBuyCostBasis = Math.round(buy.getCostBasis() * (float(sharesFromBuy) / float(buy.getSharesAdded())))
                        sell.setUnallottedSharesAdded(sell.getUnallottedSharesAdded() + sharesFromBuyAdjusted)
                        buy.setUnallottedSharesAdded(buy.getUnallottedSharesAdded() - sharesFromBuy)
                        sell.getBuyAllocations().add(MyCostCalculation.Allocation(self, sharesFromBuyAdjusted, sharesFromBuy, matchedBuyCostBasis, buy))
                        buy.getSellAllocations().add(MyCostCalculation.Allocation(self, sharesFromBuy, sharesFromBuyAdjusted, matchedBuyCostBasis, sell))
                        if self.COST_DEBUG: myPrint("B", ".... . matchedBuyCostBasis: %s" %(self.investCurr.getDoubleValue(matchedBuyCostBasis)))

                    if (buy.getUnallottedSharesAdded() == 0):
                        buyIdx += 1
                        continue  # SCB: MD2024(5118) fix (for avg cost, buy 60, split 7:1, sell 20, split 4:1 issue)

                    # if we are here then... in theory... we are on the same sell, and it has fully consumed enough buys..
                    # repeat the inner-while condition and trap endless loops which should never occur!
                    if (sell.getUnallottedSharesAdded() < 0):  # SCB: MD2024(5118) fix (for avg cost, buy 60, split 7:1, sell 20, split 4:1 issue)
                        buyIdx = numPositions + 1
                        sellIdx = numPositions + 1
                        raise Exception("LOGIC ERROR: end of while loop, but sell.unallottedSharesAdded (%s) < 0L - breaking out of loop... Cost Basis will be wrong!" % (sell.getUnallottedSharesAdded()))

                    # inner-while.. On a sell, consuming buys....
                # outer-while..  #changed - removed 'end' and trailing dots to match kotlin

            if self.COST_DEBUG:
                myPrint("B", "-------------------------\npositions and allotments for '%s' (Avg Cost Basis: %s):" %(self.getSecAccount(), self.getUsesAverageCost()))
                for pos in self.getPositions(): myPrint("B", "  ", pos)
                myPrint("B", "-------------------------")

        def allocateLots(self):
            #type: () -> None

            # analyse the sell transactions...
            for sellPosition in [position for position in self.getPositions() if (position.getSharesAdded() < 0)]:

                sellTxn = sellPosition.getTxn()
                if sellTxn is None: continue

                if self.COST_DEBUG: myPrint("B", ">> SELL: date: %s sellPos:" %(sellPosition.getDate()), sellPosition)

                lotMatchedBuyTable = TxnUtil.parseCostBasisTag(sellTxn if isinstance(sellTxn, SplitTxn) else None)                                                 # type: {String: Long}
                if self.COST_DEBUG: myPrint("B", ".. sell date: %s, txn's (lot matching) lotMatchedBuyTable: %s" %(sellPosition.getDate(), lotMatchedBuyTable))

                # parse the "cost_basis" parameter and obtain a table of buy txns matched to this sell txn.
                if lotMatchedBuyTable is not None:
                    # iterate each matched buy txn...
                    for lotMatchedBuyID in lotMatchedBuyTable.keySet():
                        # find the matched buy's position
                        lotMatchedBoughtPos = self.getPositionsByBuyID().get(lotMatchedBuyID)                           # type: MyCostCalculation.Position
                        if self.COST_DEBUG: myPrint("B", "      txn lotMatchedBuyID: %s, (lot matched) lotMatchedBoughtPos: %s" %(lotMatchedBuyID, lotMatchedBoughtPos))
                        if (lotMatchedBoughtPos is not None):
                            lotMatchedBoughtShares = lotMatchedBuyTable.get(lotMatchedBuyID)

                            # found the matched buy position.. unadjust the matched sell qty back from the sell's date to the buy's date
                            lotMatchedBoughtSharesAdjusted = self.secCurr.unadjustValueForSplitsInt(lotMatchedBoughtPos.getDate(), lotMatchedBoughtShares, sellPosition.getDate())

                            if self.COST_DEBUG: myPrint("B", ".... lotMatchedBoughtPos.getDate(): %s, lotMatchedBoughtShares: %s, sellPosition.getDate(): %s, lotMatchedBoughtSharesAdjusted: %s"
                                                        %(lotMatchedBoughtPos.getDate(), self.secCurr.getDoubleValue(lotMatchedBoughtShares), sellPosition.getDate(), self.secCurr.getDoubleValue(lotMatchedBoughtSharesAdjusted)))
                            if self.COST_DEBUG: myPrint("B", ".... (lot matched) lotMatchedBoughtShares: %s, (lot matched) lotMatchedBoughtSharesAdjusted: %s"
                                                        %(self.secCurr.getDoubleValue(lotMatchedBoughtShares), self.secCurr.getDoubleValue(lotMatchedBoughtSharesAdjusted)))

                            matchedBuyCostBasis = Math.round(lotMatchedBoughtPos.getCostBasis() * (float(lotMatchedBoughtSharesAdjusted) / float(lotMatchedBoughtPos.getSharesAdded())))

                            sellPosition.getBuyAllocations().add(MyCostCalculation.Allocation(self, lotMatchedBoughtSharesAdjusted, lotMatchedBoughtShares, matchedBuyCostBasis, lotMatchedBoughtPos))
                            if self.COST_DEBUG: myPrint("B", ".... 0. matchedBuyCostBasis: %s" %(self.investCurr.getDoubleValue(matchedBuyCostBasis)))

                            if self.COST_DEBUG: myPrint("B", ".... 1. PRE  - sellPosition.getUnallottedSharesAdded: %s, lotMatchedBoughtShares: %s"
                                                        %(self.secCurr.getDoubleValue(sellPosition.getUnallottedSharesAdded()), self.secCurr.getDoubleValue(lotMatchedBoughtShares)))

                            sellPosition.setUnallottedSharesAdded(sellPosition.getUnallottedSharesAdded() + lotMatchedBoughtShares)

                            if self.COST_DEBUG: myPrint("B", ".... 2. POST - sellPosition.getUnallottedSharesAdded: %s" %(self.secCurr.getDoubleValue(sellPosition.getUnallottedSharesAdded())))

                            lotMatchedBoughtPos.getSellAllocations().add(MyCostCalculation.Allocation(self, lotMatchedBoughtShares, lotMatchedBoughtSharesAdjusted, matchedBuyCostBasis, sellPosition))

                            if self.COST_DEBUG: myPrint("B", ".... 3. PRE  - lotMatchedBoughtPos.getUnallottedSharesAdded: %s, lotMatchedBoughtSharesAdjusted: %s"
                                                        %(self.secCurr.getDoubleValue(lotMatchedBoughtPos.getUnallottedSharesAdded()), self.secCurr.getDoubleValue(lotMatchedBoughtSharesAdjusted)))
                            lotMatchedBoughtPos.setUnallottedSharesAdded(lotMatchedBoughtPos.getUnallottedSharesAdded() - lotMatchedBoughtSharesAdjusted)
                            if self.COST_DEBUG: myPrint("B", ".... 4. POST - lotMatchedBoughtPos.getUnallottedSharesAdded: %s"
                                                        %(self.secCurr.getDoubleValue(lotMatchedBoughtPos.getUnallottedSharesAdded())))

                        else:
                            myPrint("B", ">> Warning: Could NOT find: lotMatchedBuyID: '%s' in getPositionsByBuyID() for sellPosition: %s" %(lotMatchedBuyID, sellPosition))

            if self.COST_DEBUG:
                myPrint("B", "-------------------------\npositions and allotments for '%s':" %(self.getSecAccount()))
                for pos in self.getPositions(): myPrint("B", "  ", pos)
                myPrint("B", "-------------------------")

        def updateCostBasisForLots(self):
            sharedOwned = 0
            runningCostBasis = 0

            for pos in self.getPositions():

                if self.COST_DEBUG:
                    myPrint("B", "--------------------------")
                    myPrint("B", "... on pos:", pos)

                sharedOwned += self.secCurr.adjustValueForSplitsInt(pos.getDate(), pos.getSharesAdded(), self.getAsOfDate())
                assert sharedOwned == pos.getSharesOwnedAsOfAsOf(), ("ERROR: failed sharedOwned(%s) == pos.getSharesOwnedAsOfAsOf()(%s)" %(sharedOwned, pos.getSharesOwnedAsOfAsOf()))

                if pos.isSellTxn():
                    if self.COST_DEBUG: myPrint("B", "...... isSell!")
                    totMatchedBuyCostBasis = 0
                    for buyAllocation in pos.getBuyAllocations():
                        if self.COST_DEBUG: myPrint("B", "...... buyAllocation:", buyAllocation)
                        buyMatchedPos = buyAllocation.getAllocatedPosition()                                            # type: MyCostCalculation.Position
                        if self.COST_DEBUG: myPrint("B", "...... buyMatchedPos:", buyMatchedPos)
                        buyCostBasis = buyMatchedPos.getCostBasis()
                        buyShares = buyMatchedPos.getSharesAdded()
                        buyCostBasisPrice = 0.0 if (buyShares == 0) else self.investCurr.getDoubleValue(buyCostBasis) / self.secCurr.getDoubleValue(buyShares)
                        if self.COST_DEBUG: myPrint("B", "...... %s * %s" %(buyCostBasisPrice,  self.secCurr.getDoubleValue(buyAllocation.getSharesAllocated())))
                        buyMatchedCostBasis = self.investCurr.getLongValue(buyCostBasisPrice * self.secCurr.getDoubleValue(buyAllocation.getSharesAllocated()))
                        if self.COST_DEBUG: myPrint("B", "......... matched buy CB: %s" %(self.investCurr.getDoubleValue(buyMatchedCostBasis)))
                        totMatchedBuyCostBasis += buyMatchedCostBasis
                    pos.setCostBasis(-totMatchedBuyCostBasis)
                    if self.COST_DEBUG: myPrint("B", "...... setting sellPos CostBasis to: %s" %(self.investCurr.getDoubleValue(pos.getCostBasis())))

                if not pos.isMiscIncExpTxn():   # Assume that for LOT controlled, we do not add misc inc/exp fee into costbasis (as the cb cannot be assigned to any lot!)
                    runningCostBasis += pos.getCostBasis()

                pos.setRunningCost(runningCostBasis)
                if self.COST_DEBUG: myPrint("B", "... setting Pos runningCost to: %s" %(self.investCurr.getDoubleValue(pos.getRunningCost())))

        def getBasisPrice(self, asOfTxn):
            # type: (AbstractTxn) -> float
            """Returns the cost (per share) of the shares held as of the given transaction, or as of the last transaction if the given transaction is null.
            Note: For LOT controlled security accounts, if the cost basis is invalid then zero will be returned"""

            if self.isCostBasisInvalid(): return 0.0
            if asOfTxn is not None:
                for pos in self.getPositions():                                                                         # type: MyCostCalculation.Position
                    if pos.getTxn() is None: continue
                    if pos.getTxn() == asOfTxn: return pos.getBasisPrice()
                myPrint("B", "getBasisPrice: unable to find position for txn :%s; returning cost basis as of last position" %(asOfTxn))
            return self.getMostRecentPosition().getBasisPrice()

        def getTxnPos(self, forTxn):
            for pos in self.getPositions():
                txn = pos.getTxn()
                if (txn is None): continue
                if (txn == forTxn): return pos
            myPrint("B", "getTxnPos: unable to find position for txn %s; returning null" % (forTxn))
            return None

        def getTxnCostBasisImpact(self, forTxn):
            for pos in self.getPositions():
                txn = pos.getTxn()
                if (txn is None): continue
                if (txn != forTxn): continue
                return pos.actualCostBasisImpact()
            myPrint("B", "getTxnCostBasisImpact: unable to find position for txn %s; returning null" % (forTxn))
            return None

        def getListGainsForDateRange(self, dateRange):
            # type: (DateRange) -> [CapitalGainResult]

            if self.COST_DEBUG: myPrint("B", ">> Calculating list of gains for '%s', DR: '%s'" %(self.getSecAccount(), dateRange))

            listGains = ArrayList()
            countInvalidGains = 0

            # Add up all the sales gains manually...
            for pos in self.getPositions():  # iterate oldest to most recent
                if pos.getDate() > self.asOfDate: break
                if pos.getDate() > dateRange.getEndDateInt(): break
                if pos.getDate() < dateRange.getStartDateInt(): continue
                txn = pos.getTxn()

                if not isinstance(txn, SplitTxn): continue
                if not pos.isSellTxn(): continue
                gainInfo = self.calculateGainsForPos(pos)
                if not gainInfo.isValid(): countInvalidGains += 1
                listGains.add(gainInfo)

            if self.COST_DEBUG: myPrint("B", ">>>> returning a list of %s CapitalGainResult(s)%s"
                                        %(listGains.size(), (" - invalid gains count: %s" % (countInvalidGains)) if countInvalidGains > 0 else ""))
            return list(listGains)

        def getSaleGainsForDateRange(self, dateRange, targetCurrency=None, valuationDate=None):
            # type: (DateRange, CurrencyType, int) -> CapitalGainResult

            toCurrency = targetCurrency if targetCurrency is not None else self.investCurr
            localIsTarget = (self.investCurr == toCurrency)

            gidv = self.investCurr.getDoubleValue
            gsdv = self.secCurr.getDoubleValue

            if self.COST_DEBUG: myPrint("B", ">> Calculating gains for '%s', DR: '%s' Investment Currency: '%s' >> toCurrency: '%s' valuationDate: %s (%s)"
                                        %(self.getSecAccount(), dateRange, self.investCurr, toCurrency, valuationDate,
                                          "valued by gain/txn date" if valuationDate is None else "constant currency"))

            totSaleShares = 0
            totSaleSharesShort = 0
            totSaleSharesLong = 0

            # store values in the investment account's currency
            totSaleValue = 0
            totSaleValueShort = 0
            totSaleValueLong = 0
            totSaleBasis = 0
            totSaleBasisShort = 0
            totSaleBasisLong = 0
            totSaleGains = 0
            totSaleGainsShort = 0
            totSaleGainsLong = 0

            # store values in the target currency
            totSaleValueTarget = 0
            totSaleValueShortTarget = 0
            totSaleValueLongTarget = 0
            totSaleBasisTarget = 0
            totSaleBasisShortTarget = 0
            totSaleBasisLongTarget = 0
            totSaleGainsTarget = 0
            totSaleGainsShortTarget = 0
            totSaleGainsLongTarget = 0

            for pos in self.getPositions():                             # Iterate oldest to most recent
                if pos.getDate() > self.asOfDate: break
                if pos.getDate() > dateRange.getEndDateInt(): break
                if pos.getDate() < dateRange.getStartDateInt(): continue
                txn = pos.getTxn()
                if not isinstance(txn, SplitTxn): continue
                if not pos.isSellTxn(): continue
                gainInfo = self.calculateGainsForPos(pos)
                if not gainInfo.isValid(): continue                     # Skip records flagged as invalid

                saleShares = gainInfo.totSaleShares

                if (gainInfo.totSaleSharesShort + gainInfo.totSaleSharesLong) != saleShares:
                    myPrint("B", "getSaleGainsForDateRange - WARNING: '%s' (totSaleSharesShort: %s + totSaleSharesLong: %s) = %s != totSaleShares: %s >> txn date: %s"
                            %(self.getSecAccount(), gainInfo.totSaleSharesShort, gainInfo.totSaleSharesLong,
                              (gainInfo.totSaleSharesShort + gainInfo.totSaleSharesLong), gainInfo.totSaleShares, txn.getDateInt()))

                if saleShares != abs(txn.getValue()):
                    myPrint("B", "getSaleGainsForDateRange - WARNING: '%s' saleShares: %s != txn's sell abs(shares): %s >> txn date: %s"
                            %(self.getSecAccount(), saleShares, abs(txn.getValue()), txn.getDateInt()))

                saleValueGross = txn.getParentAmount()                  # Gross (does not include fee)
                salePriceGross = self.investCurr.getDoubleValue(saleValueGross) / self.secCurr.getDoubleValue(saleShares) if saleShares != 0 else 1.0

                saleValueGrossTarget = CurrencyUtil.convertValue(saleValueGross, self.investCurr, toCurrency, valuationDate if valuationDate is not None else pos.getDate())
                salePriceGrossTarget = toCurrency.getDoubleValue(saleValueGrossTarget) / self.secCurr.getDoubleValue(saleShares) if saleShares != 0 else 1.0

                # NOTE: MD puts the whole sale fee into short-term if there are any short term sales (this code copies that)

                saleBasis = gainInfo.totSaleBasis                     # We put the fee into the calculated cb
                saleGains = (saleValueGross - saleBasis)

                saleBasisTarget = CurrencyUtil.convertValue(saleBasis, self.investCurr, toCurrency, valuationDate if valuationDate is not None else pos.getDate())
                saleGainsTarget = saleValueGrossTarget - saleBasisTarget  # Recalculate to prevent conversion 'drift'

                saleSharesLong = gainInfo.totSaleSharesLong
                saleBasisLong = gainInfo.totSaleBasisLong
                saleBasisLongTarget = CurrencyUtil.convertValue(saleBasisLong, self.investCurr, toCurrency, valuationDate if valuationDate is not None else pos.getDate())

                # LT gains - treated as authoritative
                saleValueLong = CurrencyUtil.convertValue(saleSharesLong, self.secCurr, self.investCurr, salePriceGross)
                saleValueLongTarget = CurrencyUtil.convertValue(saleSharesLong, self.secCurr, toCurrency, salePriceGrossTarget)
                saleGainsLong = saleValueLong - saleBasisLong
                saleGainsLongTarget = saleValueLongTarget - saleBasisLongTarget

                # ST gains
                saleSharesShort = gainInfo.totSaleSharesShort
                saleBasisShort = gainInfo.totSaleBasisShort
                saleBasisShortTarget = CurrencyUtil.convertValue(saleBasisShort, self.investCurr, toCurrency, valuationDate if valuationDate is not None else pos.getDate())
                saleValueShort = CurrencyUtil.convertValue(saleSharesShort, self.secCurr, self.investCurr, salePriceGross)
                saleValueShortTarget = CurrencyUtil.convertValue(saleSharesShort, self.secCurr, toCurrency, salePriceGrossTarget)
                saleGainsShort = saleValueShort - saleBasisShort
                saleGainsShortTarget = saleGainsTarget - saleGainsLongTarget  # Ensures ST/LT total reconciles after conversion

                if self.COST_DEBUG:
                    myPrint("B", "... GAIN INFO:", gainInfo)
                    myPrint("B", "... investCurrency: '%s' : "
                                 "saleShares: %s (short: %s, long: %s), "
                                 "saleValueGross: %s (short: %s, long: %s), "
                                 "saleBasis: %s (short: %s, long: %s), "
                                 "saleGains: %s (short: %s, long: %s)"
                            %(self.investCurr,
                              gsdv(saleShares),     gsdv(saleSharesShort), gsdv(saleSharesLong),
                              gidv(saleValueGross), gidv(saleValueShort),  gidv(saleValueLong),
                              gidv(saleBasis),      gidv(saleBasisShort),  gidv(saleBasisLong),
                              gidv(saleGains),      gidv(saleGainsShort),  gidv(saleGainsLong)))
                    if not localIsTarget:
                        myPrint("B", "... toCurrency: '%s' valuationDate: %s : "
                                     "saleShares: %s (short: %s, long: %s), "
                                     "saleValueGrossTarget: %s (short: %s, long: %s), "
                                     "saleBasisTarget: %s (short: %s, long: %s), "
                                     "saleGainsTarget: %s (short: %s, long: %s)"
                                %(toCurrency, valuationDate,
                                  gsdv(saleShares),                                gsdv(saleSharesShort),                          gsdv(saleSharesLong),
                                  toCurrency.getDoubleValue(saleValueGrossTarget), toCurrency.getDoubleValue(saleValueShortTarget), toCurrency.getDoubleValue(saleValueLongTarget),
                                  toCurrency.getDoubleValue(saleBasisTarget),      toCurrency.getDoubleValue(saleBasisShortTarget), toCurrency.getDoubleValue(saleBasisLongTarget),
                                  toCurrency.getDoubleValue(saleGainsTarget),      toCurrency.getDoubleValue(saleGainsShortTarget), toCurrency.getDoubleValue(saleGainsLongTarget)))

                totSaleShares += saleShares
                totSaleSharesShort += saleSharesShort
                totSaleSharesLong += saleSharesLong
                totSaleValue += saleValueGross
                totSaleValueShort += saleValueShort
                totSaleValueLong += saleValueLong
                totSaleBasis += saleBasis
                totSaleBasisShort += saleBasisShort
                totSaleBasisLong += saleBasisLong
                totSaleGains += saleGains
                totSaleGainsShort += saleGainsShort
                totSaleGainsLong += saleGainsLong

                totSaleValueTarget += saleValueGrossTarget
                totSaleValueShortTarget += saleValueShortTarget
                totSaleValueLongTarget += saleValueLongTarget
                totSaleBasisTarget += saleBasisTarget
                totSaleBasisShortTarget += saleBasisShortTarget
                totSaleBasisLongTarget += saleBasisLongTarget
                totSaleGainsTarget += saleGainsTarget
                totSaleGainsShortTarget += saleGainsShortTarget
                totSaleGainsLongTarget += saleGainsLongTarget

            # no txn as this is grand total of gains for the range...
            result = CapitalGainResult(
                self.getSecAccount(), self.asOfDate, dateRange,
                totSaleShares, totSaleSharesShort, totSaleSharesLong,
                0, 0, 0,
                totSaleValue, totSaleValueShort, totSaleValueLong,
                totSaleBasis, totSaleBasisShort, totSaleBasisLong,
                totSaleGains, totSaleGainsShort, totSaleGainsLong,
                not self.isCostBasisInvalid(), False, True, None,
                "cost_basis_invalid" if self.isCostBasisInvalid() else None)

            resultTarget = CapitalGainResult(
                self.getSecAccount(), self.asOfDate, dateRange,
                totSaleShares, totSaleSharesShort, totSaleSharesLong,
                0, 0, 0,
                totSaleValueTarget, totSaleValueShortTarget, totSaleValueLongTarget,
                totSaleBasisTarget, totSaleBasisShortTarget, totSaleBasisLongTarget,
                totSaleGainsTarget, totSaleGainsShortTarget, totSaleGainsLongTarget,
                not self.isCostBasisInvalid(), False, True, None,
                "cost_basis_invalid" if self.isCostBasisInvalid() else None)

            if self.COST_DEBUG:
                myPrint("B", ">>>> Calculated %sgains for '%s', DR: '%s' Investment Currency: '%s' Result:"
                        %("(INVALID COST BASIS) " if self.isCostBasisInvalid() else "", self.getSecAccount(), dateRange, self.investCurr), result)
                if not localIsTarget:
                    myPrint("B", ">>>> Calculated %sgains for '%s', DR: '%s' >> toCurrency: '%s' valuationDate: %s Result:"
                            %("(INVALID COST BASIS) " if self.isCostBasisInvalid() else "", self.getSecAccount(), dateRange, toCurrency, valuationDate), resultTarget)

            return result if localIsTarget else resultTarget

        def getGainInfo(self, saleTxn):
            # type: (AbstractTxn) -> CapitalGainResult
            """Returns the overall capital gain information specific to the given sell transaction.
               The sell transaction must have the security as its 'account' which means the transaction
               must be the SplitTxn that is assigned to the security account.  If the transaction is
               invalid or null then a zero/error capital gains is returned.
               Returns a CapitalGainResult object with the details of the cost and gains for this transaction"""

            if saleTxn is None:
                myPrint("B", "you must supply a sale txn; returning Invalid/Zeros")
                return CapitalGainResult("sale_txn_not_specified")
            for pos in self.getPositions():                                                                             # type: MyCostCalculation.Position
                if (pos.getTxn() is not None and pos.getTxn() == saleTxn):
                    return self.calculateGainsForPos(pos)
            myPrint("B", "unable to find position for txn :%s; returning Invalid/Zeros" %(saleTxn))
            return CapitalGainResult(saleTxn, "sale_txn_posn_not_found")

        def calculateGainsForPos(self, pos):
            # type: (MyCostCalculation.Position) -> CapitalGainResult

            assert pos.isSellTxn(), "LOGIC ERROR: Can only be called with a sale txn!"

            gidv = self.investCurr.getDoubleValue
            gsdv = self.secCurr.getDoubleValue

            # Note: we are flagging a sell zero shares txn as invalid (it adjusts the cost basis, and is not a gain)
            if pos.getSharesAdded() == 0: return CapitalGainResult(pos.getTxn(), "sell_zero_shares_assume_no_gain")

            isUnmatchedSell = self.isUnmatchedSellTxn(pos.getTxn())

            messageKey = None
            if (pos.getSharesAddedAsOfAsOf() < 0 and pos.getSharesOwnedAsOfAsOf() < 0):
                messageKey = "sell_short"       # Short sale: sold shares we didn't have
                if self.COST_DEBUG: myPrint("B", ".... sell_short (sharesAdded: %s, sharesAddedAsOfAsOf: %s, sharesOwnedAsOfAsOf: %s"
                                            %(gsdv(pos.getSharesAdded()), gsdv(pos.getSharesAddedAsOfAsOf()), gsdv(pos.getSharesOwnedAsOfAsOf())))

            ltDate = self.longTermCutoffDate if (pos.getDate() <= 0) else DateUtil.incrementDate(pos.getDate(), -1, 0, 0)

            # figure out how many of the sold shares were long or short term investments
            longTermSharesSold = -(pos.getSharesAdded())
            shortTermSalesSold = 0

            longTermCostBasis = 0

            for buy in pos.getBuyAllocations():                                                                         # type: MyCostCalculation.Allocation
                if buy.getAllocatedPosition().getDate() >= ltDate:
                    shortTermSalesSold += buy.getSharesAllocated()
                    longTermSharesSold -= buy.getSharesAllocated()
                else:
                    longTermCostBasis += buy.getCostBasisAllocated()

            # go through all transactions and add up all of the shares that were purchased
            denominator = float(longTermSharesSold + shortTermSalesSold)
            longProportion = 0.0 if (denominator == 0.0) else float(longTermSharesSold) / denominator

            saleFeeLongTermProportion = Math.round(pos.getFee() * longProportion)
            if self.COST_DEBUG: myPrint("B", "...>>>> pos.getSharesAdded(): %s, longTermSharesSold: %s, shortTermSalesSold: %s = longProportion: %s,  pos.getFee(): %s, saleFeeLongTermProportion: %s"
                                              %(gsdv(pos.getSharesAdded()), gsdv(longTermSharesSold), gsdv(shortTermSalesSold), longProportion, gidv(pos.getFee()), gidv(saleFeeLongTermProportion)))

            costBasis = -(pos.getCostBasis()) + pos.getFee()                                                            # todo MDFIX

            if self.getUsesAverageCost():
                longTermCostBasis = Math.round(-(pos.getCostBasis()) * longProportion)      # Exclude sales fee at this point....
                if self.COST_DEBUG: myPrint("B", "....... longTermCostBasis (excl. sale fee) recalculated to: %s" %(gidv(longTermCostBasis)))

            # NOTE: MD puts the whole sale fee into short-term if there are any short term sales. Do the same for avg cost too.
            # (this improves the tax position) - otherwise the fee is split according to the short/long-term ratio. Previously,
            # the old InvestUtil.getLotBasedCostCapGain() would only add the fee to the long-term basis.
            longCostBasis = longTermCostBasis + (saleFeeLongTermProportion if shortTermSalesSold == 0 else 0)
            shortCostBasis = costBasis - longCostBasis

            # This method below allocates the fee across ST/LT (not used as MD dumps the whole fee into ST when split between ST/LT....
            # longCostBasis = longTermCostBasis + saleFeeLongTermProportion;
            # shortCostBasis = costBasis - longCostBasis

            # st/lt available only used for (the now obsolete) U.S. IRS double-category reporting
            # only applies to average cost based shares... Use -1 when lot based...
            previousPosShrsOwnedAdjusted = self.secCurr.adjustValueForSplitsInt(pos.getPreviousPos().getDate(), pos.getPreviousPos().getSharesOwnedAsOfThisTxn(), pos.getDate())
            longTermAvailShares = Math.round(float(previousPosShrsOwnedAdjusted) * longProportion) if self.getUsesAverageCost() else -1
            shortTermAvailShares = (previousPosShrsOwnedAdjusted - longTermAvailShares) if self.getUsesAverageCost() else -1

            if self.COST_DEBUG:
                if self.getUsesAverageCost():
                    if self.COST_DEBUG: myPrint("B", "...... (US IRS 'double-category' st/lt pools prior to this sale (as at the date of this sale): shortTermAvailShares: %s, longTermAvailShares: %s = shares owned: %s)"
                                                      %(gsdv(shortTermAvailShares), gsdv(longTermAvailShares), gsdv(pos.getPreviousPos().getSharesOwnedAsOfThisTxn())))

            totSaleSharesAvailable = -1L if (shortTermAvailShares == -1L and longTermAvailShares == -1L) else (shortTermAvailShares + longTermAvailShares)

            result = CapitalGainResult(
                            None, None, None,
                            (shortTermSalesSold + longTermSharesSold), shortTermSalesSold, longTermSharesSold,
                            totSaleSharesAvailable, shortTermAvailShares, longTermAvailShares,
                            0L, 0L, 0L,
                            costBasis, shortCostBasis, longCostBasis,
                            0L, 0L, 0L,
                            not isUnmatchedSell, True, False, pos.getTxn(),
                            "cost_basis_invalid" if isUnmatchedSell else messageKey)

            if self.COST_DEBUG: myPrint("B", "... calculated gain for '%s' from position " %(self.getSecAccount()), pos, "\nprevious position:", pos.getPreviousPos(), "\n-->", result)

            return result

        class SharesOwnedAsOf:
            def __init__(self, secAccount, asOfDate, sharesOwnedAsOf, costBasisAsOf, isCostBasisValid=True):
                self.secAccount = secAccount
                self.asOfDate = asOfDate
                self.sharesOwnedAsOf = sharesOwnedAsOf
                self.costBasisAsOf = costBasisAsOf
                self._isCostBasisValid = isCostBasisValid

            def getSecAccount(self): return self.secAccount
            def getAsOfDate(self): return self.asOfDate
            def getSharesOwnedAsOf(self): return self.sharesOwnedAsOf
            def getCostBasisAsOf(self): return self.costBasisAsOf
            def isCostBasisValid(self): return self._isCostBasisValid

        class Position:
            def __init__(self, callingClass, txn=None, previousPosition=None):
                # type: (MyCostCalculation, AbstractTxn, MyCostCalculation.Position) -> None
                self.callingClass = callingClass
                self.previousPos = previousPosition
                self.buyAllocations = ArrayList()
                self.sellAllocations = ArrayList()
                self.sellTxn = False
                self.buyTxn = False
                self.miscIncExp = False
                self.txn = txn
                self.date = 0 if (txn is None) else txn.getDateInt()
                fields = InvestFields()                                                                                 # type: InvestFields
                if txn is not None:
                    fields.setFieldStatus(txn.getParentTxn())
                else:
                    fields.txnType = InvestTxnType.BANK

                txnCostBasis = 0
                txnShares = 0
                txnFee = 0
                txnRunningCost = 0 if (previousPosition is None) else previousPosition.getRunningCost()

                if fields.txnType in [InvestTxnType.BUY, InvestTxnType.BUY_XFER, InvestTxnType.COVER, InvestTxnType.DIVIDEND_REINVEST]:
                    txnShares = fields.shares
                    buyCost = Math.round(float(txnShares) / fields.price)

                    # SCB: MD2024(5118) fix - previously checked 'if (buyCost == 0L)'; also added check for buy shares with zero value...
                    # manual adjustment of costbasis when buy zero shares; or buy shares for zero value to make zero cost basis (features ;->)
                    txnCostBasis = fields.amount if (txnShares == 0) else 0 if (fields.amount == 0) else (buyCost + fields.fee)
                    txnFee = fields.fee
                    self.buyTxn = True
                    if self.callingClass.COST_DEBUG:
                        myPrint("B", ">> BUY: prev date: %s prev shrs asofasof: %s asof date: %s "
                                     "prev running cost: %s "
                                     "txnShares: %s "
                                     "fields.amount: %s "
                                     "buyCost: %s "
                                     "txnCostBasis: %s"
                                     %(previousPosition.getDate(), previousPosition.getSharesOwnedAsOfAsOf(), self.callingClass.getAsOfDate(), txnRunningCost, txnShares, fields.amount, buyCost, txnCostBasis))

                elif fields.txnType in [InvestTxnType.SELL, InvestTxnType.SELL_XFER, InvestTxnType.SHORT]:
                    txnShares = -fields.shares
                    runningAvgPrice = 0.0 if (fields.amount == 0) else float(fields.price)  # SCB: MD2024(5118) fix. When amount is zero, set price to zero too
                    if (previousPosition is not None and previousPosition.getSharesOwnedAsOfAsOf() != 0):
                        priorSharesOwnedAdjusted = self.callingClass.secCurr.unadjustValueForSplitsInt(previousPosition.getDate(), previousPosition.getSharesOwnedAsOfAsOf(), self.callingClass.getAsOfDate())
                        runningAvgPrice = float(txnRunningCost) / float(priorSharesOwnedAdjusted)
                        if self.callingClass.COST_DEBUG:
                            myPrint("B", ">> SELL: prev date: %s prev shrs asofasof: %s asof date: %s "
                                         "prev running cost: %s "
                                         "prior shrs owned adjusted: %s "
                                         "new avg running price: %s"
                                         %(previousPosition.getDate(), previousPosition.getSharesOwnedAsOfAsOf(), self.callingClass.getAsOfDate(), txnRunningCost, priorSharesOwnedAdjusted, runningAvgPrice))

                    # Next two lines.... SCB: MD2024(5118) fix (for avg cost, buy 60, split 7:1, sell 20, split 4:1 issue)
                    sellCost = Math.round(float(txnShares) * runningAvgPrice)

                    # note: previousPosition is always non-None for a SELL (dummy start Position guarantees this)
                    sellCost = self.callingClass.secCurr.unadjustValueForSplitsInt(previousPosition.getDate(), sellCost, self.getDate())

                    # SCB: MD2024(5118) fix - previously checked 'if (sellCost == 0L)'
                    # manual adjustment of costbasis when sell/buy zero shares (feature ;->)
                    txnCostBasis = (-fields.amount - fields.fee) if (txnShares == 0) else sellCost

                    txnFee = fields.fee
                    self.sellTxn = True

                elif fields.txnType in [InvestTxnType.MISCINC, InvestTxnType.MISCEXP]:
                    txnFee = fields.fee
                    txnCostBasis = fields.fee
                    self.miscIncExp = True

                elif fields.txnType in [InvestTxnType.BANK, InvestTxnType.DIVIDEND, InvestTxnType.DIVIDENDXFR]: pass

                txnSharesUnadjusted = txnShares
                txnSharesAdjusted = callingClass.secCurr.adjustValueForSplitsInt(self.getDate(), txnSharesUnadjusted, callingClass.getAsOfDate())
                self.fee = txnFee
                self.sharesAdded = txnSharesUnadjusted
                self.sharesAddedAsOfAsOf = txnSharesAdjusted
                self.unallottedSharesAdded = self.getSharesAdded()
                self.costBasis = txnCostBasis
                self.runningCost = (txnRunningCost + txnCostBasis)
                self.sharesOwnedAsOfAsOf = (txnSharesAdjusted + (0 if previousPosition is None else previousPosition.getSharesOwnedAsOfAsOf()))

                if self.sharesOwnedAsOfAsOf == 0:
                    # No shares equals no cost basis..!
                    # Possible issue when you perform sell zero with amount to adjust cost basis AFTER selling all!?
                    self.runningCost = 0

                if previousPosition is None:
                    self.sharesOwnedAsOfThisTxn = txnSharesUnadjusted
                else:
                    previousPosShrsOwnedAdjusted = callingClass.secCurr.adjustValueForSplitsInt(previousPosition.getDate(), previousPosition.getSharesOwnedAsOfThisTxn(), self.getDate())
                    self.sharesOwnedAsOfThisTxn = previousPosShrsOwnedAdjusted + txnSharesUnadjusted

                if self.callingClass.COST_DEBUG: myPrint("B", "@@ Added Position:", self)

            def actualCostBasisImpact(self):
                # type: () -> int
                if self.previousPos is None: return None                        # Probably on the initial 'dummy' position
                if self.txn is None: return None                                # Should never happen - logic error
                if self.callingClass.isUnmatchedSellTxn(self.txn): return None  # Sell txn that caused invalid cost basis
                if not self.sellTxn and not self.buyTxn and self.sharesAdded == 0L and self.costBasis == 0L: return None  # e.g. dividend - has no bearing on cost
                return self.runningCost - self.previousPos.getRunningCost()

            def getPreviousPos(self): return self.previousPos
            def isSellTxn(self): return self.sellTxn
            def isBuyTxn(self): return self.buyTxn
            def isMiscIncExpTxn(self): return self.miscIncExp

            def getTxn(self):
                # type: () -> AbstractTxn
                return self.txn

            def getSharesOwnedAsOfAsOf(self):
                # type: () -> int
                """This is the running total of all shares owned adjusted up to the requested asof date (i.e. not the number of shares as at the date of the txn)"""
                return self.sharesOwnedAsOfAsOf

            def getSharesOwnedAsOfThisTxn(self):
                # type: () -> int
                """This is the running total of all shares owned adjusted only up to the date of this txn (i.e. not the number of shares adjusted to the asof date)"""
                return self.sharesOwnedAsOfThisTxn

            def getSharesAdded(self):
                # type: () -> int
                """The number of shares on this txn asof the sell/buy date - not adjusted for splits"""
                return self.sharesAdded

            def getSharesAddedAsOfAsOf(self):
                # type: () -> int
                """The number of shares on this txn adjusted for splits up to the requested asof date"""
                return self.sharesAddedAsOfAsOf

            def getRunningCost(self):
                # type: () -> int
                return self.runningCost

            def setRunningCost(self, newRunningCost):
                # type: (int) -> None
                self.runningCost = newRunningCost

            def getCostBasis(self):
                # type: () -> int
                return self.costBasis

            def setCostBasis(self, newCostBasis):
                # type: (int) -> None
                self.costBasis = newCostBasis

            def getFee(self):
                # type: () -> int
                return self.fee

            def getDate(self):
                # type: () -> int
                return self.date

            def getUnallottedSharesAdded(self):                     # asof the sell/buy date unadjusted
                # type: () -> int
                return self.unallottedSharesAdded

            def setUnallottedSharesAdded(self, uasa):
                # type: (int) -> None
                self.unallottedSharesAdded = uasa

            def getBuyAllocations(self):
                # type: () -> [MyCostCalculation.Allocation]
                return self.buyAllocations

            # def setBuys(self, buyList):
            #     # type: ([MyCostCalculation.Allocation]) -> None
            #     self.buyAllocations = buyList

            def getSellAllocations(self):
                # type: () -> [MyCostCalculation.Allocation]
                return self.sellAllocations

            # def setSells(self, sellList):
            #     # type: ([MyCostCalculation.Allocation]) -> None
            #     self.sellAllocations = sellList

            def toString(self):
                # type: () -> String
                i = 12
                sb = StringBuilder()
                sb.append(pad(self.getDate(), 8))
                sb.append("\t").append(pad("buy:" if self.isBuyTxn() else "sell:",5)).append(rpad(self.callingClass.secCurr.formatSemiFancy(Math.abs(self.getSharesAdded()), '.'), i))
                sb.append("\tfee:").append(rpad(self.callingClass.investCurr.formatSemiFancy(self.getFee(), '.'), i))
                sb.append("\tcostBasis: ").append(rpad(self.callingClass.investCurr.formatSemiFancy(self.getCostBasis(), '.'),i))
                sb.append("\ttotcost: ").append(rpad(self.callingClass.investCurr.formatSemiFancy(self.getRunningCost(), '.'),i))
                actualCBI = self.actualCostBasisImpact()
                sb.append("\tactualCostBasisImpact: ").append(rpad(self.callingClass.investCurr.formatSemiFancy(actualCBI, '.') if actualCBI is not None else "null", i))
                if (self.getSharesAdded() != 0):
                    sb.append("\tprice: ").append(rpad(self.callingClass.investCurr.getDoubleValue(self.getCostBasis()) / self.callingClass.secCurr.getDoubleValue(self.getSharesAdded()),i))
                else:
                    sb.append("\tprice: ").append(pad("",i))
                sb.append("\ttotshrs: ").append(rpad(self.callingClass.secCurr.formatSemiFancy(self.getSharesOwnedAsOfAsOf(), '.'),i))

                if (self.getBuyAllocations().size() > 0):
                    sb.append("\n  buys:\n")
                    for aBuy in self.getBuyAllocations():                                                               # type: MyCostCalculation.Allocation
                        sb.append("    ").append(aBuy).append('\n')

                if (self.getSellAllocations().size() > 0):
                    sb.append("\n  sells:\n")
                    for aSell in self.getSellAllocations():                                                             # type: MyCostCalculation.Allocation
                        sb.append("    ").append(aSell).append('\n')
                return sb.toString()
            def __str__(self):  return self.toString()
            def __repr__(self): return self.toString()

            def price(self, excludeFee):                                                                                # todo MDFIX
                # type: (bool) -> float
                """Return the price of this transaction, excluding the fee if excludeFee==true"""
                shrsAdded = self.callingClass.secCurr.getDoubleValue(Math.abs(self.getSharesAdded()))
                txnFee = self.getFee() if (excludeFee) else 0
                return 0.0 if (shrsAdded == 0.0) else self.callingClass.investCurr.getDoubleValue(Math.abs(self.getCostBasis() - txnFee)) / shrsAdded

            def getBasisPrice(self):
                # type: () -> float
                shares = self.getSharesOwnedAsOfAsOf()
                return 0.0 if (shares == 0) else self.callingClass.investCurr.getDoubleValue(self.getRunningCost()) / self.callingClass.secCurr.getDoubleValue(shares)

        class Allocation:
            """Class that references a transaction and number of shares allocated from that transaction"""

            def __init__(self, callingClass, sharesAllocated, sharesAllocatedAdjusted, costBasisAllocated, allocatedPosition):
                # type: (MyCostCalculation, int, int, int, MyCostCalculation.Position) -> None
                self.callingClass = callingClass
                self.sharesAllocated = sharesAllocated
                self.sharesAllocatedAdjusted = sharesAllocatedAdjusted
                self.costBasisAllocated = costBasisAllocated
                self.allocatedPosition = allocatedPosition

            def getSharesAllocatedAdjusted(self):
                # type: () -> int
                return self.sharesAllocatedAdjusted

            def setSharesAllocatedAdjusted(self, saa):
                # type: (int) -> None
                self.sharesAllocatedAdjusted = saa

            def getSharesAllocated(self):
                # type: () -> int
                return self.sharesAllocated

            def setSharesAllocated(self, sa):
                # type: (int) -> None
                self.sharesAllocated = sa

            def getCostBasisAllocated(self):
                # type: () -> int
                return self.costBasisAllocated

            def setCostBasisAllocated(self, cba):
                # type: (int) -> None
                self.costBasisAllocated = cba

            def getAllocatedPosition(self):
                # type: () -> MyCostCalculation.Position
                return self.allocatedPosition

            def setAllocatedPosition(self, position):
                # type: (MyCostCalculation.Position) -> None
                self.allocatedPosition = position

            def toString(self):
                i = 14
                allocatedPosition = self.getAllocatedPosition()
                price = allocatedPosition.price(False)
                strTxt = ("%s %s shrs x %s = %s (shrs adjusted: %s)"
                          %(pad(self.allocatedPosition.getDate(), 8),
                            rpad(self.callingClass.secCurr.format(self.getSharesAllocated(), '.'), i),
                            rpad(price, i),
                            rpad(self.callingClass.secCurr.getDoubleValue(self.getSharesAllocated()) * self.allocatedPosition.price(True), i),
                            rpad(self.callingClass.secCurr.format(self.getSharesAllocatedAdjusted(), '.'), i)))
                return strTxt
            def __str__(self):  return self.toString()
            def __repr__(self): return self.toString()

        @staticmethod
        def isCostBasisValid(sec, debug=False):                                                                         # noqa
            # type: (Account, bool) -> bool
            unmatchedSaleLots = MyCostCalculation.getInvalidLotMatchSellTxns(sec=sec, txns=None, failFast=True, debug=debug)
            return unmatchedSaleLots is None or len(unmatchedSaleLots) < 1

        @staticmethod
        def getInvalidLotMatchSellTxns(sec, txns=None, failFast=False, debug=False):                                    # noqa
            # type: (Account, TxnSet, bool, bool) -> [SplitTxn]

            if debug: myPrint("B", "debugging MyCostCalculation::getInvalidLotMatchSellTxns for '%s' method: '%s' >> validating....."
                              %(sec, "average cost" if sec.getUsesAverageCost() else "lot control"))

            unmatchedSaleLots = LinkedHashSet()
            isValid = True

            if not sec.getUsesAverageCost():
                buyTxnIDtoSellTxnsMap = HashMap()
                curr = sec.getCurrencyType()
                buyTxnSet = TxnSet()
                sellTxnSet = TxnSet()
                allValidBuysList = Hashtable()
                tSet = sec.getBook().getTransactionSet()
                txnSet = txns if isinstance(txns, TxnSet) else tSet.getTransactionsForAccount(sec)

                for i in range(0, txnSet.getSize()):
                    absTxn = txnSet.getTxn(i)
                    txnType = absTxn.getParentTxn().getInvestTxnType()

                    if txnType in [InvestTxnType.BUY, InvestTxnType.SELL, InvestTxnType.BUY_XFER, InvestTxnType.SELL_XFER]:
                        split = TxnUtil.getSecurityPart(absTxn.getParentTxn())
                        if split is None: continue
                        if split.getSplitAmount() > 0:
                            buyTxnSet.addTxn(split)
                        elif split.getSplitAmount() < 0:
                            sellTxnSet.addTxn(split)
                        else:
                            myPrint("B", "... ignoring '%s' for zero shares.. split.dateInt: %s split.parentAmount: %s" %(txnType, split.getDateInt(), split.getParentAmount()))

                    elif txnType in [InvestTxnType.DIVIDEND, InvestTxnType.DIVIDEND_REINVEST]:
                        split = TxnUtil.getSecurityPart(absTxn.getParentTxn())
                        if split is None: continue
                        if split.getSplitAmount() > 0:
                            buyTxnSet.addTxn(split)

                for i in range(0, sellTxnSet.getSize()):
                    stxn = sellTxnSet.getTxn(i)
                    shares = abs(stxn.getValue())

                    checkNumShares = TxnUtil.getNumShares(txnSet, stxn)
                    if debug: myPrint("B", "... stxn.dateInt: %s txn shares: %s validated saved matched shares: %s" %(stxn.getDateInt(), shares, checkNumShares))

                    if shares != checkNumShares:
                        isValid = False
                        unmatchedSaleLots.add(stxn)
                        if debug: myPrint("B", "... shares: %s != checkNumShares: %s - result: %s" %(shares, checkNumShares, isValid))
                        if failFast: return list(unmatchedSaleLots)
                        continue

                    sellTxnBuyTable = TxnUtil.parseCostBasisTag(stxn)
                    if sellTxnBuyTable is None:
                        isValid = False
                        unmatchedSaleLots.add(stxn)
                        if debug: myPrint("B", "... sellTxnBuyTable is null...  result: %s" %(isValid))
                        if failFast: return list(unmatchedSaleLots)
                        continue

                    for txnID in sellTxnBuyTable.keySet():
                        plusValue = sellTxnBuyTable.get(txnID)
                        existingValue = allValidBuysList.get(txnID)
                        if existingValue is not None:
                            adjustedShares = curr.adjustValueForSplitsInt(stxn.getDateInt(), plusValue)
                            newValue = existingValue + adjustedShares                                                   # noqa
                            allValidBuysList.put(txnID, newValue)
                        else:
                            allValidBuysList.put(txnID, curr.adjustValueForSplitsInt(stxn.getDateInt(), sellTxnBuyTable.get(txnID)))

                        existingSells = buyTxnIDtoSellTxnsMap.get(txnID)
                        if existingSells is None:
                            existingSells = HashSet()
                            buyTxnIDtoSellTxnsMap.put(txnID, existingSells)
                        existingSells.add(stxn)

                for txnID in allValidBuysList.keySet():
                    numShares = allValidBuysList.get(txnID)
                    txn = TxnUtil.getTxnByID(buyTxnSet, txnID)
                    if txn is None:
                        isValid = False
                        relatedSells = buyTxnIDtoSellTxnsMap.get(txnID)
                        if relatedSells is not None:
                            for s in relatedSells: unmatchedSaleLots.add(s)
                        if debug: myPrint("B", "... txnID: '%s' from allValidBuysList not found in buyTxnSet...  result: %s" %(txnID, isValid))
                        if failFast: return list(unmatchedSaleLots)
                        continue

                    valueAdjusted = curr.adjustValueForSplitsInt(txn.getDateInt(), txn.getValue())
                    if valueAdjusted < numShares:
                        isValid = False
                        relatedSells = buyTxnIDtoSellTxnsMap.get(txnID)
                        if relatedSells is not None:
                            for s in relatedSells: unmatchedSaleLots.add(s)
                        if debug: myPrint("B", "... txnId '%s' from allValidBuysList - txn.date: %s txn.value: %s adjustValueForSplitsInt: %s < numShares: %s result: %s"
                                          %(txnID, txn.getDateInt(), txn.getValue(), valueAdjusted, numShares, isValid))
                        if failFast: return list(unmatchedSaleLots)
                        continue

                    if debug: myPrint("B", "... txn.date: %s txn.value: %s adjustValueForSplitsInt: %s numShares: %s result: %s"
                                      %(txn.getDateInt(), txn.getValue(), valueAdjusted, numShares, isValid))

            if debug: myPrint("B", "... result: %s" %(isValid))
            return list(unmatchedSaleLots) if (unmatchedSaleLots.size() > 0) else None
    ####################################################################################################################




    #### END EXTRA CODE HERE ####

    _extra_code_initialiser()
    myPrint("DB", "Extra Code Initialiser finished....")

except QuickAbortThisScriptException: pass
