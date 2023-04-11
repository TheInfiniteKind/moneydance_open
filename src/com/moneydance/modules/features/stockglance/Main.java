// Main.java
//
// Copyright (c) 2015-2021, James Larus
//  All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//  1. Redistributions of source code must retain the above copyright
//  notice, this list of conditions and the following disclaimer.
//
//  2. Redistributions in binary form must reproduce the above copyright
//  notice, this list of conditions and the following disclaimer in the
//  documentation and/or other materials provided with the distribution.
//
//  3. Neither the name of the copyright holder nor the names of its
//  contributors may be used to endorse or promote products derived from
//  this software without specific prior written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
//  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
//  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
//  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
//  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
//  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
//  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
//  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
//  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
//  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
//  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

package com.moneydance.modules.features.stockglance;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;


/**
 * Home page component to display active stock prices and returns.
 */

public class Main extends FeatureModule {
    private StockGlance glance;

    @Override
    public void init() {
        try {
            FeatureModuleContext context = getContext();
            MoneydanceGUI mdGUI = (MoneydanceGUI)((com.moneydance.apps.md.controller.Main) context).getUI();
            glance = new StockGlance(mdGUI);
            getContext().registerHomePageView(this, glance);
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }
    }

    public void invoke(String uri) {
        glance.refresh();
    }

    public String getName() {
        return "Stock Glance";
    }

    @Override
    public void cleanup() {
        glance.reset();
        glance = null;
    }

    @Override
    public void unload() {
        cleanup();
    }
}