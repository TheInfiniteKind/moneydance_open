/*
 * AccountSelectDialog.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 6, 2008
 * Time: 5:53:32 AM
 */


package com.moneydance.modules.features.findandreplace;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;

import javax.swing.JDialog;
import javax.swing.JButton;
import javax.swing.JPanel;
import javax.swing.BorderFactory;
import javax.swing.WindowConstants;
import javax.swing.JOptionPane;
import java.awt.Frame;
import java.awt.BorderLayout;
import java.awt.Dialog;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

import com.moneydance.apps.md.model.RootAccount;

/**
 * <p>Dialog that allows the user to select one or more accounts or categories.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class AccountSelectDialog extends JDialog
{
    private final AccountSelectModel _model;
    private final AccountSelectController _controller;
    private final AccountSelectView _view;
    private final IResourceProvider _resources;

    private int _result;

    /**
     * Creates a modeless dialog with the specified title and
     * with the specified owner frame.  If <code>owner</code>
     * is <code>null</code>, a shared, hidden frame will be set as the
     * owner of the dialog.
     * <p/>
     * This constructor sets the component's locale property to the value
     * returned by <code>JComponent.getDefaultLocale</code>.
     * <p/>
     * NOTE: This constructor does not allow you to create an unowned
     * <code>JDialog</code>. To create an unowned <code>JDialog</code>
     * you must use either the <code>JDialog(Window)</code> or
     * <code>JDialog(Dialog)</code> constructor with an argument of
     * <code>null</code>.
     *
     * @param owner     The <code>Frame</code> from which the dialog is displayed
     * @param resources Internationalization resource provider.
     * @param data      Root account providing access to all data.
     * @param filter    Filter for the types of accounts managed by the dialog.
     * @throws java.awt.HeadlessException if <code>GraphicsEnvironment.isHeadless()</code>
     *                                    returns <code>true</code>.
     * @see java.awt.GraphicsEnvironment#isHeadless
     * @see javax.swing.JComponent#getDefaultLocale
     */
    public AccountSelectDialog(Frame owner, IResourceProvider resources, RootAccount data,
                               AccountFilter filter)
    {
        // this will be modal
        super(owner, resources.getString(L10NFindAndReplace.ACCOUNTSELECT_TITLE),
                Dialog.ModalityType.APPLICATION_MODAL);

        _model = new AccountSelectModel(data, filter, resources);
        _view = new AccountSelectView(_model);
        _controller = new AccountSelectController(_model, resources);
        _view.setController(_controller);
        _resources = resources;

        // hook up listeners
        _model.addPropertyChangeListener(_view);

        buildMainPanel();

        // this is a temporary dialog, but we need to get the result of the dialog
        _result = JOptionPane.CANCEL_OPTION;
        setDefaultCloseOperation(WindowConstants.HIDE_ON_CLOSE);
    }


    void loadData()
    {
        try
        {
            _model.refresh();
        }
        catch (Exception error)
        {
            _view.handleException(error);
        }

    }

    int getResult()
    {
        return _result;
    }

    void cleanUp()
    {
        // avoid the lapsed listener problem
        _model.removePropertyChangeListener(_view);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void buildMainPanel()
    {
        _view.layoutUI();

        // for convenience, setLayout() and add() are overridden to go to the content pane
        setLayout(new BorderLayout());

        add(_view, BorderLayout.CENTER);
        add(buildButtonPanel(), BorderLayout.SOUTH);
    }

    private JPanel buildButtonPanel()
    {
        final double[][] sizes = new double[][]
                {
                        // columns
                        {
                                TableLayout.FILL, // space (buttons right justified)
                                TableLayout.PREFERRED, // ok
                                UiUtil.HGAP, // gap
                                TableLayout.PREFERRED, // cancel
                        },

                        // rows
                        {TableLayout.PREFERRED}
                };
        final JPanel buttonPanel = new JPanel(new TableLayout(sizes));

        JButton ok = new JButton(_resources.getString(L10NFindAndReplace.OK));
        buttonPanel.add(ok, new TableLayoutConstraints(1, 0));
        ok.addActionListener(new ActionListener()
        {
            public void actionPerformed(ActionEvent e)
            {
                onOk();
            }
        });

        JButton cancel = new JButton(_resources.getString(L10NFindAndReplace.CANCEL));
        buttonPanel.add(cancel, new TableLayoutConstraints(3, 0));
        cancel.addActionListener(new ActionListener()
        {
            public void actionPerformed(ActionEvent e)
            {
                onCancel();
            }
        });

        // pad it a little
        buttonPanel.setBorder(BorderFactory.createEmptyBorder(UiUtil.VGAP, UiUtil.HGAP,
                UiUtil.VGAP, UiUtil.HGAP));

        return buttonPanel;
    }

    private void onOk()
    {
        _controller.apply();
        _result = JOptionPane.OK_OPTION;
        setVisible(false);
    }

    private void onCancel()
    {
        _result = JOptionPane.CANCEL_OPTION;
        setVisible(false);
    }

}
