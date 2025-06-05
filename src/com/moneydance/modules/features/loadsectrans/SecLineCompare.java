/* 
 * Copyright (c) 2014, Michael Bray. All rights reserved.
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
 */ 
package com.moneydance.modules.features.loadsectrans;

import java.util.Comparator;

public class SecLineCompare implements Comparator<SecLine> {
	@Override
	public int compare(SecLine scLine1, SecLine scLine2) {
		Integer iDate1 = scLine1.getDate();
		Integer iDate2 = scLine2.getDate();
		Long lValue1 = scLine1.getValue();
		Long lValue2 = scLine2.getValue();
		int iCompare = iDate2.compareTo(iDate1);
		if (iCompare != 0)
			return iCompare;
		iCompare = lValue1.compareTo(lValue2);
		if (iCompare != 0)
			return iCompare;
		iCompare = scLine1.getTranType().compareTo(scLine2.getTranType());
		if (iCompare != 0)
			return iCompare;
		if (scLine1.getAccount() == null)
			return iCompare;
		if (scLine2.getAccount() == null)
			return iCompare;
		iCompare = scLine1.getAccount().getAccountName().compareTo(scLine2.getAccount().getAccountName());
		return iCompare;
		
	}
}
