/*
 * NumericDisplay.java
 *
 * Created on Sep 18, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 *
 *
 */
package com.moneydance.modules.features.debtinsights.creditdisplay;

import java.awt.Color;

import javax.swing.SwingConstants;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.JLinkLabel;
import com.moneydance.modules.features.debtinsights.AccountUtils;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Strings;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.model.DebtAccount;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;


public abstract class NumericDisplay implements CreditLimitComponent {
    private static final String UNKNOWN = "??";

    public NumericDisplay() {
    }

    @Override
    public JLinkLabel getComponent(CreditCardViewPanel ccvp, Account acct, long balanceAmt) {
        JLinkLabel limitDisplay = new JLinkLabel(Strings.BLANK, acct, SwingConstants.RIGHT);
        Long displayAmt = null;
        String creditLimitStr = UNKNOWN;
        Util.logConsole(true, "Widget: ...Deep... In getComponent()");

        if (!acct.getAccountOrParentIsInactive()) {
//            CurrencyType relCurr = AccountUtils.getRelCurrency(acct.getCurrencyType(), acct.getParentAccount());
            displayAmt = getDisplayAmount(ccvp, acct, balanceAmt);

			if (displayAmt != null) {
			    //				displayAmt = CurrencyUtil.convertValue(displayAmt, acct.getCurrencyType(), relCurr);
                //              creditLimitStr = acct.getCurrencyType().formatFancy(displayAmt, ccvp.getDec());
                CurrencyType currToUse = Main.getWidgetValueConversionCurrencyType(acct.getCurrencyType());
                displayAmt = CurrencyUtil.convertValue(displayAmt, acct.getCurrencyType(), currToUse);
                creditLimitStr = currToUse.formatFancy(displayAmt, ccvp.getDec());
				if (displayAmt < 0L) {
					Color negFGColor = ccvp.getCcAccountView().getMDGUI().getColors().negativeBalFG;
					limitDisplay.setForeground(negFGColor);
				}

                if (displayAmt > 0 && Main.getWidgetEnhancedColors()) {
                    switch (ccvp.getCreditLimitType()) {
                        case AVAILABLE_CREDIT:
                        case CREDIT_LIMIT: {
                            limitDisplay.setForeground(Util.getPositiveGreen());
                        }
                    }
                }
				Util.logConsole(true, "@@@ getBalanceType: " + ccvp.getBalanceType()
                        + " derivedBT: "
                        + Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType()
                        + " getCreditLimitType: "
                        + ccvp.getCreditLimitType()
                        + " calculation: "
                        + displayAmt);
            }
        }
		if (displayAmt == null) {
			Color grayFGColor = ccvp.getCcAccountView().getMDGUI().getColors().secondaryTextFG;
			limitDisplay.setForeground(grayFGColor);
		}
        limitDisplay.setText(creditLimitStr);
        return limitDisplay;
    }

    protected abstract Long getDisplayAmount(CreditCardViewPanel ccvp, Account acct, long balanceAmt);

}
