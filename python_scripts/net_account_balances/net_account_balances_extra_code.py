#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# net_account_balances_extra_code.py build: 1005 - October 2026 - Stuart Beesley StuWareSoftSystems

# To avoid the dreaded issue below, moving some code here....:
# java.lang.RuntimeException: java.lang.RuntimeException: For unknown reason, too large method code couldn't be resolved

# build: 1000 - NEW SCRIPT
# build: 1001 - Updated MyCostCalculation(v10) - inline with MD2026(5500)
# build: 1002 - Updated MyCostCalculation(v11) - inline with MD2027(5511) alpha 5th September 2027 (MD2026 was never released)
# build: 1003 - Updated MyCostCalculation(v12) - inline with MD2027(5512) alpha 18th September 2027
# build: 1004 - Updated MyCostCalculation(v14) - inline with MD2027(5512) alpha 21st September 2027 (preparedTxns)
# build: 1005 - Updated MyCostCalculation(v15) - inline with MD2027(5512) alpha 3rd October 2026 (CC fixes, tax dates); added MyCapitalGainResult(v1)
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
from com.infinitekind.moneydance.model import AccountBook, InvestFields, InvestTxnType
# from com.infinitekind.moneydance.model import CapitalGainResult                      # no longer used - replaced by MyCapitalGainResult (below)
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
    class MyCapitalGainResult:
        """Capital gain result (v1). Backport of MD's CapitalGainResult() - only as much of it as MyCostCalculation uses.
        # v1: MD2027(5512) - MD's own class can no longer be used by MyCostCalculation: the useTaxDate / selectSalesByTaxDate constructor
        #     parameters only exist from MD2027(5512), so on any older build the calls would fail. Property names are the same as the original.
        #     Backported: the primary constructor, and the 'invalid result with an error message' constructor (txn, errorKey, useTaxDate, selectSalesByTaxDate)
        #     as the class method invalidResult(). Not backported (MyCostCalculation does not use them): the other five secondary constructors - listed in the class.
        """
        # KDoc:
        #Tracks the result of a capital gain computation, including both short term and long term
        #gains. The class is immutable. Updated by Stuart Beesley February 2024 - since MD2024(5100)
        #to allow a more 'complete' set of values to be stored along with the updated CostCalculation class.
        #WARNING: Check isValid() before using results. If not valid then you should assume zeros and no gain calculation!
        #@property totSaleSharesAvailable      The three 'available' fields (this one, [totSaleSharesAvailableShort], [totSaleSharesAvailableLong]) are only
        #                               calculated for average cost securities, and only when CostCalculation.CALCULATE_AVG_COST_DOUBLE_CATEGORY is on.
        #                               Otherwise all three are 0 (lot-based securities gave -1 before MD2027).
        #@property useTaxDate           true when the calculation used tax dates for the long/short term split (and for the order of a gains list). Default false. @since MD2027
        #@property selectSalesByTaxDate true when the sale(s) were selected by tax date - a sale's tax date, not its transaction date, fell within
        #                               the date range asked for. Default false. @since MD2027
        #@author Sean Reilly & Stuart Beesley
        #@since 2024-02-01
        #

        VERSION = 1

        def __init__(self, secAcct,
                     asOfDateInt,
                     selectedDateRange,
                     totSaleShares,
                     totSaleSharesShort,
                     totSaleSharesLong,
                     totSaleSharesAvailable,
                     totSaleSharesAvailableShort,
                     totSaleSharesAvailableLong,
                     totSaleValue,
                     totSaleValueShort,
                     totSaleValueLong,
                     totSaleBasis,
                     totSaleBasisShort,
                     totSaleBasisLong,
                     totSaleGains,
                     totSaleGainsShort,
                     totSaleGainsLong,
                     isValid,
                     isSimpleResult,
                     isCompleteResult,
                     txn,
                     errorMessageKey,
                     useTaxDate=False,
                     selectSalesByTaxDate=False):
            # type: (Account, int, DateRange, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, bool, bool, bool, SplitTxn, str, bool, bool) -> None
            # the primary constructor - same parameters, in the same order, as the kotlin
            self.secAcct = secAcct                                                  # type: Account
            self.asOfDateInt = asOfDateInt                                          # type: int
            self.selectedDateRange = selectedDateRange                              # type: DateRange
            self.totSaleShares = totSaleShares
            self.totSaleSharesShort = totSaleSharesShort
            self.totSaleSharesLong = totSaleSharesLong
            self.totSaleSharesAvailable = totSaleSharesAvailable                    # @Deprecated("Obsolete U.S. IRS double-category method (withdrawn 2011)")
            self.totSaleSharesAvailableShort = totSaleSharesAvailableShort          # @Deprecated("Obsolete U.S. IRS double-category method (withdrawn 2011)")
            self.totSaleSharesAvailableLong = totSaleSharesAvailableLong            # @Deprecated("Obsolete U.S. IRS double-category method (withdrawn 2011)")
            self.totSaleValue = totSaleValue
            self.totSaleValueShort = totSaleValueShort
            self.totSaleValueLong = totSaleValueLong
            self.totSaleBasis = totSaleBasis
            self.totSaleBasisShort = totSaleBasisShort
            self.totSaleBasisLong = totSaleBasisLong
            self.totSaleGains = totSaleGains
            self.totSaleGainsShort = totSaleGainsShort
            self.totSaleGainsLong = totSaleGainsLong
            self._isValid = isValid                                                 # held as _isValid etc. as isValid() etc. are the accessors (as when calling the original from Jython)
            self._isSimpleResult = isSimpleResult
            self._isCompleteResult = isCompleteResult
            self.txn = txn                                                          # type: SplitTxn
            self.errorMessageKey = errorMessageKey                                  # type: str
            self.useTaxDate = useTaxDate                                            # type: bool
            self.selectSalesByTaxDate = selectSalesByTaxDate                        # type: bool

        def getSecAcct(self): return self.secAcct
        def getAsOfDateInt(self): return self.asOfDateInt
        def getSelectedDateRange(self): return self.selectedDateRange
        def getTotSaleShares(self): return self.totSaleShares
        def getTotSaleSharesShort(self): return self.totSaleSharesShort
        def getTotSaleSharesLong(self): return self.totSaleSharesLong
        def getTotSaleSharesAvailable(self): return self.totSaleSharesAvailable
        def getTotSaleSharesAvailableShort(self): return self.totSaleSharesAvailableShort
        def getTotSaleSharesAvailableLong(self): return self.totSaleSharesAvailableLong
        def getTotSaleValue(self): return self.totSaleValue
        def getTotSaleValueShort(self): return self.totSaleValueShort
        def getTotSaleValueLong(self): return self.totSaleValueLong
        def getTotSaleBasis(self): return self.totSaleBasis
        def getTotSaleBasisShort(self): return self.totSaleBasisShort
        def getTotSaleBasisLong(self): return self.totSaleBasisLong
        def getTotSaleGains(self): return self.totSaleGains
        def getTotSaleGainsShort(self): return self.totSaleGainsShort
        def getTotSaleGainsLong(self): return self.totSaleGainsLong
        def isValid(self): return self._isValid
        def isSimpleResult(self): return self._isSimpleResult
        def isCompleteResult(self): return self._isCompleteResult
        def getTxn(self): return self.txn
        def getErrorMessageKey(self): return self.errorMessageKey
        def getUseTaxDate(self): return self.useTaxDate
        def getSelectSalesByTaxDate(self): return self.selectSalesByTaxDate

        # @Deprecated("Please use totSaleBasis", ReplaceWith("totSaleBasis"))
        def getBasis(self): return self.totSaleBasis

        # @Deprecated("Please use totSaleBasisShort", ReplaceWith("totSaleBasisShort"))
        def getShortTermBasis(self): return self.totSaleBasisShort

        # @Deprecated("Please use totSaleBasisLong", ReplaceWith("totSaleBasisLong"))
        def getLongTermBasis(self): return self.totSaleBasisLong

        # @Deprecated("Please use totSaleSharesShort", ReplaceWith("totSaleSharesShort"))
        def getShortTermShares(self): return self.totSaleSharesShort

        # @Deprecated("Please use totSaleSharesLong", ReplaceWith("totSaleSharesLong"))
        def getLongTermShares(self): return self.totSaleSharesLong

        # @Deprecated("Please use totSaleSharesAvailableShort", ReplaceWith("totSaleSharesAvailableShort"))
        def getShortTermAvailableShares(self): return self.totSaleSharesAvailableShort

        # @Deprecated("Please use totSaleSharesAvailableLong", ReplaceWith("totSaleSharesAvailableLong"))
        def getLongTermAvailableShares(self): return self.totSaleSharesAvailableLong

        # Jython conversion note: Jython has no constructor overloading, so the kotlin secondary constructors cannot be further __init__ methods.
        # The one that MyCostCalculation uses is backported as the class method invalidResult() - same parameters, same defaults, and it passes
        # the same values on to the primary constructor as the kotlin this(...) does. Call it as: MyCapitalGainResult.invalidResult(txn, errorKey, ...)
        #
        # NOT backported (MyCostCalculation does not use them):
        #   constructor(errorKey: String)
        #       'Constructor - invalid result with an error message.'
        #   constructor(basis, shortTermBasis, longTermBasis, shortTermShares, longTermShares, shortTermAvailShares, longTermAvailShares, messageKey)
        #       'Constructor - valid (simple) result with an optional message key.'         //@Deprecated("Please use the more complete constructor")
        #   constructor(txn, basis, shortTermBasis, longTermBasis, shortTermShares, longTermShares, shortTermAvailShares, longTermAvailShares, messageKey)
        #       'Constructor - valid (simple) result with an optional message key.'         //@Deprecated("Please use the more complete constructor")
        #   constructor(secAcct, asOfDateInt, selectedDateRange, totSaleShares ... totSaleGainsLong, messageKey)
        #       'Constructor - valid (complete) result with an optional message key.'
        #   constructor(txn, secAcct, asOfDateInt, selectedDateRange, totSaleShares ... totSaleGainsLong, messageKey)
        #       'Constructor - valid (complete) result with an optional message key.'

        @classmethod
        def invalidResult(cls, txn, errorKey, useTaxDate=False, selectSalesByTaxDate=False):
            # type: (SplitTxn, str, bool, bool) -> MyCapitalGainResult
            # Constructor - invalid result with an error message.
            # @param errorKey Resource key for message to display to the user (localized).
            # @param txn the source txn for this error
            # @param useTaxDate           see [CapitalGainResult.useTaxDate]. Default false. @since MD2027
            # @param selectSalesByTaxDate see [CapitalGainResult.selectSalesByTaxDate]. Default false. @since MD2027
            # @return CapitalGainResult instance with no values, marked invalid, and with the specified error key.
            return cls(
                None, None, None,
                0, 0, 0,
                0, 0, 0,
                0, 0, 0,
                0, 0, 0,
                0, 0, 0,
                False,
                False, False,
                txn,
                errorKey,
                useTaxDate,
                selectSalesByTaxDate)

        def toString(self):
            secCurr = None if (self.secAcct is None) else self.secAcct.getCurrencyType()
            investCurr = None if (self.secAcct is None) else (None if (self.secAcct.getParentAccount() is None) else self.secAcct.getParentAccount().getCurrencyType())   # noqa
            def gsdv(v): return 0 if (secCurr is None) else secCurr.getDoubleValue(v)
            def gidv(v): return 0 if (investCurr is None) else investCurr.getDoubleValue(v)
            strTxt = ("CapitalGainResult: asof: %s, dateRange: '%s' " %(self.asOfDateInt, self.selectedDateRange)
                      + "totSaleShares:          %s          (short: %s,          long: %s), " %(gsdv(self.totSaleShares), gsdv(self.totSaleSharesShort), gsdv(self.totSaleSharesLong))
                      + "totSaleSharesAvailable: %s (short: %s, long: %s), " %(gsdv(self.totSaleSharesAvailable), gsdv(self.totSaleSharesAvailableShort), gsdv(self.totSaleSharesAvailableLong))
                      + "totSaleValue:           %s        (short: %s,        long: %s), " %(gidv(self.totSaleValue), gidv(self.totSaleValueShort), gidv(self.totSaleValueLong))
                      + "totSaleBasis:           %s        (short: %s,        long: %s), " %(gidv(self.totSaleBasis), gidv(self.totSaleBasisShort), gidv(self.totSaleBasisLong))
                      + "totSaleGains:           %s        (short: %s,        long: %s) - " %(gidv(self.totSaleGains), gidv(self.totSaleGainsShort), gidv(self.totSaleGainsLong))
                      + "isSimpleResult: %s + isCompleteResult: %s - " %(self._isSimpleResult, self._isCompleteResult)
                      + "useTaxDate: %s, selectSalesByTaxDate: %s - " %(self.useTaxDate, self.selectSalesByTaxDate)
                      + "%s - secAcct: '%s' - error/message Key: %s" %("isValid" if self._isValid else "INVALID", self.secAcct, self.errorMessageKey))
            return strTxt
        def __str__(self):  return self.toString()
        def __repr__(self): return self.toString()


    class MyCostCalculation:
        """CostBasis calculation engine (v15). Backport of MD's CostCalculation().
        # v2: LOT control fixes
        # v3: added isCostBasisValid()
        # v4: don't incl. fees on misc inc/exp in cbasis with lots, ...fixes for  capital gains to work
        # v5: added in short/long term support
        # v6: added unRealizedSaleTxn parameter support
        # v7: added SharesOwnedAsOf class to match MD's upgraded CostCalculation class)
        # v8: fixed code to match MD2024(5119) - fixed endless loop, buy 60, split 7:1, sell 20, split 4:1, sell all for zero cost basis scenarios
        # v10: MD2026(5500) applied latest fixes, v11: MD2027(5511) applied latest fixes, v12: MD2027(5512) applied latest fixes
        # v13: MD2027(5512) fixed for preparedTxns and obtainCurrentBalanceToo
        # v15: MD2027(5512) applied latest fixes (own-date shares, lot validity walk, tiny sale after a split, available LT/ST shares), tax date support, now uses MyCapitalGainResult
        """
        # KDoc:
        #Class rewritten/fixed by Stuart Beesley February 2024 - since MD2024(5100)
        #
        #This class is used to calculate the cost of a security using either the average cost or lot-based method.
        #This can be used to produce the cost and gains (both short and long-term) for the security or for individual transactions on the security.
        #
        #Follows U.S. IRS 'single-category' average cost method.
        #- Basis is pooled (single average for all shares).
        #- long/short-term split is determined by assigning sales to purchases in FIFO order to establish each share’s holding period.
        #
        #From U.S. IRS Publication 564 for 2009, under Average Basis, for the 'single-category' method:
        #          <blockquote>
        #          "Even though you include all unsold shares of a fund in a single category to compute average
        #          basis, you may have both short-term and long-term gains or losses when you sell these shares.
        #          To determine your holding period, the shares disposed of are considered to be those acquired first."
        #          https://www.irs.gov/pub/irs-prior/p564--2009.pdf </blockquote>
        #
        #There was a 'double-category' method which allowed you to separate short-term and long-term average cost pools,
        #but the IRS eliminated that method on April 1, 2011. NOTE: this class can still compute the available shares
        #in both short-term and long-term pools so the user can manually run the double-category method. This is
        #controlled by [CALCULATE_AVG_COST_DOUBLE_CATEGORY] - currently on, but it will be off by default in a future release.
        #
        #Notes:
        #      - LOT controlled security accounts can have an invalid cost basis. This is primarily when sell txns are not fully/properly matched to buy txns
        #        - when this condition is detected then results from the cost calculation should be used with care.
        #        - the cost basis for the account will be returned as zero
        #        - capital gains will still be calculated, but will be invalid for any sells not fully/properly matched.
        #      - A sale's fee is never split: it goes wholly to short-term if any short-term shares were sold, else wholly to long-term.
        #      - A buy or sell of zero shares is a manual cost basis adjustment. It is treated like a normal buy / sell: a zero-share buy adds its
        #        amount plus fee to the cost basis; a zero-share sell reduces the cost basis by its amount, and its fee does not affect the cost basis.
        #      - Tax dates ([useTaxDate]): the long-term / short-term holding period test uses each buy's and sale's tax date instead of its transaction
        #        date, and [getListGainsForDateRange] returns its sales in tax date order.
        #        - Nothing else changes: the cost basis, the order transactions are processed in, stock splits, currency conversion and the as-of date
        #          cut all stay on the transaction date.
        #        - Selecting sales by tax date is a separate option on [getListGainsForDateRange] and [getSaleGainsForDateRange] (selectSalesByTaxDate).
        #
        #@since Moneydance 2018.8 (build 1684); Significant upgrade to unified class MD2024(5100)
        #
        #@property secAccount             The security account
        #@property asOfDate               Default: null. The as-of date for this calculation. Pass null to calculate and use the balance date (which can be today or future)
        #@param preparedTxns              Default: null. Optional. A candidate set of txns for this security account, which saves this calculation scanning the whole book.
        #                                 It is not the authoritative universe: the txns supplied are still filtered to [secAccount] and to the as-of date, and are copied
        #                                 into this calculation's own set, so the supplied [TxnSet] is never mutated.
        #@param obtainCurrentBalanceToo   Default: false. When true and this calculation's as-of date is after today, a second calculation dated today is performed - result stored in the [currentBalanceCostCalculation] property.
        #                                 When the as-of date is today or earlier, [currentBalanceCostCalculation] is this calculation itself - so with a past as-of date it is NOT a today calculation.
        #                                 Cannot be combined with [unRealizedSaleTxn].
        #@property unRealizedSaleTxn      Default: null. Optional. Specify a dummy sell txn that can be used to generate un-realised gains. Will be appended to the list of transactions.
        #                                 Always supply it here, never inside [preparedTxns] - otherwise it cannot be identified later (so cannot be excluded via excludeSyntheticTxn),
        #                                 it would be lot validated as though it were a real sell, and it would be cut by the as-of date filter.
        #@property useTaxDate            Default: false. When true the LT/ST holding period test uses the txn's tax date instead of its transaction date, and [getListGainsForDateRange] returns its sales in tax date order. @since MD2027
        #

        COST_DEBUG = False
        VERSION = 15

        # Calculates the obsolete U.S. IRS double-category average cost figures (LT/ST shares held before each sale).
        # The IRS withdrew the method in 2011. Currently on; it will be off by default in a future release.
        # When off, the work is skipped and the three totSaleSharesAvailable fields are 0.
        CALCULATE_AVG_COST_DOUBLE_CATEGORY = True

        def __init__(self, secAccount, asOfDate=None, preparedTxns=None, obtainCurrentBalanceToo=False, unRealizedSaleTxn=None, useTaxDate=False):
            # type: (Account, int, TxnSet, bool, SplitTxn, bool) -> None

            if self.COST_DEBUG: myPrint("B", "** MyCostCalculation() initialising..... running asof: %s, for account: '%s' (%s) **"%(asOfDate, secAccount, "AvgCost" if secAccount.getUsesAverageCost() else "LotControl"))

            # prevent callers attempting to request impossible / illogical combinations of parameters
            # an unRealizedSaleTxn is synthetic and is never cut by date, so it must not leak into the current balance calculation
            if obtainCurrentBalanceToo and unRealizedSaleTxn is not None: raise Exception("Cannot obtainCurrentBalanceToo when using unRealizedSaleTxn")

            if unRealizedSaleTxn is not None:
                assert (isinstance(unRealizedSaleTxn, SplitTxn))
                if self.COST_DEBUG: myPrint("B", "... unrealized (sale txn) gain calculation requested for:", unRealizedSaleTxn)

            if preparedTxns is not None:
                if self.COST_DEBUG: myPrint("B", "... preparedTxns parameter specified (containing: %s txns)" %(preparedTxns.getSize()))

            todayInt = DateUtil.getStrippedDateInt()
            if (asOfDate is None or asOfDate < 19000000): asOfDate = None
            self.asOfDate = asOfDate
            self.unRealizedSaleTxn = unRealizedSaleTxn
            self.useTaxDate = useTaxDate

            self.positions = ArrayList()            # Use java Class to exactly mirror original code (rather than [list])
            self.positionsByBuyID = HashMap()       # Use java Class to exactly mirror original code (rather than {dict})
            # SCB: MD2027(5512) - fix so that long term cut off date (used for unrealised balance reporting) dynamically moves depending on the as of date requested.
            # note - we assume that null (today/future = balance) still requires the cutoff date calculated backwards from today...
            self.longTermCutoffDate = DateUtil.incrementDate(self.asOfDate if (self.asOfDate is not None) else todayInt, -1, 0, 0)
            self.secAccount = secAccount
            self.investCurr = secAccount.getParentAccount().getCurrencyType()                                           # type: CurrencyType
            self.secCurr = secAccount.getCurrencyType()                                                                 # type: CurrencyType
            self.usesAverageCost = secAccount.getUsesAverageCost()

            # SCB: MD2027(5512) - fix (part 1) so that the transaction universe for this calculation is limited to the requested as-of date - always, including a supplied preparedTxns list.
            # a supplied preparedTxns is a candidate set that saves us a book scan; it is not the authoritative universe. We always apply our own account / as-of rules to it,
            # and we always build our own TxnSet, so that the sort / insert below never reorders or modifies a set the caller may be sharing across accounts or reports.
            # note: Jython - deliberately NOT using getTransactions(TxnSearch) as MD does. That calls back into Jython once per txn in the WHOLE book,
            # per security account - which runs ~30x slower. getTransactionsForAccount() keeps that scan inside Java; we then cut by date over the small result.
            cutoff = self.asOfDate
            allAcctTxns = preparedTxns if (isinstance(preparedTxns, TxnSet))\
                else secAccount.getBook().getTransactionSet().getTransactionsForAccount(secAccount)
            self.txns = TxnSet()
            for _i in range(0, allAcctTxns.getSize()):
                _t = allAcctTxns.getTxn(_i)
                if (_t.getAccount() == secAccount and (cutoff is None or _t.getDateInt() <= cutoff)): self.txns.addTxn(_t)

            # detect invalid cost basis against THIS calculation's own universe, so a later mistake cannot
            # invalidate an earlier report. Performed before sorting, and before any unRealizedSaleTxn is added.
            self._unmatchedSellTxns = MyCostCalculation.getInvalidLotMatchSellTxns(secAccount, self.txns, False, self.COST_DEBUG)
            if self.isCostBasisInvalid():
                myPrint("B", "@@ WARNING: INVALID Cost Basis for lot controlled security account: '%s' (%s sells not fully / properly lot matched to buys) >> - cost basis defaulting to ZERO"
                        %(self.getSecAccount().getFullAccountName(), len(self.getUnmatchedSellTxns())))
                invalidStr = "[%s]" % ", ".join("%s, %s, %s, %s" %(
                            it.getUUID(), it.getParentTxn().getInvestTxnType(),
                            it.getDateInt(), it.getSplitAmount()) for it in self.getUnmatchedSellTxns())
                myPrint("B", "... invalid cost basis txns: %s" %(invalidStr))

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
                    # SCB: MD2027(5512) - fix (part 2) so that the transaction universe for this calculation is limited to the requested as-of date.
                    # passing our own txns is safe: the constructor below is given a non-null as-of date of today, so it cuts them to today itself.
                    # Both routes reach here: an explicit future as-of date, and the null/balance path whenever any transaction is dated ahead, which is the common one.
                    self.currentBalanceCostCalculation = MyCostCalculation(self.getSecAccount(), todayInt, self.getTxns(), False, None, useTaxDate)
                else:
                    self.currentBalanceCostCalculation = self                                                           # type: MyCostCalculation
            else:
                self.currentBalanceCostCalculation = None                                                               # type: MyCostCalculation

        def isAsOfToday(self): return self._isAsOfToday

        def getCostBasisAsOfAsOf(self): return 0L if (self.isCostBasisInvalid()) else self.getMostRecentPosition().getRunningCost()  # noqa

        def getLongTermCutoffDate(self): return self.longTermCutoffDate
        def getInvestCurr(self): return self.investCurr
        def getSecCurr(self): return self.secCurr

        def getUnRealizedSaleTxn(self): return self.unRealizedSaleTxn

        def getUnmatchedSellTxns(self):
            # Contains a list of sell transactions which have not been full/properly matched to buy txns. Only applies to LOT controlled security accounts.
            # When null then no issues were detected, and the cost basis is considered valid. This determines the [isCostBasisInvalid] property.
            # Note: [unRealizedSaleTxn] will not be validated/included in this result.
            # Refer: [getInvalidLotMatchSellTxns].
            # @since MD2027
            if (self._unmatchedSellTxns is None or len(self._unmatchedSellTxns) <1): return None
            return self._unmatchedSellTxns

        # Determines whether the cost basis for this security account / calculation is invalid.
        # Always false for average cost controlled items (i.e. these always have a valid cost basis).
        # Will be true for LOT controlled security accounts where any sell txns are not fully/properly matched to buy txns.
        # Note: [unRealizedSaleTxn] will not be validated/included in this result.
        # This property is derived from [unmatchedSellTxns].
        def isCostBasisInvalid(self): return (self._unmatchedSellTxns is not None and len(self._unmatchedSellTxns) > 0)
        def getUsesAverageCost(self): return self.usesAverageCost
        def getUseTaxDate(self): return self.useTaxDate

        def getCurrentBalanceCostCalculation(self):
            # type: () -> MyCostCalculation
            return self.currentBalanceCostCalculation

        def getTxns(self): return self.txns

        def getSecAccount(self): return self.secAccount

        def getAsOfDate(self): return self.asOfDate

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

        def getPositionForAsOf(self, excludeSyntheticTxn=False):
            # type: (bool) -> MyCostCalculation.Position
            # Returns the most recent [Position] upto/asof requested.
            # @param excludeSyntheticTxn when false (default) then any (optional) [unRealizedSaleTxn] synthetic unrealized sell-all sale transaction will be included in the result.
            #                            specify true to obtain the pure result for the asof required without the synthetic transaction included.
            # The [excludeSyntheticTxn] parameter / constructor was added @since MD2027
            rtnPos = self.getPositions().get(0)
            for pos in reversed(self.getPositions()):                           # Reversed puts most recent first
                if excludeSyntheticTxn and self.unRealizedSaleTxn is not None and pos.getTxn() == self.unRealizedSaleTxn: continue    # skip the synthetic unrealised sell all txn if needed
                if pos.getDate() > self.asOfDate: continue                      # Skip future posns
                rtnPos = pos
                if pos.getDate() <= self.asOfDate: break                        # Capture the most recent posn we find before/on asof
            return rtnPos

        class SharesOwnedAsOf:
            # Data class containing the shares owned, and cost basis upto/asof the date requested.
            # When a LOT controlled security account's cost basis is invalid, then you can expect [costBasisAsOf] zero, and [isCostBasisValid] false.
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

        def getSharesAndCostBasisForAsOf(self, excludeSyntheticTxn=False):
            # type: (bool) -> (int, int)
            #  Returns a [SharesOwnedAsOf] data class containing the shares owned, and cost basis upto/asof the date requested.
            # @param excludeSyntheticTxn when false (default) then any (optional) [unRealizedSaleTxn] synthetic unrealized sell-all sale transaction will be included in the result.
            # Notes:
            #        - if the calculation's as-of date is null, then null will be returned.
            #        - for LOT controlled securities, `costBasisAsOf` will be zero and `isCostBasisValid` false when the security account's cost basis is invalid.
            # The [excludeSyntheticTxn] parameter / constructor was added @since MD2027
            if self.getAsOfDate() is None: return None
            asofPos = self.getPositionForAsOf(excludeSyntheticTxn=excludeSyntheticTxn)
            costBasisAsOf = 0L if self.isCostBasisInvalid() else asofPos.getRunningCost()
            return MyCostCalculation.SharesOwnedAsOf(self.getSecAccount(), self.getAsOfDate(), asofPos.getSharesOwnedAsOfAsOf(), costBasisAsOf, not self.isCostBasisInvalid())

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

        def deriveTxnDateRange(self, onlyCostImpactingTxns=True):
            # Derive the date range that can be used to describe the transactional range for this security account's cost calculation.
            # [asOfDate] is important. When `null` then it is assumed to be `today` or the most recent transactional date found
            # The start date is derived from the oldest relevant transactional date found.
            # Note: [unRealizedSaleTxn] can artificially extend the derived [asOfDate] / returned end date into the future.
            # @param onlyCostImpactingTxns By default `true` only includes txns that impact the cost basis. Use `false` to include all txns found for [secAccount] (e.g. BANK, DIVIDEND, DIVIDENDXFR)
            # @return derived date range (or null if no transactions were found prior to [asOfDate])
            # @since MD2027
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

        # Detects whether the specified sell txn is not fully/properly matched to buy txn(s) causing an invalid cost basis.
        # Only applies to lot controlled security accounts
        #
        # @param sellTxn The sell txn
        # @return true if the specified sell txn is not properly lot matched and is causing an invalid cost basis
        #
        # @since MD2027
        def isUnmatchedSellTxn(self, sellTxn): return (self.getUnmatchedSellTxns() is not None and sellTxn in self.getUnmatchedSellTxns())

        def addTxn(self, txn):
            # type: (AbstractTxn) -> None
            # Add a transaction for this security to the calculation
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

                    # SCB: MD2027(5512) - fix: a very small sale made after a split (e.g. buy 10, split 7:1, sell 0.0001) rounds to zero shares when taken back to the buy's date.
                    # Previously no allocation was made, the sale was never allotted, and the logic error below was thrown. Now the sale is allotted to this buy
                    # with zero buy-date shares (the buy is left untouched). For average cost this allocation only drives the long/short term split, not the cost.
                    sellRoundsToZeroOnBuy = (unallottedSellShares == 0 and buy.getUnallottedSharesAdded() > 0)

                    if (sharesFromBuy != 0 or sellRoundsToZeroOnBuy):
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
                        buyIdx = numPositions + 1                                                                       # noqa
                        sellIdx = numPositions + 1                                                                      # noqa
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

                            # SCB: MD2027(5512) fix - CUMULATIVE LOT BASIS ROUNDING (part 1 of 2; part 2 is in updateCostBasisForLots)
                            # Take the lot's rounded cumulative basis less what has already been drawn, instead of rounding each allocation on its own - otherwise a lot whose cost does not divide cleanly by its shares
                            # strands the difference and nothing collects it. The remainder lands wherever the running total needs it, not necessarily on the last sale.
                            # ORDER MATTERS: both figures below must be read BEFORE this allocation is added to sellAllocations and BEFORE unallottedSharesAdded is decremented - both happen further down.
                            # drawnBasis is summed from the allocations, so they remain the single source of truth. An over-matched lot is deliberately unguarded - the fraction passes 1 and the reports' own
                            # adjustment rows reverse the excess; clamping it would hide the over-match.
                            drawnShares = lotMatchedBoughtPos.getSharesAdded() - lotMatchedBoughtPos.getUnallottedSharesAdded()
                            drawnBasis = sum([_a.getCostBasisAllocated() for _a in lotMatchedBoughtPos.getSellAllocations()])
                            cumShares = drawnShares + lotMatchedBoughtSharesAdjusted
                            matchedBuyCostBasis = 0 if (lotMatchedBoughtPos.getSharesAdded() == 0) else Math.round(lotMatchedBoughtPos.getCostBasis() * (float(cumShares) / float(lotMatchedBoughtPos.getSharesAdded()))) - drawnBasis

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
                        # SCB: MD2027(5512) fix - CUMULATIVE LOT BASIS ROUNDING (part 2 of 2; part 1 is in allocateLots)
                        # Use the figure allocateLots already stored, not a fresh per-share recompute - recomputing rounds a second time and discards part 1's cumulative rounding. Neither part works without the other.
                        if self.COST_DEBUG: myPrint("B", "...... costBasisAllocated: %s" %(self.investCurr.getDoubleValue(buyAllocation.getCostBasisAllocated())))
                        totMatchedBuyCostBasis += buyAllocation.getCostBasisAllocated()

                    # SCB: MD2027(5511) same bug as the other two, own guard here since this runs in a separate function (lot-matching) that never reaches the fix built into the other two.
                    priorSharesNegativeForLot = (0 if pos.getPreviousPos() is None else pos.getPreviousPos().getSharesOwnedAsOfThisTxn()) < 0
                    pos.setCostBasis(totMatchedBuyCostBasis if priorSharesNegativeForLot else -totMatchedBuyCostBasis)
                    if priorSharesNegativeForLot:
                        if self.COST_DEBUG: myPrint("B", "CC-LOTBASIS-TRAP secAcct=%s txnDate=%s pos.costBasis=%s (not negated)" %(self.getSecAccount(), pos.getDate(), pos.getCostBasis()))
                    if self.COST_DEBUG: myPrint("B", "...... setting sellPos CostBasis to: %s" %(self.investCurr.getDoubleValue(pos.getCostBasis())))

                if not pos.isMiscIncExpTxn():   # Assume that for LOT controlled, we do not add misc inc/exp fee into costbasis (as the cb cannot be assigned to any lot!)
                    runningCostBasis += pos.getCostBasis()

                pos.setRunningCost(runningCostBasis)
                if self.COST_DEBUG: myPrint("B", "... setting Pos runningCost to: %s" %(self.investCurr.getDoubleValue(pos.getRunningCost())))

        def getBasisPrice(self, asOfTxn):
            # type: (AbstractTxn) -> float
            # Returns the cost (per share) of the shares held as of the given transaction, or as of the last transaction if the given transaction is null.
            # Note: For LOT controlled security accounts, if the cost basis is invalid then zero will be returned.
            #
            # @param asOfTxn The transaction for which the gains should apply
            # @return the cost per share

            if self.isCostBasisInvalid(): return 0.0
            if asOfTxn is not None:
                for pos in self.getPositions():                                                                         # type: MyCostCalculation.Position
                    if pos.getTxn() is None: continue
                    if pos.getTxn() == asOfTxn: return pos.getBasisPrice()
                myPrint("B", "getBasisPrice: unable to find position for txn :%s; returning cost basis as of last position" %(asOfTxn))
            return self.getMostRecentPosition().getBasisPrice()                                                         # noqa

        def getTxnPos(self, forTxn):
            # Returns the calculated cost basis [Position] for the specified [SplitTxn] transaction
            #
            # @param forTxn The transaction to locate in positions
            # @return the calculated [Position] for the transaction
            # @since MD2027
            for pos in self.getPositions():
                txn = pos.getTxn()
                if (txn is None): continue
                if (txn == forTxn): return pos
            myPrint("B", "getTxnPos: unable to find position for txn %s; returning null" % (forTxn))
            return None

        def getTxnCostBasisImpact(self, forTxn):
            # Returns the actual cost basis impact that the specified [SplitTxn] transaction has on the running cost basis.
            # Note: Only txn(s) that have a bearing on cost basis will return a value - otherwise null will be returned.
            #       - LOT controlled sell txns that caused invalid cost basis will return null.
            #       - Unfound position(s) will also return null.
            #
            # @see [Position.actualCostBasisImpact]
            #
            # @param forTxn The transaction to locate in positions
            # @return the calculated cost basis impact for the specified transaction. Null if not found. Zero if lot controlled sell txn caused invalid cost basis
            # @since MD2027
            for pos in self.getPositions():
                txn = pos.getTxn()
                if (txn is None): continue
                if (txn != forTxn): continue
                return pos.actualCostBasisImpact()
            myPrint("B", "getTxnCostBasisImpact: unable to find position for txn %s; returning null" % (forTxn))
            return None

        def getSaleGainsForDateRange(self, dateRange, targetCurrency=None, valuationDate=None, selectSalesByTaxDate=False):
            # type: (DateRange, CurrencyType, int, bool) -> MyCapitalGainResult
            # Calculates and returns [CapitalGainResult] containing the grand total of all fields within the date requested.
            # Notes:
            #        - Gains flagged as invalid will be skipped when calculating totals
            #        - The result's `isValid` property will be false if the security account's cost basis is invalid.
            #        - Values are normally returned in the security account's parent (investment) account's currency. You should not directly convert
            #          these returned totals to another currency, as gains should normally be converted individually to another currency using that gain's txn date.
            #          - optionally pass the [targetCurrency] for each gain to be converted into (using the gain's txn's date).
            #        - The method of calculating / totalling the value/basis/gain/LT/ST and conversion to target currency mirror the CapitalGainsReport for consistancy.
            #          - refer [valuationDate] - when enabled, then constant currency mode is enabled and results will mirror the InvestmentPerformanceReport for consistancy.
            #
            # @param dateRange      specify the date range to filter gains (should not end after the asof date!)
            # @param targetCurrency Default null to use the security account's parent (investment) account's currency, or specify to convert each gain to the target currency (as of the txn's date)
            # @param valuationDate  Default null to (re)value / currency convert each gain using the gain's txn date. Specify a date to (re)value each gain using [valuationDate] - i.e. constant currency methodology
            # @param selectSalesByTaxDate Default false: a sale is selected when its transaction date falls within [dateRange].
            #                             When true: a sale is selected when its tax date falls within [dateRange], whatever its transaction date.
            #                             Sales dated after the range end are then read up to this calculation's as-of date only, so the caller
            #                             must build the calculation to a late enough as-of date (refer [deriveTxnDateRangesForTaxDates]).
            #                             Requires [useTaxDate] and no [unRealizedSaleTxn]: throws IllegalArgumentException when true and this
            #                             calculation was built without [useTaxDate], or with an [unRealizedSaleTxn]. Same selection as [getListGainsForDateRange]. The parameter was added @since MD2027
            # @return returns [CapitalGainResult] result which contains totals for the gains within the range, optionally converted to the target currency.
            # Jython conversion note: raises Exception (the kotlin require() throws IllegalArgumentException)
            if selectSalesByTaxDate and not self.useTaxDate: raise Exception("selectSalesByTaxDate requires useTaxDate - build the CostCalculation with useTaxDate = true")
            if selectSalesByTaxDate and self.unRealizedSaleTxn is not None: raise Exception("selectSalesByTaxDate cannot be used with an unRealizedSaleTxn - the synthetic sale would be selected as a realised sale")

            toCurrency = targetCurrency if targetCurrency is not None else self.investCurr
            localIsTarget = (self.investCurr == toCurrency)

            gidv = self.investCurr.getDoubleValue
            gsdv = self.secCurr.getDoubleValue

            if self.COST_DEBUG: myPrint("B", ">> Calculating gains for '%s', DR: '%s' Investment Currency: '%s' >> toCurrency: '%s' valuationDate: %s (%s) useTaxDate: %s, selectSalesByTaxDate: %s"
                                        %(self.getSecAccount(), dateRange, self.investCurr, toCurrency, valuationDate,
                                          "valued by gain/txn date" if valuationDate is None else "constant currency",
                                          self.useTaxDate, selectSalesByTaxDate))

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
                if not selectSalesByTaxDate:
                    if pos.getDate() > dateRange.getEndDateInt(): break
                    if pos.getDate() < dateRange.getStartDateInt(): continue
                elif not dateRange.containsInt(pos.getTxnOrTaxDate()): continue   # by tax date: no early break - a later position can still have a tax date in the range
                txn = pos.getTxn()
                if not isinstance(txn, SplitTxn): continue
                if not pos.isSellTxn(): continue
                gainInfo = self.calculateGainsForPos(pos, selectSalesByTaxDate)
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
                # SCB: MD2027(5512) - fix so that ST is always the remainder to eliminate small differences
                # note: we are treating LT gains as authoritative - ST is the remainder in both currencies, so the two parts always sum back to the total (matches shortCostBasis and shortTermAvailShares below)
                saleGainsShort = saleGains - saleGainsLong
                saleGainsShortTarget = saleGainsTarget - saleGainsLongTarget

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
            result = MyCapitalGainResult(
                self.getSecAccount(), self.asOfDate, dateRange,
                totSaleShares, totSaleSharesShort, totSaleSharesLong,
                0, 0, 0,
                totSaleValue, totSaleValueShort, totSaleValueLong,
                totSaleBasis, totSaleBasisShort, totSaleBasisLong,
                totSaleGains, totSaleGainsShort, totSaleGainsLong,
                not self.isCostBasisInvalid(), False, True, None,
                "cost_basis_invalid" if self.isCostBasisInvalid() else None,
                self.useTaxDate, selectSalesByTaxDate)

            resultTarget = MyCapitalGainResult(
                self.getSecAccount(), self.asOfDate, dateRange,
                totSaleShares, totSaleSharesShort, totSaleSharesLong,
                0, 0, 0,
                totSaleValueTarget, totSaleValueShortTarget, totSaleValueLongTarget,
                totSaleBasisTarget, totSaleBasisShortTarget, totSaleBasisLongTarget,
                totSaleGainsTarget, totSaleGainsShortTarget, totSaleGainsLongTarget,
                not self.isCostBasisInvalid(), False, True, None,
                "cost_basis_invalid" if self.isCostBasisInvalid() else None,
                self.useTaxDate, selectSalesByTaxDate)

            if self.COST_DEBUG:
                myPrint("B", ">>>> Calculated %sgains for '%s', DR: '%s' Investment Currency: '%s' Result:"
                        %("(INVALID COST BASIS) " if self.isCostBasisInvalid() else "", self.getSecAccount(), dateRange, self.investCurr), result)
                if not localIsTarget:
                    myPrint("B", ">>>> Calculated %sgains for '%s', DR: '%s' >> toCurrency: '%s' valuationDate: %s Result:"
                            %("(INVALID COST BASIS) " if self.isCostBasisInvalid() else "", self.getSecAccount(), dateRange, toCurrency, valuationDate), resultTarget)

            return result if localIsTarget else resultTarget

        def getListGainsForDateRange(self, dateRange, selectSalesByTaxDate=False):
            # type: (DateRange, bool) -> [MyCapitalGainResult]
            # Calculates and then returns a list of individual (simple) [CapitalGainResult]s for all sale txns within the date requested
            # Notes:
            #        - the caller should check the status of this cost calculation's `isCostBasisInvalid` property,
            #          along with the status of each returned gain's `isValid` property to handle invalid capital gains.
            #        - Order: when [useTaxDate] or [selectSalesByTaxDate] is true the sales are ordered by tax date, then transaction date;
            #          sales on the same dates keep this calculation's own order (the sort is stable). Otherwise the gains are in this
            #          calculation's own order (transaction date). Either way the unrealised gain ([unRealizedSaleTxn]), when present, stays last.
            #        - Each gain records both options in [CapitalGainResult.useTaxDate] and [CapitalGainResult.selectSalesByTaxDate].
            #
            # @param dateRange            The date range to select the sales by.
            # @param selectSalesByTaxDate Default false: a sale is selected when its transaction date falls within [dateRange].
            #                             When true: a sale is selected when its tax date falls within [dateRange], whatever its transaction date.
            #                             Sales dated after the range end are then read up to this calculation's as-of date only, so the caller
            #                             must build the calculation to a late enough as-of date (refer [deriveTxnDateRangesForTaxDates]).
            #                             Requires [useTaxDate] and no [unRealizedSaleTxn]: throws IllegalArgumentException when true and this
            #                             calculation was built without [useTaxDate], or with an [unRealizedSaleTxn]. The parameter was added @since MD2027

            # Jython conversion note: raises Exception (the kotlin require() throws IllegalArgumentException)
            if selectSalesByTaxDate and not self.useTaxDate: raise Exception("selectSalesByTaxDate requires useTaxDate - build the CostCalculation with useTaxDate = true")
            if selectSalesByTaxDate and self.unRealizedSaleTxn is not None: raise Exception("selectSalesByTaxDate cannot be used with an unRealizedSaleTxn - the synthetic sale would be selected as a realised sale")
            if self.COST_DEBUG: myPrint("B", ">> Calculating list of gains for '%s', DR: '%s', selectSalesByTaxDate: %s" %(self.getSecAccount(), dateRange, selectSalesByTaxDate))

            listGains = ArrayList()
            countInvalidGains = 0

            # Add up all the sales gains manually...
            for pos in self.getPositions():  # iterate oldest to most recent
                if pos.getDate() > self.asOfDate: break
                if not selectSalesByTaxDate:
                    if pos.getDate() > dateRange.getEndDateInt(): break
                    if pos.getDate() < dateRange.getStartDateInt(): continue
                elif not dateRange.containsInt(pos.getTxnOrTaxDate()): continue   # by tax date: no early break - a later position can still have a tax date in the range
                txn = pos.getTxn()

                if not isinstance(txn, SplitTxn): continue
                if not pos.isSellTxn(): continue
                gainInfo = self.calculateGainsForPos(pos, selectSalesByTaxDate)
                if not gainInfo.isValid(): countInvalidGains += 1
                listGains.add(gainInfo)

            if self.COST_DEBUG: myPrint("B", ">>>> returning a list of %s CapitalGainResult(s)%s - useTaxDate: %s, selectSalesByTaxDate: %s - order: %s"
                                        %(listGains.size(), (" - invalid gains count: %s" % (countInvalidGains)) if countInvalidGains > 0 else "",
                                          self.useTaxDate, selectSalesByTaxDate,
                                          "tax date, then transaction date" if (self.useTaxDate or selectSalesByTaxDate) else "transaction date (as calculated)"))
            gains = list(listGains)
            if not self.useTaxDate and not selectSalesByTaxDate: return gains
            sales = []
            others = []
            for gain in gains:
                if (gain.getTxn() is not None and not (self.unRealizedSaleTxn is not None and gain.getTxn() == self.unRealizedSaleTxn)): sales.append(gain)
                else: others.append(gain)
            # arrives in CC order (date, then shares largest first - TxnUtil.DATE_THEN_AMOUNT_COMPARATOR); the sort is stable,
            # so same-day sales keep that order - no UUID tie-break, which would reorder them at random
            sales.sort(key=lambda sale: (sale.getTxn().getTaxDateInt(), sale.getTxn().getDateInt()))
            return sales + others

        def getGainInfo(self, saleTxn):
            # type: (AbstractTxn) -> MyCapitalGainResult
            # Returns the overall capital gain information specific to the given sell transaction.
            # The sell transaction must have the security as its 'account' which means the transaction
            # must be the SplitTxn that is assigned to the security account.  If the transaction is
            # invalid or null then a zero/error capital gains is returned.
            #
            # @param saleTxn The transaction for which the gains should apply
            # @return a CapitalGainResult object with the details of the cost and gains for this transaction

            if saleTxn is None:
                myPrint("B", "you must supply a sale txn; returning Invalid/Zeros")
                return MyCapitalGainResult.invalidResult(None, "sale_txn_not_specified", self.useTaxDate, False)
            for pos in self.getPositions():                                                                             # type: MyCostCalculation.Position
                if (pos.getTxn() is not None and pos.getTxn() == saleTxn):
                    return self.calculateGainsForPos(pos)
            myPrint("B", "unable to find position for txn :%s; returning Invalid/Zeros" %(saleTxn))
            return MyCapitalGainResult.invalidResult(saleTxn, "sale_txn_posn_not_found", self.useTaxDate, False)

        def calculateGainsForPos(self, pos, selectSalesByTaxDate=False):
            # type: (MyCostCalculation.Position, bool) -> MyCapitalGainResult

            assert pos.isSellTxn(), "LOGIC ERROR: Can only be called with a sale txn!"

            gidv = self.investCurr.getDoubleValue
            gsdv = self.secCurr.getDoubleValue

            # Note: we are flagging a sell zero shares txn as invalid (it adjusts the cost basis, and is not a gain)
            if pos.getSharesAdded() == 0: return MyCapitalGainResult.invalidResult(pos.getTxn(), "sell_zero_shares_assume_no_gain", self.useTaxDate, selectSalesByTaxDate)

            isUnmatchedSell = self.isUnmatchedSellTxn(pos.getTxn())

            messageKey = None
            # SCB: MD2027(5512) - fix: test on the sale's own date. The as-of (split-adjusted) shares can round negative after a later reverse split and mislabel a normal sale as short.
            if (pos.getSharesAdded() < 0 and pos.getSharesOwnedAsOfThisTxn() < 0):
                messageKey = "sell_short"       # Short sale: sold shares we didn't have
                if self.COST_DEBUG: myPrint("B", ".... sell_short (sharesAdded: %s, sharesOwnedAsOfThisTxn: %s, sharesAddedAsOfAsOf: %s, sharesOwnedAsOfAsOf: %s"
                                            %(gsdv(pos.getSharesAdded()), gsdv(pos.getSharesOwnedAsOfThisTxn()), gsdv(pos.getSharesAddedAsOfAsOf()), gsdv(pos.getSharesOwnedAsOfAsOf())))

            ltDate = self.longTermCutoffDate if (pos.getTxnOrTaxDate() <= 0) else DateUtil.incrementDate(pos.getTxnOrTaxDate(), -1, 0, 0)

            # figure out how many of the sold shares were long or short term investments
            longTermSharesSold = -(pos.getSharesAdded())
            shortTermSalesSold = 0

            longTermCostBasis = 0

            for buy in pos.getBuyAllocations():                                                                         # type: MyCostCalculation.Allocation
                if buy.getAllocatedPosition().getTxnOrTaxDate() >= ltDate:
                    # SCB: MD2027(5512) - fix so that we track the st/lt shares on the same post-split basis.
                    # The two (avg/lot) builders store these fields in OPPOSITE order: allocateLots() puts the sale-date count in sharesAllocatedAdjusted, allocateAverageCostSales() puts it in sharesAllocated
                    # so the field to read depends on the cost method. This is the only reader that sees both; the others are guarded to lot-matched securities.
                    saleUnits = buy.getSharesAllocated() if self.getUsesAverageCost() else buy.getSharesAllocatedAdjusted()
                    shortTermSalesSold += saleUnits
                    longTermSharesSold -= saleUnits
                else:
                    longTermCostBasis += buy.getCostBasisAllocated()

            # go through all transactions and add up all of the shares that were purchased
            denominator = float(longTermSharesSold + shortTermSalesSold)
            longProportion = 0.0 if (denominator == 0.0) else float(longTermSharesSold) / denominator

            saleFeeLongTermProportion = Math.round(pos.getFee() * longProportion)
            if self.COST_DEBUG: myPrint("B", "...>>>> pos.getSharesAdded(): %s, longTermSharesSold: %s, shortTermSalesSold: %s = longProportion: %s,  pos.getFee(): %s, saleFeeLongTermProportion: %s"
                                              %(gsdv(pos.getSharesAdded()), gsdv(longTermSharesSold), gsdv(shortTermSalesSold), longProportion, gidv(pos.getFee()), gidv(saleFeeLongTermProportion)))

            # SCB: MD2027(5511) unconditional negation assumes cost is always sell-derived - wrong when the prior balance was already negative, since then the cost was built by a buy (a cover).
            priorSharesNegative = (0 if pos.getPreviousPos() is None else pos.getPreviousPos().getSharesOwnedAsOfThisTxn()) < 0
            if priorSharesNegative:
                if self.COST_DEBUG: myPrint("B", "CC-SIGNFLIP-TRAP secAcct=%s txnDate=%s priorShares=%s pos.costBasis=%s (not negated)"
                                                 %(self.getSecAccount(), pos.getDate(), None if pos.getPreviousPos() is None else pos.getPreviousPos().getSharesOwnedAsOfThisTxn(), pos.getCostBasis()))
            costBasis = (pos.getCostBasis() if priorSharesNegative else -(pos.getCostBasis())) + pos.getFee()

            if self.getUsesAverageCost():
                # SCB: MD2027(5511) same guard as the main costBasis fix above, reused here since this Avg-Cost-specific split does the identical unconditional negation in its own line.
                longTermCostBasis = Math.round((pos.getCostBasis() if priorSharesNegative else -(pos.getCostBasis())) * longProportion)      # Exclude sales fee at this point....
                if priorSharesNegative:
                    if self.COST_DEBUG: myPrint("B", "CC-LTBASIS-TRAP secAcct=%s txnDate=%s longTermCostBasis=%s (not negated)" %(self.getSecAccount(), pos.getDate(), longTermCostBasis))
                if self.COST_DEBUG: myPrint("B", "....... longTermCostBasis (excl. sale fee) recalculated to: %s" %(gidv(longTermCostBasis)))

            # The whole sale fee goes to short-term if there are any short-term sales, otherwise it all goes to
            # long-term. It is never split between the two. (MD does the same; this improves the tax position.)
            longCostBasis = longTermCostBasis + (saleFeeLongTermProportion if shortTermSalesSold == 0 else 0)
            shortCostBasis = costBasis - longCostBasis

            # This method below allocates the fee across ST/LT (not used as MD dumps the whole fee into ST when split between ST/LT....
            # longCostBasis = longTermCostBasis + saleFeeLongTermProportion;
            # shortCostBasis = costBasis - longCostBasis

            # st/lt available only used for (the now obsolete) U.S. IRS double-category reporting
            # only applies to average cost based shares... 0 when lot based, or when not calculated (refer [CALCULATE_AVG_COST_DOUBLE_CATEGORY])
            previousPosShrsOwnedAdjusted = self.secCurr.adjustValueForSplitsInt(pos.getPreviousPos().getDate(), pos.getPreviousPos().getSharesOwnedAsOfThisTxn(), pos.getDate())
            # SCB: MD2027(5512) - fix: the long-term shares actually still held just before this sale (was this sale's LT proportion applied to all shares held)
            calcDoubleCategory = self.getUsesAverageCost() and MyCostCalculation.CALCULATE_AVG_COST_DOUBLE_CATEGORY
            longTermAvailShares = self.longTermSharesHeldBefore(pos, ltDate, previousPosShrsOwnedAdjusted) if calcDoubleCategory else 0L
            shortTermAvailShares = (max(previousPosShrsOwnedAdjusted, 0L) - longTermAvailShares) if calcDoubleCategory else 0L

            if self.COST_DEBUG:
                if self.getUsesAverageCost():
                    if self.COST_DEBUG: myPrint("B", "...... (US IRS 'double-category' st/lt pools prior to this sale (as at the date of this sale): shortTermAvailShares: %s, longTermAvailShares: %s = shares owned: %s)"
                                                      %(gsdv(shortTermAvailShares), gsdv(longTermAvailShares), gsdv(pos.getPreviousPos().getSharesOwnedAsOfThisTxn())))

            totSaleSharesAvailable = shortTermAvailShares + longTermAvailShares

            result = MyCapitalGainResult(
                            None, None, None,
                            (shortTermSalesSold + longTermSharesSold), shortTermSalesSold, longTermSharesSold,
                            totSaleSharesAvailable, shortTermAvailShares, longTermAvailShares,
                            0L, 0L, 0L,
                            costBasis, shortCostBasis, longCostBasis,
                            0L, 0L, 0L,
                            not isUnmatchedSell, True, False, pos.getTxn(),
                            "cost_basis_invalid" if isUnmatchedSell else messageKey,
                            self.useTaxDate, selectSalesByTaxDate)

            if self.COST_DEBUG: myPrint("B", "... calculated gain for '%s' from position " %(self.getSecAccount()), pos, "\nprevious position:", pos.getPreviousPos(), "\n-->", result)

            return result

        def longTermSharesHeldBefore(self, sale, ltDate, heldBefore):
            # type: (MyCostCalculation.Position, int, int) -> int
            # Long-term shares still held just before [sale], adjusted to the sale date. Average cost only.
            # A buy's remaining shares are its own shares less those allocated to sales earlier in [positions].
            # A buy is long-term when its date (its tax date when [useTaxDate] is on) is before [ltDate].
            # The result is the holding less the short-term buys' remaining shares. Each buy is split-adjusted and rounded on
            # its own, and old (long-term) buys usually cross splits, so adding those up can be a unit out; recent (short-term)
            # buys rarely cross splits. The long-term buys are added up only to detect that none remain - then 0 is returned.
            # @Deprecated("Obsolete U.S. IRS double-category method (withdrawn 2011) - refer [CALCULATE_AVG_COST_DOUBLE_CATEGORY]")
            if heldBefore <= 0: return 0L
            earlier = set()
            for p in self.positions:
                if p is sale: break
                earlier.add(p)
            heldLT = 0L
            heldST = 0L
            for buy in earlier:
                if buy.getSharesAdded() <= 0: continue
                sold = sum([a.getSharesAllocated() for a in buy.getSellAllocations() if a.getAllocatedPosition() in earlier])
                remaining = self.secCurr.adjustValueForSplitsInt(buy.getDate(), buy.getSharesAdded() - sold, sale.getDate())
                if buy.getTxnOrTaxDate() < ltDate: heldLT += remaining
                else: heldST += remaining
            return 0L if heldLT == 0 else max(0L, min(heldBefore - heldST, heldBefore))

        class Allocation:
            # Class that references a transaction and number of shares allocated from that transaction.
            #  QUANTITY BASIS DIFFERS BY ALLOCATION MODEL - consumers must pick the one they need.
            #  The table below is AS SEEN ON A SELL'S buyAllocations; a buy's sellAllocations are the reverse:
            #    average cost  : sharesAllocated = sale-date, sharesAllocatedAdjusted = buy-date
            #    lot controlled: sharesAllocated = buy-date,  sharesAllocatedAdjusted = sale-date
            #  and both are reversed again between a sell's buyAllocations and a buy's sellAllocations,
            #  because allocateLots() and allocateAverageCostSales() each add the pair with the arguments swapped.
            #  Refer [calculateGainsForPos], the only reader that sees both models.

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
                # SCB: MD2027(5512) - LT/ST classification date only. taxDateInt falls back to dateInt, so this is always a real date.
                self.txnOrTaxDate = (0 if (txn is None) else txn.getTaxDateInt()) if callingClass.getUseTaxDate() else self.date
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
                    # note: InvestFields.amount for a buy already includes the fee (security amount + fee), so a zero-share buy adds amount + fee - as a normal buy does
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
                    # This next line has gone through two fixes:
                    # 1. SCB: MD2024(5118) fix - when amount is zero, set price to zero too - superceded by the next fix...
                    # 2. SCB: MD2027(5511) fix - always default `runningAvgPrice` to zero. Includes fix 1 above, and
                    # now ensures that if we encounter a sell txn when there is zero shareholding (unexpected or short), then we set the running average price to zero...
                    runningAvgPrice = 0.0
                    # SCB: MD2027(5512) - fix: use the shares held at the previous txn's own date (sharesOwnedAsOfThisTxn), instead of its as-of shares unadjusted back
                    # from the as-of date. That round trip rounds at each split, so a reverse / uneven split after the sale could change this (earlier) sale's cost.
                    if (previousPosition is not None and previousPosition.getTxn() is not None and previousPosition.getSharesOwnedAsOfThisTxn() != 0):
                        priorSharesOwnedAdjusted = previousPosition.getSharesOwnedAsOfThisTxn()
                        runningAvgPrice = float(txnRunningCost) / float(priorSharesOwnedAdjusted)
                        if self.callingClass.COST_DEBUG:
                            myPrint("B", ">> SELL: prev date: %s prev shrs asofasof: %s asof date: %s "
                                         "prev running cost: %s "
                                         "prior shrs owned adjusted: %s "
                                         "new avg running price: %s"
                                         %(previousPosition.getDate(), previousPosition.getSharesOwnedAsOfAsOf(), self.callingClass.getAsOfDate(), txnRunningCost, priorSharesOwnedAdjusted, runningAvgPrice))
                    else:
                        if self.callingClass.COST_DEBUG:
                            myPrint("B", ">> SELL: prev date: %s prev shrs asofasof: %s asof date: %s "
                                         "prev running cost: %s "
                                         "prior shrs owned adjusted: N/A "
                                         "new avg running price: %s"
                                         %(None if previousPosition is None else previousPosition.getDate(), None if previousPosition is None else previousPosition.getSharesOwnedAsOfAsOf(), self.callingClass.getAsOfDate(), txnRunningCost, runningAvgPrice))  # noqa

                    # Next two lines.... SCB: MD2024(5118) fix (for avg cost, buy 60, split 7:1, sell 20, split 4:1 issue)
                    sellCost = Math.round(float(txnShares) * runningAvgPrice)

                    # note: previousPosition is always non-None for a SELL (dummy start Position guarantees this)
                    # however previousPosition could be the initial dummy with a None txn if the first txn is a sell (unexpected)
                    if (previousPosition is not None and previousPosition.getTxn() is not None and previousPosition.getSharesOwnedAsOfThisTxn() != 0):    # SCB: MD2027(5512) - fix: same own-date test as above
                        sellCost = self.callingClass.secCurr.unadjustValueForSplitsInt(previousPosition.getDate(), sellCost, self.getDate())

                    # SCB: MD2024(5118) fix - previously checked 'if (sellCost == 0L)'
                    # manual adjustment of costbasis when sell/buy zero shares (feature ;->)
                    # note: InvestFields.amount for a sell is net of the fee (security amount - fee), so '- fields.fee' cancels it: a zero-share sell reduces the
                    # cost basis by the security amount only and the fee does not affect the cost basis - as a normal sell
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

                if previousPosition is None:
                    self.sharesOwnedAsOfThisTxn = txnSharesUnadjusted
                else:
                    previousPosShrsOwnedAdjusted = callingClass.secCurr.adjustValueForSplitsInt(previousPosition.getDate(), previousPosition.getSharesOwnedAsOfThisTxn(), self.getDate())
                    self.sharesOwnedAsOfThisTxn = previousPosShrsOwnedAdjusted + txnSharesUnadjusted

                # SCB: MD2027(5512) - fix: test the shares held on this txn's own date, not the as-of (split-adjusted) shares. A later reverse / uneven split can round
                # a small real holding to zero as-of (wiping its cost and moving a later sale's cost), or round a sold-out holding to non-zero (cost not cleared).
                if self.sharesOwnedAsOfThisTxn == 0:
                    # No shares equals no cost basis..!
                    # Possible issue when you perform sell zero with amount to adjust cost basis AFTER selling all!?
                    self.runningCost = 0

                if self.callingClass.COST_DEBUG: myPrint("B", "@@ Added Position:", self)

            def actualCostBasisImpact(self):
                # type: () -> int
                # Returns the actual cost basis impact that this position's [SplitTxn] transaction has on the running cost basis
                # INFO: there are some txns for which [CostCalculation] will return a [Position] with a cost basis that does not actually affect the running total..
                #    e.g. average cost, sell zero shares for an amount when the total shares owned is zero. With zero shares owned there cannot be a cost basis balance.
                #    e.g. lot controlled, misc exp (zero shares), with fee. A txn with zero shares cannot be lot matched to it corresponding buy/sell.
                # NOTE: lot controlled, sell txns that caused invalid cost basis will return null.
                #
                # @return the calculated cost basis impact for this position (and therefore its transaction), or null if this txn does not / cannot impact the cost basis
                # @since MD2027
                if self.previousPos is None: return None                        # Probably on the initial 'dummy' position
                if self.txn is None: return None                                # Should never happen - logic error
                if self.callingClass.isUnmatchedSellTxn(self.txn): return None  # Sell txn that caused invalid cost basis
                if not self.sellTxn and not self.buyTxn and self.sharesAdded == 0L and self.costBasis == 0L: return None  # e.g. dividend - has no bearing on cost
                return self.runningCost - self.previousPos.getRunningCost()

            def isLotOverMatched(self):
                # type: () -> bool
                # Lot controlled: returns true when this buy lot is over-matched - its matched sells take more shares than it holds.
                # SCB: MD2027(5512) - fix: true only when the lot validity check ([getInvalidLotMatchSellTxns]) also flagged one of its sells. [unallottedSharesAdded]
                # alone can dip below zero by a rounding unit after an uneven split (each sell is converted back to the buy date separately), on a lot the check passes.
                # @since MD2027
                return (self.getUnallottedSharesAdded() < 0
                        and any(self.callingClass.isUnmatchedSellTxn(sellAlloc.getAllocatedPosition().getTxn()) for sellAlloc in self.getSellAllocations()))

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

            def getTxnOrTaxDate(self):
                # type: () -> int
                return self.txnOrTaxDate

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
                # Return the price of this transaction, excluding the fee if excludeFee==true
                shrsAdded = self.callingClass.secCurr.getDoubleValue(Math.abs(self.getSharesAdded()))
                txnFee = self.getFee() if (excludeFee) else 0
                return 0.0 if (shrsAdded == 0.0) else self.callingClass.investCurr.getDoubleValue(Math.abs(self.getCostBasis() - txnFee)) / shrsAdded

            def getBasisPrice(self):
                # type: () -> float
                shares = self.getSharesOwnedAsOfAsOf()
                return 0.0 if (shares == 0) else self.callingClass.investCurr.getDoubleValue(self.getRunningCost()) / self.callingClass.secCurr.getDoubleValue(shares)

        @staticmethod
        def isCostBasisValid(sec, debug=False):                                                                         # noqa
            # type: (Account, bool) -> bool
            # Validates the integrity of cost-basis lot matching for a lot-controlled Security Account.
            # Refer: [getInvalidLotMatchSellTxns] for details of validation checks performed.
            #        >> if getUnmatchedSaleLots returns null or empty, then cost basis will be valid.
            #        >> passes `failFast` parameter true. I.e. validation check stop on first error detected.
            #
            # Note: Relocated code from InvestUtil so that all 'cost basis' type code in one unified class...
            #
            # @param sec   The security account to validate.
            # @param debug enable debug messages for this validation.
            # @return true if all cost-basis validations succeed; otherwise false.
            unmatchedSaleLots = MyCostCalculation.getInvalidLotMatchSellTxns(sec=sec, txns=None, failFast=True, debug=debug)
            return unmatchedSaleLots is None or len(unmatchedSaleLots) < 1

        @staticmethod
        def isCostBasisImpactingTxnType(txnType):
            # type: (InvestTxnType) -> bool
            # Determine whether the specified txn type is one that actually impacts cost basis calculations
            # i.e. typically these do:    BUY, BUY_XFER, COVER, DIVIDEND_REINVEST, SELL, SELL_XFER, SHORT, MISCINC, MISCEXP
            #                these don't: BANK, DIVIDEND, DIVIDENDXFR
            # @param txnType The txn type to check
            # @since MD2027
            return txnType in [InvestTxnType.BUY, InvestTxnType.BUY_XFER, InvestTxnType.COVER, InvestTxnType.DIVIDEND_REINVEST,
                               InvestTxnType.SELL, InvestTxnType.SELL_XFER, InvestTxnType.SHORT, InvestTxnType.MISCINC,
                               InvestTxnType.MISCEXP]

        @staticmethod
        def deriveTxnDateRangesForTaxDates(book, accounts, taxDateRange, onlyCostImpactingTxns=True, txns=None):
            # type: (AccountBook, [Account], DateRange, bool, TxnSet) -> {Account: DateRange}
            # Derive, per account, the transaction date range covering every txn whose tax date falls within [taxDateRange].
            # Use it to widen a calculation's universe so that tax date selection can see txns dated outside the requested range.
            # Scans all of the relevant txns, so call it once, early, and only when needed.
            #
            # @param book                  The account book.
            # @param accounts              The security account(s) to consider (pass security accounts, not investment accounts).
            # @param taxDateRange          The tax date range to match txns against.
            # @param onlyCostImpactingTxns Default: `true` only considers txns that impact the cost basis. Use `false` to consider all txns found (e.g. BANK, DIVIDEND, DIVIDENDXFR)
            # @param txns                  Default: null. Specify the set of transactions to operate on.
            # @return the minimum/maximum transaction dates found per account. An account with no qualifying txn is absent from the map.
            # @since MD2027
            # Jython conversion note: the kotlin uses getTransactions(TxnSearch) when more than one account is passed. A TxnSearch written in Jython
            # is called back once per txn in the whole book (very slow), so here the book's txns are iterated directly instead - still ONE pass over
            # the book, and the same tests are applied to each txn in the loop below (which already skips txns of other accounts, as the kotlin does).
            if (accounts is None or len(accounts) == 0): return {}
            if isinstance(txns, TxnSet):
                txnSet = txns
            elif (len(accounts) == 1):
                txnSet = book.getTransactionSet().getTransactionsForAccount(list(accounts)[0])
            else:
                txnSet = book.getTransactionSet()

            # note: for/next iterators used (rather than Kotlin .filter{}.forEach{} techniques), for speed, and to avoid intermediate list creation
            minMaxByAcct = {}
            fields = InvestFields()
            for txn in txnSet:
                acct = txn.getAccount()
                if (acct not in accounts): continue
                if (not taxDateRange.containsInt(txn.getTaxDateInt())): continue
                if onlyCostImpactingTxns:
                    fields.setFieldStatus(txn.getParentTxn())
                    if (not MyCostCalculation.isCostBasisImpactingTxnType(fields.txnType)): continue
                date = txn.getDateInt()
                minMax = minMaxByAcct.get(acct)
                if (minMax is None):
                    minMax = [date, date]
                    minMaxByAcct[acct] = minMax
                if (date < minMax[0]): minMax[0] = date
                if (date > minMax[1]): minMax[1] = date
            result = {}
            for acct in minMaxByAcct:
                minMax = minMaxByAcct[acct]
                result[acct] = DateRange(Integer(minMax[0]), Integer(minMax[1]))    # Integer() wrappers needed in Jython to resolve overload ambiguity
            return result

        @staticmethod
        def getInvalidLotMatchSellTxns(sec, txns=None, failFast=False, debug=False):                                    # noqa
            # type: (Account, TxnSet, bool, bool) -> [SplitTxn]
            # Validates the integrity of cost-basis lot matching for a lot-controlled Security Account.
            # Checks performed:
            # 1. Applies only to lot-controlled securities (average cost always valid).
            # 2. Scans all investment txns for the security account to build buy/sell tables.
            #      • Buy/Sell transactions for zero shares are ignored (and not considered invalid).
            # 3. For each sell, confirms:
            #      • The sell's "cost_basis" (buy matching) parameter is valid.
            #        • computes the parsed matched-share quantity via getNumShares() - this only includes quantities where the matched buy txn actually exists.
            #        • the calculated matched qty equals the actual sell quantity (if it doesn't then txns were changed after the matching was performed).
            #      >> Then builds a table of validated matched buys for the sell being validated.
            #      >> Records each validated matched-buy quantity, in the sell's date terms together with the sell date, against its buy
            #         in an 'all valid matched buys' table. This represents every sell attempting to match each buy.
            # 4. For every matched buy in the table, verify:
            #      • The buy transaction exists.
            #      • The lot is walked forward through its matched sells in date order: before each sell, the remaining lot quantity is
            #        adjusted for splits from the previous transaction date to the sell date, then the sell quantity is deducted.
            #        A sell dated before its buy (bad data) is brought forward to the buy date instead.
            #      • The buy is over-allocated as soon as the remaining quantity becomes negative.
            #
            # @since MD2027
            #
            # @param sec      The security account to validate.
            # @param txns     Default: null. Specify the set of transactions to operate on.
            # @param failFast Defult: false. When true short-circuits the validation checks and returns after first detected error/txn.
            # @param debug    Enable debug messages for this validation.
            # @return a list of sell transactions that are not fully/properly matched to buys, causing an invalid cost basis on the security account.
            # If the result is null or empty, then the cost basis will be valid. When using [failFast] then returned results will only contain
            # the first sell transaction found to be improperly matched to buys.

            if debug: myPrint("B", "debugging MyCostCalculation::getInvalidLotMatchSellTxns for '%s' method: '%s' >> validating....."
                              %(sec, "average cost" if sec.getUsesAverageCost() else "lot control"))

            unmatchedSaleLots = LinkedHashSet()
            isValid = True

            if not sec.getUsesAverageCost():
                buyTxnIDtoSellTxnsMap = HashMap()
                curr = sec.getCurrencyType()
                buyTxnSet = TxnSet()
                sellTxnSet = TxnSet()
                # SCB: MD2027(5512) - fix: each buy lot is now validated by walking it through its matched sells in date order (validation loop below), instead of
                # converting every sell to today's terms and rounding each one separately - after a later uneven split (e.g. 1-for-3) that could make a
                # correctly matched lot total more than its buy and wrongly flag the security's cost basis invalid.
                allValidBuysList = Hashtable()      # buy txnID -> each matched sell's (date, matched shares in that sell's date terms)
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
                            # a buy / sell of zero shares is a manual cost basis adjustment - ignored here on purpose: it has no shares to match, so it cannot affect lot matching
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
                        # for each matched buy, record this sell's date and matched shares (in the sell's date terms) against the buy
                        matchedSellsList = allValidBuysList.get(txnID)
                        if matchedSellsList is None:
                            matchedSellsList = []
                            allValidBuysList.put(txnID, matchedSellsList)
                        matchedSellsList.append((stxn.getDateInt(), plusValue))

                        existingSells = buyTxnIDtoSellTxnsMap.get(txnID)
                        if existingSells is None:
                            existingSells = HashSet()
                            buyTxnIDtoSellTxnsMap.put(txnID, existingSells)
                        existingSells.add(stxn)

                # now iterate allValidBuysList (every sell matched to each buy) and validate the matched sells against the buy txn's shares
                for txnID in allValidBuysList.keySet():
                    matchedSells = allValidBuysList.get(txnID)
                    txn = TxnUtil.getTxnByID(buyTxnSet, txnID)
                    if txn is None:
                        isValid = False
                        relatedSells = buyTxnIDtoSellTxnsMap.get(txnID)
                        if relatedSells is not None:
                            for s in relatedSells: unmatchedSaleLots.add(s)
                        if debug: myPrint("B", "... txnID: '%s' from allValidBuysList not found in buyTxnSet...  result: %s" %(txnID, isValid))
                        if failFast: return list(unmatchedSaleLots)
                        continue

                    # walk the lot: start with the buy qty on the buy date; for each matched sell in date order, split-adjust the remaining qty forward to the
                    # sell date and deduct the sell. Checked after every sell - a small negative could otherwise round to zero through a later split.
                    remaining = txn.getValue()
                    remainingDate = txn.getDateInt()
                    for (sellDate, sellShares) in sorted(matchedSells, key=lambda ms: ms[0]):
                        sold = sellShares
                        if sellDate >= remainingDate:
                            remaining = curr.adjustValueForSplitsInt(remainingDate, remaining, sellDate)
                            remainingDate = sellDate
                        else:
                            # a sell dated before its matched buy only arises when a date is edited after matching (the lot matching window only offers earlier buys).
                            # The sell is brought forward to the buy date and checked normally - the lot is not flagged invalid for this alone.
                            sold = curr.adjustValueForSplitsInt(sellDate, sellShares, remainingDate)   # sell dated before its buy (bad data): bring the sell up to the buy date
                        remaining -= sold
                        if remaining < 0: break

                    # the buy is over-allocated if the walk above left the remaining qty negative
                    if remaining < 0:
                        isValid = False
                        relatedSells = buyTxnIDtoSellTxnsMap.get(txnID)
                        if relatedSells is not None:
                            for s in relatedSells: unmatchedSaleLots.add(s)
                        if debug: myPrint("B", "... txnId '%s' from allValidBuysList - txn.date: %s txn.value: %s matched sells: %s remaining: %s (at %s) result: %s"
                                          %(txnID, txn.getDateInt(), txn.getValue(), len(matchedSells), remaining, remainingDate, isValid))
                        if failFast: return list(unmatchedSaleLots)
                        continue

                    if debug: myPrint("B", "... txn.date: %s txn.value: %s matched sells: %s remaining: %s (at %s) result: %s"
                                      %(txn.getDateInt(), txn.getValue(), len(matchedSells), remaining, remainingDate, isValid))

            if debug: myPrint("B", "... result: %s" %(isValid))
            return list(unmatchedSaleLots) if (unmatchedSaleLots.size() > 0) else None
    ####################################################################################################################




    #### END EXTRA CODE HERE ####

    _extra_code_initialiser()
    myPrint("DB", "Extra Code Initialiser finished....")

except QuickAbortThisScriptException: pass
