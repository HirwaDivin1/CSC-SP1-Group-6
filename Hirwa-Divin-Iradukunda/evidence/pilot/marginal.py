import csv,sys,collections as C,datetime as D
csv.field_size_limit(10**7)
rows=[]
for r in csv.reader(open(sys.argv[1],newline=''),delimiter='\t'):
    if len(r)!=8: continue
    rows.append((D.datetime.fromisoformat(r[0].replace('Z','+00:00')).timestamp(),r[1],r[2],r[7]))
rows.sort()
def cross(ts,T,W):
    i=0
    for j,t in enumerate(ts):
        while t-ts[i]>W:i+=1
        if j-i+1>=T:return t
    return None
def run(rows,label):
    N=len(rows);srcs=C.defaultdict(lambda:C.defaultdict(list))
    for t,s,n,_ in rows: srcs[s][n].append(t)
    print(label,'events',N,'nodes',len({r[2] for r in rows}),'sources',len(srcs))
    delays=[0,10,60,300,3600]
    for T,W,name in [(5,600,'5/10m'),(30,1800,'30/30m'),(5,3600,'5/1h'),(10,86400,'10/24h'),(30,86400,'30/24h')]:
        none=0;local=0;shared=C.Counter();detsrc=0;multi=0;allow_undet=0
        for s,per in srcs.items():
            dets={n:cross(ts,T,W) for n,ts in per.items()}
            found=[d for d in dets.values() if d is not None]
            first=min(found) if found else None
            if first is not None:
                detsrc+=1
                if len(per)>1: multi+=1
            for n,ts in per.items():
                ld=dets[n]
                local+=sum(1 for t in ts if ld is None or t<=ld)
                for dl in delays:
                    # banned at this node from min(own detection, first+delay)
                    cut=None
                    if first is not None:
                        cut=first+dl
                        if ld is not None: cut=min(cut,ld)
                    shared[dl]+=sum(1 for t in ts if cut is None or t<=cut)
        s=' '.join(f'{dl}s:{(local-shared[dl])/local*100:.1f}%' for dl in delays)
        print(f' {name}: attempts reaching sshd with local-ban only {local} ({local/N*100:.1f}% of all); detected sources {detsrc}, on 2+ nodes {multi}; reduction by sharing vs local-only, by delay: {s}; (share of all attempts at 0s {(local-shared[0])/N*100:.1f}%)')
run(rows,'ALL')
run([r for r in rows if r[3]!='ubuntu_basic_pool'],'EXCL POOL')
