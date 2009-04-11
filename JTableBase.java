/*
 * JTableBase.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 16, 2008
 * Time: 7:50:00 PM
 */


package com.moneydance.modules.features.findandreplace;

import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.JViewport;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableCellEditor;
import java.awt.event.MouseEvent;
import java.awt.event.MouseAdapter;
import java.awt.EventQueue;
import java.awt.AWTEvent;
import java.awt.Component;
import java.util.EventObject;

/**
 * <p>Base class of JTables with extra decoration support.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
public class JTableBase extends JTable
{
    /**
     * The decoration processor used to decorate the table.
     */
    private final TableDecorator _decorators;

    /**
     * Model of the tables components used in the adapters to gain information about the table.
     */
    private final DecoratorComponentModel _componentModel;

    /**
     * <code>true</code> if the table cells are editable <code>false</code> otherwise.
     */
    private final boolean _editable;

    /**
     * Initialize the table.
     *
     * @param editable <code>true</code> to set this table up for editing <code>false</code>
     *                 otherwise.
     */
    JTableBase( final boolean editable )
    {
        _decorators = new TableDecorator();
        _componentModel = new TableComponentModel();

        final JTableHeader header = getTableHeader();
        header.setReorderingAllowed( false );

        setShowHorizontalLines( false );
        setAutoCreateColumnsFromModel( false );
        addDecorator( new AlternateRowTableDecorator() );

        if ( editable )
        {
            // this is required if you want space bar to start
            // editing in the date column
            setSurrendersFocusOnKeystroke( true );

            // tells table to terminate cell editing when table loses focus
            // so that values can be validated
            putClientProperty( "terminateEditOnFocusLost", Boolean.TRUE );

            // add a mouse listener so that clicking on the column headers
            // stops cell editing and allows the table to validate the value
            header.addMouseListener( new HeaderMouseHandler() );
        }
        else
        {
            setSurrendersFocusOnKeystroke( false );
            putClientProperty( "terminateEditOnFocusLost", Boolean.FALSE );
        }
        _editable = editable;
    }

    /**
     * {@inheritDoc}
     *
     * @param rowIndex    {@inheritDoc}
     * @param columnIndex {@inheritDoc}
     * @param toggle      {@inheritDoc}
     * @param extend      {@inheritDoc}
     */
    @Override
    public void changeSelection( final int rowIndex,
                                 final int columnIndex,
                                 final boolean toggle,
                                 final boolean extend )
    {
        super.changeSelection( rowIndex, columnIndex, toggle, extend );

        final AWTEvent currentEvent = EventQueue.getCurrentEvent();
        if ( currentEvent instanceof MouseEvent && getEditorComponent() instanceof JTextField)
        {
            final JTextField field = (JTextField)getEditorComponent();
            field.setCaretPosition( field.getText().length() );
            field.moveCaretPosition( 0 );
        }
    }


    /**
     * Overriden to cause the table to stretch to the height of it's container.
     *
     * @return false
     */
    @Override
    public boolean getScrollableTracksViewportHeight()
    {
        if (getParent() instanceof JViewport)
        {
            return getParent().getHeight() > getPreferredSize().height;
        }
        return false;
    }

    /**
     * Programmatically starts editing the cell at <code>row</code> and <code>column</code>, if
     * those indices are in the valid range, and the cell at those indices is editable. To prevent
     * the <code>JTable</code> from editing a particular table, column or cell value, return false
     * from the <code>isCellEditable</code> method in the <code>TableModel</code> interface.
     *
     * @param row         the row to be edited
     * @param column      the column to be edited
     * @param eventObject event to pass into <code>shouldSelectCell</code>; note that as of Java 2
     *                    platform v1.2, the call to <code>shouldSelectCell</code> is no longer
     *                    made
     * @return false if for any reason the cell cannot be edited, or if the indices are invalid
     */
    @Override
    public boolean editCellAt( final int row, final int column, final EventObject eventObject )
    {
        if ( _editable )
        {
            return super.editCellAt( row, column, eventObject );
        }
        else
        {
            return false;
        }
    }

    /**
     * Add a decorator to the table.
     *
     * @param decorator The decorator to add to end of the decoration list.
     */
    final void addDecorator( final IDecorator decorator )
    {
        _decorators.addDecorator( decorator );
    }

    /**
     * Remove a decorator from the table.
     *
     * @param decorator The decorator to remove from the decoration list.
     */
    public final void removeDecorator( final IDecorator decorator )
    {
        _decorators.removeDecorator( decorator );
    }

    /**
     * {@inheritDoc}
     *
     * @param renderer {@inheritDoc}
     * @param row      {@inheritDoc}
     * @param column   {@inheritDoc}
     * @return {@inheritDoc}
     */
    @Override
    public Component prepareRenderer( final TableCellRenderer renderer,
                                      final int row,
                                      final int column )
    {
        _componentModel.row = row;
        _componentModel.column = column;
        _componentModel.editing = false;

        final Component component = super.prepareRenderer( renderer, row, column );
        return _decorators.decorate( component, _componentModel );
    }

    /**
     * {@inheritDoc}
     *
     * @param editor {@inheritDoc}
     * @param row    {@inheritDoc}
     * @param column {@inheritDoc}
     * @return {@inheritDoc}
     */
    @Override
    public Component prepareEditor( final TableCellEditor editor, final int row, final int column )
    {
        _componentModel.row = row;
        _componentModel.column = column;
        _componentModel.editing = true;

        final Component component = super.prepareEditor( editor, row, column );
        return _decorators.decorate( component, _componentModel );
    }


    /**
     * Mouse handler that stops validation when clicks are detected on the table header.
     */
    private class HeaderMouseHandler extends MouseAdapter
    {
        /**
         * {@inheritDoc}
         */
        @Override
        public void mousePressed( final MouseEvent event )
        {
            if ( isEditing() )
            {
                getCellEditor().stopCellEditing();
                getParent().requestFocus();
            }
        }
    }

    /**
     * Component model for this table instance.
     */
    private class TableComponentModel extends DecoratorComponentModel
    {
        /**
         * {@inheritDoc}
         */
        @Override
        public boolean isSelected()
        {
            return isCellSelected( row, column );
        }

    }

}
