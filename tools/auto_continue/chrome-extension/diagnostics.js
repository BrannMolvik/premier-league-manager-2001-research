"use strict";
const button=document.getElementById("refresh");
const summary=document.getElementById("summary");
const checks=document.getElementById("checks");
const details=document.getElementById("details");
const checked=document.getElementById("checked");
async function run(){
  button.disabled=true;summary.textContent="Checking Chrome, GitHub and the worker tab...";
  try{
    const data=await chrome.runtime.sendMessage({type:"fm2001-diagnostics"});
    if(!data?.ok)throw new Error(data?.error||"No response from extension");
    const r=data.report;checked.textContent="Checked: "+r.checkedAt;
    summary.textContent=r.summary;checks.replaceChildren();
    for(const item of r.checks){
      const li=document.createElement("li");li.className=item.ok?"pass":"fail";
      li.textContent=(item.ok?"PASS: ":"FAIL: ")+item.name+(item.detail?" — "+item.detail:"");
      checks.appendChild(li);
    }
    details.textContent=JSON.stringify({
      runtimeStatus:r.runtimeStatus,runtimeEnabled:r.runtimeEnabled,
      workerTabId:r.workerTabId,workerGenerating:r.workerGenerating,
      workerHeartbeat:r.workerHeartbeat,workerStaleMinutes:r.workerStaleMinutes,
      lastRecoveryAt:r.lastRecoveryAt,recoveryPermitted:r.recoveryPermitted,
      pendingRecovery:r.pendingRecovery,recentExtensionError:r.recentExtensionError
    },null,2);
  }catch(error){summary.textContent="Diagnostics failed: "+String(error);}
  finally{button.disabled=false;}
}
button.addEventListener("click",run);run();
