package com.moneydance.modules.features.debtinsights.ui;

import com.moneydance.modules.features.debtinsights.Util;
import javax.swing.SwingUtilities;

//  Copies: com.moneydance.awt.CollapsibleRefresher
//  Class that enables easy collapsible refreshing.  That is, if you expect to receive a lot of updates
//  to a data model that the UI can't keep up with, you can use this to enqueue a Runnable that will
//  refresh your UI that won't queue up more than one Runnable on the swing event dispatch thread.
//
//  Multiple .enqueue()s will get ignored.... The first gets pushed to the EDT via .invokeLater()
//  EXCEPT: Where an enqueued job has started on the EDT, then the next enqueued will get pushed onto the Queue

public class MyCollapsibleRefresher {
    private boolean isPendingRefresh;
    private final Runnable refreshable;
    private final Runnable queueableRefresher = new Runnable() {
        public void run() {
            Util.logConsole(true, "Inside MyCollapsibleRefresher::queueableRefresher.... Calling MyCollapsibleRefresher.refreshable.run()");
            MyCollapsibleRefresher.this.isPendingRefresh = false;
            MyCollapsibleRefresher.this.refreshable.run();
        }
    };

    public MyCollapsibleRefresher(Runnable refreshable) {
        Util.logConsole(true, "Initialising MyCollapsibleRefresher....");
        this.isPendingRefresh = false;
        this.refreshable = refreshable;
    }

    public void enqueueRefresh() {
        Util.logConsole(true, "Inside MyCollapsibleRefresher.enqueueRefresh()");
        if (this.isPendingRefresh) {
            Util.logConsole(true, "... DISCARDING enqueueRefresh request as one is already pending...");
            return;
        }

        Util.logConsole(true, "... REQUESTING .invokeLater()");
        this.isPendingRefresh = true;
        SwingUtilities.invokeLater(this.queueableRefresher);

    }



}










