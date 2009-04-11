package com.moneydance.modules.features.findandreplace;


import javax.swing.DefaultRowSorter;
import java.util.Comparator;

/**
 * <p>Table to hold the results of the find operation.</p>
 * <p><b>Note:</b> DefaultRowSorter and some of the other stuff used is new in Java 1.6, so this
 * class is one of the reasons why 1.6 is required for Find and Replace.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class FindResultsTable extends JTableBase
{
    /**
     * Initialize the table.
     * @param model Table model for the table
     */
    public FindResultsTable(final FindResultsTableModel model)
    {
        super(true); // some fields are editable, others are not

        setModel(model);
        setRowSorter(new FindResultsRowSorter(model));
    }

    private class FindResultsRowSorter extends DefaultRowSorter<FindResultsTableModel, FindResultsTableEntry>
    {
        FindResultsRowSorter(final FindResultsTableModel model)
        {
            setModelWrapper(new FindResultsModelWrapper(model));
            setComparator(FindResultsTableModel.AMOUNT_INDEX, new AmountComparator());
            setComparator(FindResultsTableModel.DATE_INDEX, new DateComparator());
        }
        
        private class FindResultsModelWrapper extends
                DefaultRowSorter.ModelWrapper<FindResultsTableModel, FindResultsTableEntry>
        {
            final FindResultsTableModel _model;
            FindResultsModelWrapper(final FindResultsTableModel model)
            {
                _model = model;
            }
            public FindResultsTableModel getModel()
            {
                return _model;
            }

            public int getColumnCount()
            {
                return _model.getColumnCount();
            }

            public int getRowCount()
            {
                return _model.getRowCount();
            }

            public Object getValueAt(int row, int column)
            {
                // we don't want to compare with strings, we want to compare with the value
                if (column == FindResultsTableModel.AMOUNT_INDEX)
                {
                    return Long.valueOf(_model.getAmount(row));
                }
                if (column == FindResultsTableModel.DATE_INDEX)
                {
                    return Integer.valueOf(_model.getDateInt(row));
                }
                return _model.getValueAt(row, column);
            }

            public FindResultsTableEntry getIdentifier(int row)
            {
                return _model.getEntry(row);
            }
        }
    } // class FindResultsRowSorter

    private class AmountComparator implements Comparator<Long>
    {
        public int compare(Long o1, Long o2)
        {
            return o1.compareTo(o2);
        }
    }
    private class DateComparator implements Comparator<Integer>
    {
        public int compare(Integer o1, Integer o2)
        {
            return o1.compareTo(o2);
        }
    }

}
