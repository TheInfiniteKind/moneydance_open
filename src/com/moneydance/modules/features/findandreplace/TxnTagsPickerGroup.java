package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.model.RootAccount;

import javax.swing.JPanel;
import javax.swing.JLabel;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;

import java.awt.event.ActionListener;

/**
 * <p>Two pickers, one 'include tags' and one 'exclude tags', combined.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.1
 * @since 1.0
 */
class TxnTagsPickerGroup extends JPanel
{
    private final TxnTagsPicker _include;
    private final TxnTagsPicker _exclude;

    /**
     * Constructor with needed information to create the view
     * @param mdGui GUI controller for Moneydance
     * @param data Datafile
     * @param controller Localization resources
     */
    TxnTagsPickerGroup(final MoneydanceGUI mdGui, final RootAccount data,
                       final FarController controller)
    {
        _include = new TxnTagsPicker(mdGui, data);
        _exclude = new TxnTagsPicker(mdGui, data);
        layoutUI(controller);
    }

    TxnTagsPicker getIncludePicker()
    {
        return _include;
    }

    TxnTagsPicker getExcludePicker()
    {
        return _exclude;
    }

    void updateFromView()
    {
        _include.updateFromView();
        _exclude.updateFromView();
    }

    void addSelectionListener(final ActionListener changeListener)
    {
        _include.getView().addSelectionListener(changeListener);
        _exclude.getView().addSelectionListener(changeListener);
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void layoutUI(final IResourceProvider resources)
    {
        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.FILL,      // include
                UiUtil.HGAP,
                TableLayout.PREFERRED, // text
                UiUtil.HGAP,
                TableLayout.FILL,      // exclude
            },

            // rows
            { TableLayout.PREFERRED }
        };

        setLayout(new TableLayout(sizes));

        // adding the 'exclude' list unnecessarily complicates the interface so for now it is
        // simply not shown
        add(_include.getView(),  new TableLayoutConstraints( 0, 0, 4, 0 ));
//        add(_include.getView(),  new TableLayoutConstraints( 0, 0 ));
//        final JLabel label = new JLabel(resources.getString(L10NFindAndReplace.FIND_NOT));
//        add(label, new TableLayoutConstraints( 2, 0 ));
//        add(_exclude.getView(), new TableLayoutConstraints( 4, 0 ));
    }
}
