import gzip,json,sys,csv,glob
inp,out=sys.argv[1],sys.argv[2]
w=csv.writer(open(out,'w'),delimiter='\t')
ev=0
def handle(sess_events):
    global ev
    h=None;v=None
    for e in sess_events:
        if e.get('hassh'): h=e['hassh']
        if e.get('eventid')=='cowrie.client.version': v=e.get('message','')
    for e in sess_events:
        if e.get('eventid') in('cowrie.login.failed','cowrie.login.success'):
            ev+=1
            w.writerow([e['timestamp'],e['src_ip_identifier'][:16],e['dst_host_identifier'][:16],e['eventid'][13:],e.get('username'),e.get('password'),h or '',(e.get('sensor') or '')])
for fn in sorted(glob.glob(inp+'/*.json.gz')):
    dec=json.JSONDecoder()
    with gzip.open(fn,'rt',errors='replace') as f:
        for line in f:
            s=line.strip().rstrip(',')
            if s.startswith('['): s=s[1:]
            if s.endswith(']') and s.count('[')<s.count(']'): s=s[:-1]
            if not s: continue
            try: d=json.loads(s)
            except Exception:
                sys.stderr.write('bad line %s %r\n'%(fn,s[:80])); continue
            for k,v in d.items():
                handle(v)
print('logins',ev)
