package com.moneydance.modules.features.findandreplace;

import info.clearthought.layout.TableLayoutConstraints;
import info.clearthought.layout.TableLayoutConstants;

/**
 * <p>User interface utilities and constants. </p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class UiUtil
{
    /** Horizontal gap between components/controls. */
    public static final int HGAP = 4;
    /** Vertical gap between components/controls. */
    public static final int VGAP = 3;

    /**
     * Left justified control on the bottom.
     *
     * @param col Column in the table layout.
     * @param row Row in the table layout.
     * @return An appropriate layout constraint.
     */
    @SuppressWarnings({"SameParameterValue"})
    public static TableLayoutConstraints createTableConstraintBtnL(int col, int row)
    {
        return new TableLayoutConstraints( col, row, col, row,
                TableLayoutConstants.LEFT, TableLayoutConstants.BOTTOM );
    }

    /**
     * Right justified control on the bottom.
     *
     * @param col Column in the table layout.
     * @param row Row in the table layout.
     * @return An appropriate layout constraint.
     */
    public static TableLayoutConstraints createTableConstraintBtnR(int col, int row)
    {
        return new TableLayoutConstraints( col, row, col, row,
                TableLayoutConstants.RIGHT, TableLayoutConstants.BOTTOM );
    }
}
