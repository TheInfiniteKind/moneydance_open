package com.moneydance.modules.features.mrbutil;
import com.moneydance.apps.md.controller.FeatureModuleContext;
public class MRBEDTInvoke {
    public static void showURL(FeatureModuleContext context,String url){
        javax.swing.SwingUtilities.invokeLater(() ->context.showURL(url));
    }
}
