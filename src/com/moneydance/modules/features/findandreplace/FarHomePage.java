package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.view.gui.MoneydanceLAF;

import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.JButton;
import javax.swing.JLabel;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;

/**
 * <p>The view for the home page. The home page just has a title, free text field and a
 * Find button.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class FarHomePage extends JPanel
{
    private RootAccount _data;
    private JLabel _title;
    private JTextField _freeText;
    private JButton _find;
    private final Main _feature;

    public FarHomePage(final RootAccount rootAccount, final Main feature)
    {
        _data = rootAccount;
        _feature = feature;
        createControls();
    }

    public void layoutUI()
    {
        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.FILL, // Text box
                UiUtil.HGAP,
                TableLayout.PREFERRED // button
            },

            // rows -- Label with the text box and the find button
            {
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED
            }
        };

        setLayout(new TableLayout(sizes));
        setOpaque(false);
        setBorder(MoneydanceLAF.homePageBorder);

        add(_title, new TableLayoutConstraints(0, 0, 2, 0));
        add(_freeText, new TableLayoutConstraints(0, 2));
        add(_find, new TableLayoutConstraints(2, 2));
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    //  Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void createControls()
    {
        _title = new JLabel(_feature.getFarController().getString(L10NFindAndReplace.TITLE));
        _title.setOpaque(false);

        _freeText = new JTextField();
        _find = new JButton(_feature.getFarController().getString(L10NFindAndReplace.FIND_BUTTON_TEXT));
        String mnemonic = _feature.getFarController().getString(L10NFindAndReplace.FIND_BUTTON_MNC);
        _find.setMnemonic( mnemonic.charAt( 0 ) );
        
        // add listeners
        _freeText.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _find.doClick();
            }
        });
        _find.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                if (_feature != null)
                {
                    _data = _feature.getFarController().getMDMain().getRootAccount();
                    _feature.getFarController().loadData(_data);
                    _feature.getFarController().setInitialFreeText(_freeText.getText());
                    _feature.getFarController().show();
                }
            }
        });
    }

    public void refresh()
    {
        // reload text from resources
        _title.setText(_feature.getFarController().getString(L10NFindAndReplace.TITLE));
        _find.setText(_feature.getFarController().getString(L10NFindAndReplace.FIND_BUTTON_TEXT));
        String mnemonic = _feature.getFarController().getString(L10NFindAndReplace.FIND_BUTTON_MNC);
        _find.setMnemonic( mnemonic.charAt( 0 ) );
    }
}
