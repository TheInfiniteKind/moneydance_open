package com.moneydance.modules.features.loadsectrans;

import com.infinitekind.moneydance.model.Account;

public class NodeEntry{
    private Account account;
    private String entry;
    public NodeEntry(Account account, String entry){
        this.account = account;
        this.entry = entry;
    }

    public Account getAccount() {
        return account;
    }

    public void setAccount(Account account) {
        this.account = account;
    }

    public String getEntry() {
        return entry;
    }

    public void setEntry(String entry) {
        this.entry = entry;
    }

}
