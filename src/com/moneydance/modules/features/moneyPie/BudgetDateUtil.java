/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;

public class BudgetDateUtil {

        /**
         * Return the start of the week. Must give what the first day of week is
         * @param dt Date
         * @param startDayOfWeek eg Calendar.MONDAY
         * @return
         */
        public static Date getStartOfWeek(Date dt,int startDayOfWeek) {
                if (dt == null)
                        return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);
                gc.set(Calendar.DAY_OF_WEEK, startDayOfWeek);
                gc.set(Calendar.HOUR_OF_DAY, 0);
                gc.set(Calendar.MINUTE, 0);
                gc.set(Calendar.SECOND, 0);
                gc.set(Calendar.MILLISECOND, 0);
                return gc.getTime();
        }

        /**
         * Return the first day of the month from the Date given Hour, minutes,
         * seconds are set to 0:00:00
         *
         * @return
         */
        public static Date getStartOfMonth(Date dt) {
                if (dt == null)
                        return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);
                gc.set(Calendar.DAY_OF_MONTH, 1);
                gc.set(Calendar.HOUR_OF_DAY, 0);
                gc.set(Calendar.MINUTE, 0);
                gc.set(Calendar.SECOND, 0);
                gc.set(Calendar.MILLISECOND, 0);
                return gc.getTime();
        }

        public static int getMonthEndDay(int year, int month){
      	  int endDay = 31;
            switch (month) {
      	      case 1: endDay = 31; break;
      	      case 2: endDay = 28; break;
      	      case 3: endDay = 31; break;
      	      case 4: endDay = 30; break;
      	      case 5: endDay = 31; break;
      	      case 6: endDay = 30; break;
      	      case 7: endDay = 31; break;
      	      case 8: endDay = 31; break;
      	      case 9: endDay = 30; break;
      	      case 10: endDay = 31; break;
      	      case 11: endDay = 30; break;
      	      case 12: endDay = 31; break;
      	      default: endDay = 31;
      	  }

            if( (year % 4) == 0 && month == 2 ) endDay = 29;

            return endDay;
        }

        /**
         * Return the first day of the year from the Date given. Hour,
         * minutes, seconds are set to 0:00:00
         *
         * @return
         */
        public static Date getStartOfYear(Date dt) {
                if (dt == null)
                        return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);
                gc.set(Calendar.MONTH, 0);
                gc.setTime(getStartOfMonth(gc.getTime()));

                return gc.getTime();
        }

        /**
         * Return the first day of the set quarter from the Date given. Hour, minutes,
         * seconds are set to 0:00:00 ie Either Jan, April, July or October
         *
         * @return
         */
        public static Date getStartOfQuarter(Date dt) {
                if (dt == null)
                        return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);

                int thisMonth = gc.get(Calendar.MONTH);
                switch (thisMonth) {
                        case Calendar.JANUARY:
                        case Calendar.FEBRUARY:
                        case Calendar.MARCH:
                                gc.set(Calendar.MONTH, Calendar.JANUARY);
                                break;
                        case Calendar.APRIL:
                        case Calendar.MAY:
                        case Calendar.JUNE:
                                gc.set(Calendar.MONTH, Calendar.APRIL);
                                break;
                        case Calendar.JULY:
                        case Calendar.AUGUST:
                        case Calendar.SEPTEMBER:
                                gc.set(Calendar.MONTH, Calendar.JULY);
                                break;
                        case Calendar.OCTOBER:
                        case Calendar.NOVEMBER:
                        case Calendar.DECEMBER:
                                gc.set(Calendar.MONTH, Calendar.OCTOBER);
                                break;
                        default:
                                break;
                }
                gc.setTime(getStartOfMonth(gc.getTime()));

                return gc.getTime();
        }

    /** Return the End of week (last day of week)
     *  Hour, minutes, seconds are set to 23:59:59
         * @param startDayOfWeek eg Calendar.MONDAY
     * @return
     */
    public static Date getEndOfWeek(Date dt,int startOfWeek)
    {
        if (dt == null) return null;
        GregorianCalendar gc = new GregorianCalendar();
        gc.setTime(getStartOfWeek(dt,startOfWeek));
        // Add 6 days
        gc.add(Calendar.DATE,6);
        gc.set(Calendar.HOUR_OF_DAY,23);
        gc.set(Calendar.MINUTE,59);
        gc.set(Calendar.SECOND,59);
        gc.set(Calendar.MILLISECOND,999);
        return gc.getTime();
    }

    /** Return the End (last day of year) of the given Date
     *  Hour, minutes, seconds are set to 23:59:59
     * @return
     */
    public static Date getEndOfMonth(Date dt)
    {
        if (dt == null) return null;
        GregorianCalendar gc = new GregorianCalendar();
        gc.setTime(getStartOfMonth(dt));
        // Add a month
        gc.add(Calendar.MONTH,1);
        // Take a day for last of of month
        gc.add(Calendar.DATE,-1);
        gc.set(Calendar.HOUR_OF_DAY,23);
        gc.set(Calendar.MINUTE,59);
        gc.set(Calendar.SECOND,59);
        gc.set(Calendar.MILLISECOND,999);
        return gc.getTime();
    }

    /** Return the End of year (last day of month & year)
     *  Hour, minutes, seconds are set to 23:59:59
     * @return
     */
    public static Date getEndOfYear(Date dt)
    {
        if (dt == null) return null;
        GregorianCalendar gc = new GregorianCalendar();
        gc.setTime(getStartOfYear(dt));
        // Last month
        gc.set(Calendar.MONTH,11);
        gc.setTime(getEndOfMonth(gc.getTime()));
        return gc.getTime();
    }

        /**
         * Return the last day of the set quarter from the Date given.
         *  Hour, minutes, seconds are set to 23:59:59
         *
         * @return
         */
        public static Date getEndOfQuarter(Date dt) {
                if (dt == null)
                        return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);

                Calendar cal = Calendar.getInstance();

                int thisMonth = gc.get(cal.get(Calendar.MONTH));
                switch (thisMonth) {
                        case Calendar.JANUARY:
                        case Calendar.FEBRUARY:
                        case Calendar.MARCH:
                                gc.set(Calendar.MONTH, Calendar.MARCH);
                                break;
                        case Calendar.APRIL:
                        case Calendar.MAY:
                        case Calendar.JUNE:
                                gc.set(Calendar.MONTH, Calendar.JUNE);
                                break;
                        case Calendar.JULY:
                        case Calendar.AUGUST:
                        case Calendar.SEPTEMBER:
                                gc.set(Calendar.MONTH, Calendar.SEPTEMBER);
                                break;
                        case Calendar.OCTOBER:
                        case Calendar.NOVEMBER:
                        case Calendar.DECEMBER:
                                gc.set(Calendar.MONTH, Calendar.DECEMBER);
                                break;
                        default:
                                break;
                }
                gc.setTime(getEndOfMonth(gc.getTime()));

                return gc.getTime();
        }

        /** Add a number of days to the given day. Can be a negative number.
         * @param dt
         * @param numDays Number of days to add/subtract.
         * @return
         */
        public static Date addDays(Date dt, int numDays)
        {
                if (dt == null) return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);
                // add one day to this day
                gc.add(Calendar.DATE,numDays);
                return gc.getTime();
        }

        /** Add a number of weeks to the given day. Can be a negative number.
         * @param dt
         * @param numWeeks Number of weeks to add/subtract.
         * @return
         */
        public static Date addWeeks(Date dt, int numWeeks)
        {
                if (dt == null) return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);
                // add one week to this day
                gc.add(Calendar.DATE,numWeeks * 7);
                return gc.getTime();
        }

        /** Add a number of months to the given day. Can be a negative number.
         * @param dt
         * @param numMonths Number of months to add/subtract.
         * @return
         */
        public static Date addMonths(Date dt, int numMonths)
        {
                if (dt == null) return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);
                // add one day to this day
                gc.add(Calendar.MONTH,numMonths);
                return gc.getTime();
        }

        /** Add a number of quarters to the given day. Can be a negative number.
         * @param dt
         * @param numQuarters Number of quarters to add/subtract.
         * @return
         */
        public static Date addQuarters(Date dt, int numQuarters)
        {
                if (dt == null) return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);
                // add one day to this day
                gc.add(Calendar.MONTH,numQuarters*3);
                return gc.getTime();
        }

        /** Add a number of years to the given day. Can be a negative number.
         * @param dt
         * @param numMonths Number of years to add/subtract.
         * @return
         */
        public static Date addYears(Date dt, int numYears)
        {
                if (dt == null) return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);
                // add one day to this day
                gc.add(Calendar.YEAR,numYears);
                return gc.getTime();
        }

    /** Returns true if the Dates are in the same day. Ignores time.
     * @param d1 Day one compared to
     * @param d2 Day two
     * @return
     */
    public static boolean isInSameDay(Date d1, Date d2)
        {
        if (d1 == null || d2 == null)
        {
                return false;
        }

        GregorianCalendar cal1 = new GregorianCalendar();
        cal1.setTime(d1);
        GregorianCalendar cal2 = new GregorianCalendar();
        cal2.setTime(d2);

        return (cal1.get(Calendar.DATE) == cal2.get(Calendar.DATE) &&
                cal1.get(Calendar.MONTH) == cal2.get(Calendar.MONTH) &&
                        cal1.get(Calendar.YEAR) == cal2.get(Calendar.YEAR));
    }

    public static boolean isInSameDayOrAfter(Date d1, Date d2) {
        if (d1 == null || d2 == null) return false;

        if (isInSameDay(d1,d2) || d1.after(d2)) return true;
        return false;
    }
    public static boolean isInSameDayOrBefore(Date d1, Date d2) {
        if (d1 == null || d2 == null) return false;

        if (isInSameDay(d1,d2) || d1.before(d2)) return true;
        return false;
    }

    /**
     * Is the date given in date range
     * @param myDate Date to compare
     * @param dateStart Range Start Date
     * @param dateEnd Range End Date
     * @return
     */
    public static boolean isInRange(Date myDate, Date dateStart, Date dateEnd) {
        return isInSameDayOrAfter(myDate, dateStart) && isInSameDayOrBefore(myDate, dateEnd);
    }

    public static String getStrDate(Date date) {
   	 Calendar c = Calendar.getInstance();
   	 c.setTime(date);

   	 int m = c.get(GregorianCalendar.MONTH) + 1;
   	 int d = c.get(GregorianCalendar.DATE);
   	 String mm = Integer.toString(m);
   	 String dd = Integer.toString(d);
   	 return "" + c.get(GregorianCalendar.YEAR) + (m < 10 ? "0" + mm : mm) +
   	     (d < 10 ? "0" + dd : dd);
   }

    public static long getLngDate(Date date) {
    	return (new Long(getStrDate(date))).longValue();
    }

    public static long getLngDateTime(Date date) {
    	//return (new Long(getStrDate(date))).longValue();
    	return date.getTime();
    }

    /**
     * Get date from form YYYYMMDD
     * @param date
     * @return
     */
        public static Date getDateYYYYMMDD(int ymd) {
                int day = ymd % 100;
                int d = ymd / 100;
                int month = d % 100;
                d = d / 100;
                int year = d;
                return getDate(year,month,day);
        }

        /** Return a Date with the year, month, day given
         * @param year Year in form yyyy
         * @param month Month from [1..12]
         * @param day Day of month
         * @return
         */
        public static Date getDate(int year, int month, int day) {
                GregorianCalendar gc = new GregorianCalendar(year,month-1,day);
                return gc.getTime();
        }

        /**
         * Does it have the same day and month of the year
         * @param dt1
         * @param dt2
         * @return
         */
        public static boolean isSameDayOfYear(Date dt1, Date dt2) {
                if (dt1 == null || dt2 == null) return false;
                GregorianCalendar gc1 = new GregorianCalendar();
                gc1.setTime(dt1);
                GregorianCalendar gc2 = new GregorianCalendar();
                gc2.setTime(dt2);

                if (gc1.get(Calendar.DAY_OF_MONTH) == gc2.get(Calendar.DAY_OF_MONTH) &&
                        gc1.get(Calendar.MONTH) == gc2.get(Calendar.MONTH)) {
                        return true;
                }

                return false;
        }

        /**
         * Does it have the same day of month
         * @param dt1
         * @param dt2
         * @return
         */
        public static boolean isSameDayOfMonth(Date dt1, Date dt2) {
                if (dt1 == null || dt2 == null) return false;
                GregorianCalendar gc1 = new GregorianCalendar();
                gc1.setTime(dt1);
                GregorianCalendar gc2 = new GregorianCalendar();
                gc2.setTime(dt2);

                return (gc1.get(Calendar.DAY_OF_MONTH) == gc2.get(Calendar.DAY_OF_MONTH));
        }

        /**
         * Set the time to zero 00:00:00
         * @param dt
         * @return
         */
        public static Date setTimeZero(Date dt) {
                if (dt == null)
                        return null;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);
                gc.set(Calendar.HOUR_OF_DAY, 0);
                gc.set(Calendar.MINUTE, 0);
                gc.set(Calendar.SECOND, 0);
                gc.set(Calendar.MILLISECOND, 0);
                return gc.getTime();
        }

        public static int getQuarterNum(Date dt) {
                if (dt == null)
                        return 0;
                GregorianCalendar gc = new GregorianCalendar();
                gc.setTime(dt);

                int thisMonth = gc.get(Calendar.MONTH);

                return thisMonth / 4 + 1;
        }

}
