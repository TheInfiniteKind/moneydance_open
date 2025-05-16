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
 */
package com.moneydance.modules.features.securityquoteload;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import com.moneydance.modules.features.mrbutil.MRBDebug;


public class TaskExecutor
{
    ScheduledExecutorService executorService = Executors.newScheduledThreadPool(1);
    Main myTask;
    volatile boolean isStopIssued;
    MRBDebug debugInst = Main.debugInst;

    public TaskExecutor(Main myTask$) 
    {
        myTask = myTask$;

    }

    public void startExecutionAt(LocalDateTime when)
    {
		debugInst.debug("TaskExecutor", "startExecutionAt", MRBDebug.DETAILED, "when time "+when.getDayOfMonth()+"/"+when.getMonthValue()+" "+when.getHour()+":"+when.getMinute());
       Runnable taskWrapper = new Runnable(){

            @Override
            public void run() 
            {
                myTask.sendAuto();
            }

        };
        long delay = computeNextDelay(when);
        LocalTime now = LocalTime.now();
		debugInst.debug("TaskExecutor", "startExecutionAt", MRBDebug.DETAILED, "time "+now.getHour()+" "+now.getMinute());
		debugInst.debug("TaskExecutor", "startExecutionAt", MRBDebug.DETAILED, "setting run at "+when.getHour()+" "+when.getMinute());
        executorService.schedule(taskWrapper, delay, TimeUnit.SECONDS);
        now = LocalTime.now();
        
    }

    private long computeNextDelay(LocalDateTime when) 
    {
        LocalDateTime localNow = LocalDateTime.now();
        ZoneId currentZone = ZoneId.systemDefault();
        ZonedDateTime zonedNow = ZonedDateTime.of(localNow, currentZone);
        ZonedDateTime zonedNextTarget = zonedNow.withHour(when.getHour()).withMinute(when.getMinute()).withSecond(0);
        if(zonedNow.compareTo(zonedNextTarget) > 0)
            zonedNextTarget = zonedNextTarget.plusDays(1);

        Duration duration = Duration.between(zonedNow, zonedNextTarget);
        return duration.getSeconds();
    }

    public void stop()
    {
        LocalTime now = LocalTime.now();
		debugInst.debug("TaskExecutor", "stop", MRBDebug.DETAILED, "time "+now.getHour()+" "+now.getMinute());
       executorService.shutdownNow();
        try {
            executorService.awaitTermination(2, TimeUnit.MINUTES);
            LocalTime now2 = LocalTime.now();
    		debugInst.debug("TaskExecutor", "stopped", MRBDebug.DETAILED, "time "+now2.getHour()+" "+now2.getMinute());
       } catch (InterruptedException ex) {
    	   debugInst.debug("TaskExecutor", "stop", MRBDebug.DETAILED, "InterruptedException ");
			ex.printStackTrace();

        }
    }
}
