"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const script=fs.readFileSync(path.join(__dirname,"../chrome-extension/content.js"),"utf8");
function start(valid){
  const v={listeners:0,disconnects:0,tick:null,clears:0,pending:0};
  const chrome={runtime: valid?{id:"test",onMessage:{addListener(){v.listeners++;}},
    sendMessage(_,cb){v.pending++;if(cb)cb({pending:null});}}:undefined};
  vm.runInNewContext(script,{
    chrome,MutationObserver:class {observe(){}disconnect(){v.disconnects++;}},
    document:{documentElement:{},querySelectorAll(){return[];}},
    window:{location:{search:""}},URLSearchParams,
    setInterval(fn){v.tick=fn;return 5;},clearInterval(){v.clears++;},
    setTimeout(){return 6;},console,Node:{ELEMENT_NODE:1}
  },{filename:"content.js"});
  return{chrome,v};
}
test("missing runtime does not register onMessage",()=>{
  const {v}=start(false);
  assert.equal(v.listeners,0);assert.equal(v.pending,0);
  assert.equal(v.tick,null);assert.equal(v.disconnects,1);
});
test("updated extension stops stale content script retry polling",async()=>{
  const {chrome,v}=start(true);
  assert.equal(v.listeners,1);assert.ok(v.tick);
  chrome.runtime=undefined;
  await v.tick();
  assert.equal(v.clears,1);assert.equal(v.disconnects,1);
});
test("normal registration still starts recovery poll",()=>{
  const {v}=start(true);
  assert.equal(v.listeners,1);assert.equal(v.pending,1);
});
