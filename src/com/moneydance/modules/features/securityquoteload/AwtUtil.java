package com.moneydance.modules.features.securityquoteload;

import javax.swing.*;
import java.awt.event.InputEvent;
import java.awt.event.MouseEvent;
import com.moneydance.util.Platform;

public class AwtUtil {

  public static boolean isPopupTrigger(InputEvent event) {
    int modifiers = event.getModifiersEx();

    if (event.getID() == MouseEvent.MOUSE_RELEASED && event instanceof MouseEvent mouseEvent) {

      // Right or middle button clicks
      if ((modifiers & (InputEvent.BUTTON2_DOWN_MASK | InputEvent.BUTTON3_DOWN_MASK)) != 0) {
        return true;
      }

      // Mac control-click
      if (Platform.isMac() && mouseEvent.isControlDown()) {
        return true;
      }

      if (mouseEvent.isPopupTrigger()) return true;

      if (SwingUtilities.isRightMouseButton(mouseEvent)) return true;
    }

    return false;
  }

}
