/*
 * DecoratorComponentModel.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 16, 2008
 * Time: 7:47:33 PM
 */


package com.moneydance.modules.features.findandreplace;

/**
 * <p>Base class for a component in a cell of a table (renderer).</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
public abstract class DecoratorComponentModel
{
    /**
     * The row we are currently working with.
     */
    int row;

    /**
     * The column we are currently working wth.
     */
    int column;

    /**
     * Is the component editable?
     */
    boolean editing;

    /**
     * Is the component selected.
     *
     * @return <code>true</code> if the component is selected, false otherwise.
     */
    @SuppressWarnings({"BooleanMethodIsAlwaysInverted"})
    public abstract boolean isSelected();

}
