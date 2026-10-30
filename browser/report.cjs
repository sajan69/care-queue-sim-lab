const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const dir=path.resolve(__dirname,'../artifacts');
(async()=>{
 const b=await chromium.launch({headless:true,args:['--no-sandbox'],...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
 const p=await b.newPage({viewport:{width:1280,height:900}}),problems=[],requests=[],checks=[];
 p.on('pageerror',e=>problems.push(e.message));
 p.on('dialog',async d=>{problems.push('dialog');await d.dismiss()});
 p.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 try{
 await p.goto(pathToFileURL(path.join(dir,'report.html')).href);
 assert.match(await p.locator('h1').innerText(),/completed requests/);
 assert.match(await p.locator('.warning').innerText(),/Not hospital data/);
 assert.match(await p.locator('body').innerText(),/-343\.39/);
 assert.equal(await p.locator('progress').count(),2);assert.equal(await p.locator('table').count(),2);
 assert.match(await p.locator('body').innerText(),/late capacity minus early capacity/);
 checks.push('computed cohorts, paired differences and synthetic-use warning');
 await p.locator('summary').click();assert.match(await p.locator('pre').innerText(),/workload_sha256/);
 checks.push('expandable experiment provenance');
 await p.screenshot({path:path.join(dir,'desktop.png'),fullPage:true});
 await p.setViewportSize({width:390,height:844});
 assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 assert(await p.locator('.scroll').first().evaluate(e=>e.scrollWidth>e.clientWidth));
 await p.screenshot({path:path.join(dir,'mobile.png'),fullPage:true});
 checks.push('390px body fit and scrollable metric tables');
 await p.goto(pathToFileURL(path.join(dir,'probe.html')).href);
 assert.equal(await p.locator('img,script').count(),0);assert.match(await p.locator('body').innerText(),/<img/);
 assert.equal(problems.length,0);assert.equal(requests.length,0);
 checks.push('inert HTML payload with no network, dialogs or page errors');
 fs.writeFileSync(path.join(dir,'browser-checks.json'),JSON.stringify({passed:checks.length,checks,browser:b.version()},null,2));
 for(const c of checks)console.log('Passed: '+c);
 }catch(e){await p.screenshot({path:path.join(dir,'failure.png'),fullPage:true});throw e}
 finally{await b.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
