package com.moneydance.modules.features.reportwriter.view;
import com.moneydance.modules.features.mrbutil.MRBPlatform;

import javax.swing.*;

public class SwingAccelerator {
        private KeyStroke deleteKey;
        private KeyStroke openKey;
        private KeyStroke saveKey;
        private KeyStroke closeKey1;
        private KeyStroke closeKey2;
        private KeyStroke closeKey3;
        private KeyStroke newKey;
        public SwingAccelerator() {
            deleteKey =KeyStroke.getKeyStroke('D',java.awt.event.InputEvent.META_DOWN_MASK);
            openKey = KeyStroke.getKeyStroke('O',java.awt.event.InputEvent.META_DOWN_MASK);
            saveKey = KeyStroke.getKeyStroke('S',java.awt.event.InputEvent.META_DOWN_MASK);
            newKey = KeyStroke.getKeyStroke('N',java.awt.event.InputEvent.META_DOWN_MASK);
            closeKey1 = KeyStroke.getKeyStroke('W',java.awt.event.InputEvent.CTRL_DOWN_MASK);
            closeKey2 = KeyStroke.getKeyStroke("F4");
            closeKey3 = KeyStroke.getKeyStroke("ESCAPE");

        }
        public void setSceneDelete(JComponent object, Action rn) {
            object.getInputMap().put(deleteKey, "delete");
            object.getActionMap().put("delete",rn);
        }
        public void setSceneOpen(JComponent object, Action rn) {
            object.getInputMap().put(openKey, "open");
            object.getActionMap().put("open",rn);
        }
        public void setSceneSave(JComponent object, Action rn) {
            object.getInputMap().put(saveKey, "save");
            object.getActionMap().put("save",rn);
       }
        public void setSceneNew(JComponent object, Action rn) {
            object.getInputMap().put(newKey, "new");
            object.getActionMap().put("new",rn);
        }
        public void setSceneClose(JComponent object, Action rn) {
            object.getInputMap().put(closeKey1, "close");
            object.getInputMap().put(closeKey2, "close");
            if (MRBPlatform.isWindows())
                object.getInputMap().put(closeKey3, "close");
            object.getActionMap().put("close",rn);
        }
}
