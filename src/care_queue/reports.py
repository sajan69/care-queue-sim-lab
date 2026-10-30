"""Static aggregate views; no browser scripts, network assets or imports."""
import csv
import html
import io
import json

STYLE='''body{font:16px system-ui,sans-serif;background:#f3f6f8;color:#183242;margin:0}main{max-width:1050px;margin:auto;padding:32px 20px}h1{font-size:2.3rem;line-height:1.15}h2{margin-top:0}p,li{line-height:1.6}article,.warning{padding:22px;background:white;border:1px solid #d8e2e6;border-radius:12px;margin:20px 0}.warning{background:#fff7e8;border-left:5px solid #b37a21}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:650px}th,td{padding:12px;border-bottom:1px solid #d8e2e6;text-align:right}th:first-child,td:first-child{text-align:left}th{background:#eaf1f3}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.8rem}.bar{height:15px;background:#157c83;min-width:1px;margin-top:5px}.eyebrow{color:#157c83;font-weight:700;letter-spacing:.06em}summary{cursor:pointer;font-weight:600}@media(max-width:500px){main{padding:20px 12px}h1{font-size:1.85rem}article{padding:12px}}'''
LABELS={'restricted_wait_mean':'Restricted wait / all arrivals (min)', 'waiting':'Still waiting at cutoff',
        'completed':'Completed by cutoff','busy_server_minutes':'Busy resource minutes'}


def esc(x):return html.escape(str(x),quote=True)


def html_report(report):
    import base64,hashlib,statistics
    token=base64.b64encode(hashlib.sha256(STYLE.encode()).digest()).decode()
    c=report['configuration'];rows=''
    for key,value in report['summaries'].items():
        lo,hi=value['bootstrap_95_percentile']
        rows+=f'<tr><td>{esc(LABELS[key])}</td><td>{value["pairs"]}</td><td>{value["mean_difference"]:+,.2f}</td><td>{lo:+,.2f} to {hi:+,.2f}</td></tr>'
    cohorts=''
    for policy in report['policy_order']:
        ms=[pair['policies'][policy]['metrics'] for pair in report['pairs']]
        avg=lambda key:statistics.fmean(m[key] for m in ms)
        cohorts+=f'<tr><td>{esc(policy)}</td><td>{avg("arrived"):.0f}</td><td>{avg("completed"):.2f}</td><td>{avg("in_service"):.2f}</td><td>{avg("waiting"):.2f}</td><td>{avg("restricted_wait_mean"):.1f}</td><td>{avg("available_server_minutes"):.0f}</td></tr>'
    bars=''.join(f'<p>{esc(p)}<br><progress max="{c["requests_per_replication"]}" value="{sum(pair["policies"][p]["metrics"]["waiting"] for pair in report["pairs"])/len(report["pairs"]):.3f}"></progress> mean requests still waiting: {sum(pair["policies"][p]["metrics"]["waiting"] for pair in report["pairs"])/len(report["pairs"]):.1f}</p>' for p in report['policy_order'])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'sha256-{token}'; base-uri 'none'; form-action 'none'"><meta name="referrer" content="no-referrer"><title>Care Queue | Synthetic experiments</title><style>{STYLE}</style></head><body><main><p class="eyebrow">SYNTHETIC QUEUE RESEARCH</p><h1>Compare waiting, not just completed requests</h1><p>{esc(c['scenario'])} · {c['replications']} paired replications · {c['requests_per_replication']} requests per replication · {c['days']} generated days</p><div class="warning"><strong>Not hospital data.</strong> These experiments are not calibrated to real services and do not recommend staffing, clinical priorities or individual decisions.</div><article><h2>Unfinished work remains visible</h2>{bars}<div class="scroll"><table><thead><tr><th>Capacity pattern</th><th>Arrived</th><th>Completed</th><th>In service</th><th>Waiting</th><th>Restricted wait / arrival</th><th>Available minutes</th></tr></thead><tbody>{cohorts}</tbody></table></div><p>Table entries are rounded replication means. Completed + in service + waiting equals arrived. Restricted waiting exposure includes observed waiting for every arrival; it is censored at cutoff and is not ultimate mean wait.</p></article><article><h2>Paired differences</h2><p>Direction: late capacity minus early capacity. Both calendars have the same resource budget; each pair shares identical arrivals and service durations.</p><div class="scroll"><table><thead><tr><th>Metric</th><th>Pairs</th><th>Mean difference</th><th>Approximate 95% bootstrap interval</th></tr></thead><tbody>{rows}</tbody></table></div><p>Intervals resample paired replication differences. They describe Monte Carlo variability under the fixed scenario, not predictive uncertainty about a real health system.</p></article><article><h2>Interpretation limits</h2><ul>{''.join('<li>'+esc(w)+'</li>' for w in report['warnings'])}</ul></article><details><summary>Configuration, provenance and method</summary><pre>{esc(json.dumps({k:report[k] for k in ('configuration','workload_sha256','environment','method')},indent=2))}</pre></details></main></body></html>'''


def csv_report(report):
    out=io.StringIO(newline='');w=csv.writer(out,quoting=csv.QUOTE_ALL)
    w.writerow(['metric','pairs','late_minus_early_mean','bootstrap95_lower','bootstrap95_upper','scenario','workload_sha256','synthetic','interpretation'])
    for metric,s in report['summaries'].items():
        w.writerow([metric,s['pairs'],s['mean_difference'],*s['bootstrap_95_percentile'],report['configuration']['scenario'],report['workload_sha256'],True,'Finite synthetic experiment; not real-world waiting or clinical advice'])
    return out.getvalue()
