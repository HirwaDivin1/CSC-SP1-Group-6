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
    print(label)
    for T,W,name in [(5,3600,'5/1h'),(10,86400,'10/24h'),(30,86400,'30/24h')]:
        local=0;sh=C.Counter();elig=C.Counter()
        for s,per in srcs.items():
            dets={n:cross(ts,T,W) for n,ts in per.items()}
            found=sorted(d for d in dets.values() if d is not None)
            for k in (1,2,3):
                if len(found)>=k: elig[k]+=1
            for n,ts in per.items():
                ld=dets[n]
                local+=sum(1 for t in ts if ld is None or t<=ld)
                for k in (1,2,3):
                    cut=found[k-1] if len(found)>=k else None
                    if ld is not None: cut=ld if cut is None else min(cut,ld)
                    sh[k]+=sum(1 for t in ts if cut is None or t<=cut)
        print(' ',name,'reduction vs local-only:',' '.join(f'k={k}:{(local-sh[k])/local*100:.1f}% ({elig[k]} srcs)' for k in (1,2,3)))
run(rows,'ALL 33 nodes')
run([r for r in rows if r[3]!='ubuntu_basic_pool'],'EXCL POOL 5 nodes')
print('sensors',C.Counter(r[3] for r in rows).most_common(6))
