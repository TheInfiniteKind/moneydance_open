/*
 * Copyright (c) 2018, Michael Bray.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 * This source is based on the work done by Hung Le the author of the hleofxquotes program.
 * 
 */	
package com.moneydance.modules.features.securityquoteload;

import java.awt.Component;

import javax.swing.JOptionPane;

// TODO: Auto-generated Javadoc
/**
 * The Class ShowDialogTask.
 */
public class ShowDialogTask implements Runnable {
    
    /** The parent component. */
    private final Component parentComponent;

    /** The message. */
    private String message;

    /** The title. */
    private String title;

    /** The message type. */
    private int messageType;

    /**
     * Instantiates a new show dialog task.
     *
     * @param parentComponent the parent component
     * @param message the message
     * @param title the title
     * @param messageType the message type
     */
    public ShowDialogTask(Component parentComponent, String message, String title, int messageType) {
        super();
        this.parentComponent = parentComponent;
        this.message = message;
        this.title = title;
        this.messageType = messageType;
    }

    /**
     * Instantiates a new show dialog task.
     *
     * @param parentComponent the parent component
     * @param exception the exception
     * @param messageType the message type
     */
    public ShowDialogTask(Component parentComponent, Exception exception, int messageType) {
        this(parentComponent, exception.toString(), exception.getClass().getName(), messageType);
    }

    /* (non-Javadoc)
     * @see java.lang.Runnable#run()
     */
    @Override
    public void run() {
        JOptionPane.showMessageDialog(parentComponent, message, title, messageType);
    }
}