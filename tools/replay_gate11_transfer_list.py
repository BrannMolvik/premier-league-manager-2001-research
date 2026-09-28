from __future__ import annotations
import struct, datetime, math
from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import os
from collections import Counter,defaultdict
parser=argparse.ArgumentParser(description="Replay FM2001 fresh transfer-list population RNG.")
parser.add_argument("--game-dir", default=os.environ.get("FM2001_GAME_DIR"), help="Directory containing Master.dat, Static.dat, English.str and Core.str")
parser.add_argument("--limit", type=int, default=40, help="Number of reverse club visits to replay (default: 40)")
parser.add_argument("--mode", choices=("scaled","modulo"), default="scaled", help="Bounded RNG mapping; modulo is diagnostic only")
parser.add_argument("--summary-only", action="store_true", help="Suppress per-visit JSON output")
parser.add_argument("--validate-prefix", action="store_true", help="Validate known 40-visit prefix for the selected mode")
parser.add_argument("--loan-tail", action="store_true", help="Replay the canonical fresh post-transfer loan-list tail through the 200-player cap")
ARGS=parser.parse_args()
if not ARGS.game_dir:
 raise SystemExit("--game-dir or FM2001_GAME_DIR is required")
BASE=Path(ARGS.game_dir)
def game_file(name):
 p=BASE/name
 if p.exists(): return p
 matches=[x for x in BASE.iterdir() if x.name.lower()==name.lower()]
 if len(matches)!=1: raise FileNotFoundError(name)
 return matches[0]
MASTER=game_file('Master.dat').read_bytes(); STATIC=game_file('Static.dat').read_bytes()

def load_strings(path):
 d=Path(path).read_bytes(); table,count=struct.unpack_from('<II',d,0); offs=struct.unpack_from(f'<{count}I',d,table+8); out=[]
 for rel in offs:
  p=8+rel
  if p>=table+8: out.append(''); continue
  e=d.find(b'\0',p,table+8); e=table+8 if e<0 else e
  out.append(d[p:e].decode('cp1252','replace'))
 return out
ENG=load_strings(game_file('English.str')); CORE=load_strings(game_file('Core.str'))
OLE=datetime.date(1899,12,30); CURRENT=datetime.date(2000,7,4); CURRENT_SERIAL=(CURRENT-OLE).days

def odate(n):
 try:return OLE+datetime.timedelta(days=n)
 except:return None

@dataclass
class Club:
 id:int; name:str; manager:int; country:int; category:int; fan_index:int
@dataclass
class Manager:
 id:int; name:str; club:int|None; forms:tuple[int,int,int]
@dataclass
class Player:
 id:int; name:str; club:int; flags:int; dob:int; pos:tuple[int,int,int]; skills:tuple[int,...]; join:int; special:int

# parse master
cc=struct.unpack_from('<I',MASTER,0)[0]; CS=181; co=4
clubs=[]
for i in range(cc):
 r=MASTER[co+i*CS:co+(i+1)*CS]; sid=struct.unpack_from('<H',r,4)[0]
 clubs.append(Club(i,ENG[sid],struct.unpack_from('<I',r,48)[0],struct.unpack_from('<I',r,12)[0],r[98],struct.unpack_from('<I',r,94)[0]))
pend=co+cc*CS; pc=struct.unpack_from('<I',MASTER,pend)[0]; PS=103; po=pend+4
players=[]; rosters=defaultdict(list)
for i in range(pc):
 r=MASTER[po+i*PS:po+(i+1)*PS]; pid,fn,ln,cid=struct.unpack_from('<HHHH',r,0)
 p=Player(pid,(CORE[fn]+' '+CORE[ln]).strip(),cid,struct.unpack_from('<I',r,10)[0],struct.unpack_from('<I',r,14)[0],tuple(r[21:24]),tuple(r[24:41]),struct.unpack_from('<I',r,76)[0],struct.unpack_from('<i',r,88)[0])
 players.append(p); rosters[cid].append(pid)
player_by_id={p.id:p for p in players}
p_end=po+pc*PS; mc=struct.unpack_from('<I',MASTER,p_end)[0]; MS=43; mo=p_end+4
managers=[]
for i in range(mc):
 r=MASTER[mo+i*MS:mo+(i+1)*MS]; fn,ln=struct.unpack_from('<HH',r,4); clubraw=struct.unpack_from('<I',r,27)[0]
 managers.append(Manager(i,(CORE[fn]+' '+CORE[ln]).strip(),None if clubraw==0xffffffff else clubraw,(r[24],r[25],r[26])))
# static countries European index
country_count=struct.unpack_from('<I',STATIC,0x4a)[0]; countries={}
for i in range(country_count):
 r=STATIC[0x4e+i*43:0x4e+(i+1)*43]; countries[struct.unpack_from('<I',r,0)[0]]={'euro':struct.unpack_from('<H',r,14)[0]}
# positions lineup groups
pos_count=struct.unpack_from('<I',STATIC,0x25e0)[0]; pos_group={}
for i in range(pos_count):
 r=STATIC[0x25e4+i*7:0x25e4+(i+1)*7]; pos_group[r[0]]=r[6]
# fan bases
fb_count=struct.unpack_from('<I',STATIC,0x13c95)[0]; fan48=[]
for i in range(fb_count):
 r=STATIC[0x13c99+i*78:0x13c99+(i+1)*78]
 # 17 packed dwords after id? file +2..?? parser says packed dword #17 = file +66
 fan48.append(struct.unpack_from('<I',r,66)[0])

# exact role weights and compatibility
W={
1:((1,.3),(14,.4),(0,.2),(5,.1),(11,.7),(12,.7),(13,.9)),2:((1,.3),(14,.5),(0,.5),(8,.4),(6,.1),(5,.6),(7,.9)),3:((1,.3),(14,.5),(0,.5),(8,.4),(6,.1),(5,.6),(7,.9)),4:((1,.3),(14,.5),(0,.5),(8,.6),(6,.1),(5,.4),(7,.9)),5:((1,.3),(14,.4),(0,.5),(8,.3),(6,.2),(5,.7),(7,.9)),6:((1,.3),(14,.4),(0,.6),(8,.2),(6,.3),(5,.7),(7,.8)),7:((1,.3),(14,.4),(0,.6),(8,.2),(6,.3),(5,.7),(7,.8)),8:((1,.3),(14,.4),(0,.4),(8,.5),(6,.2),(5,.6),(7,.9)),9:((1,.3),(14,.3),(0,.3),(8,.5),(6,.3),(5,.9),(7,.7)),10:((1,.3),(14,.3),(0,.4),(8,.5),(6,.3),(5,.9),(7,.6)),11:((1,.3),(14,.3),(0,.4),(8,.5),(6,.3),(5,.9),(7,.6)),12:((1,.3),(14,.3),(0,.4),(8,.5),(6,.3),(5,.9),(7,.6)),13:((1,.3),(14,.4),(0,.7),(8,.2),(6,.5),(5,.8),(7,.4)),14:((1,.3),(14,.4),(0,.7),(8,.2),(6,.5),(5,.8),(7,.4)),15:((1,.3),(14,.4),(0,.4),(8,.4),(6,.6),(5,.8),(7,.4)),18:((1,.3),(14,.4),(0,.5),(8,.5),(6,.9),(5,.5),(7,.2)),19:((1,.3),(14,.5),(0,.6),(8,.6),(6,.9),(5,.2),(7,.2))}
def disp(x): return (30*x+128)//255
def compat(role,ps):
 S=set(ps)
 if role in S:return 1.0
 if role==1:return .10
 if role==2:return .90 if S&{6,4} else (.75 if S&{7,3} else .50)
 if role==3:return .90 if S&{7,4} else (.75 if S&{2,6} else .50)
 if role==4:return .90 if S&{2,3,5} else .50
 if role==5:return .90 if 4 in S else (.75 if S&{2,3} else .50)
 if role==6:return .90 if 2 in S else (.75 if S&{3,7} else .50)
 if role==7:return .90 if 3 in S else (.75 if S&{2,6} else .50)
 if role in (8,9):return .90 if S&{8,9,10,11,12} else (.80 if S&{4,5} else .50)
 if role==10:return .85 if 13 in S else (.70 if 11 in S else (.80 if S&{12,9,15} else .50))
 if role==11:return .85 if 14 in S else (.70 if 10 in S else (.80 if S&{12,9,15} else .50))
 if role==12:return .90 if S&{9,10,11,15} else (.80 if 4 in S else .50)
 if role==13:return .80 if 10 in S else (.70 if 14 in S else .50)
 if role==14:return .80 if 11 in S else (.70 if 13 in S else .50)
 if role==15:return .90 if S&{9,10,11,12} else (.75 if S&{18,19} else .50)
 if role in (16,17):return .50
 if role in (18,19):return .90 if S&{18,19} else (.75 if S&{15,12,11} else .50)
 return .50
def role_rating(p,role):
 if role not in W:return 0
 v=sum(disp(p.skills[i])*w for i,w in W[role])*compat(role,p.pos)
 return int(min(v,99.0)+.49)
def best_rating(p):return max((role_rating(p,r) for r in p.pos if r),default=0)

# exact 21 formation role templates
F=[
(19,19,11,10,12,12,4,4,3,2,1),(19,19,14,13,9,9,4,4,3,2,1),(18,18,11,10,9,9,4,4,3,2,1),(19,19,15,12,12,7,6,4,4,4,1),(19,19,18,12,12,7,6,4,4,4,1),(18,18,12,12,9,7,6,4,4,4,1),(19,19,18,11,10,9,9,4,4,4,1),(19,19,18,14,13,12,12,4,4,4,1),(19,18,18,11,10,9,9,4,4,4,1),(19,19,14,13,12,12,9,4,4,4,1),(19,19,18,14,13,9,9,4,4,4,1),(19,19,15,11,10,9,9,4,4,4,1),(19,19,18,12,12,8,7,6,4,4,1),(19,19,18,15,15,12,7,6,4,4,1),(19,14,13,12,12,8,4,4,3,2,1),(18,15,15,11,10,8,4,4,3,2,1),(19,19,18,15,15,14,13,9,4,4,1),(18,15,15,11,10,5,4,4,3,2,1),(19,19,14,13,12,12,4,4,3,2,1),(19,19,15,12,12,7,6,5,4,4,1),(19,18,18,15,12,12,4,4,3,2,1)]

class RNG:
 def __init__(self,s,mode='scaled'): self.state=s&0xffffffff; self.log=[]; self.mode=mode
 def rand15(self):
  self.state=(self.state*0x343fd+0x269ec3)&0xffffffff; return (self.state>>16)&0x7fff
 def draw(self,b,label=''):
  raw=self.rand15(); b=int(b); v=((raw*b)//32768 if self.mode=='scaled' else raw%b); self.log.append((label,b,v,raw,self.state)); return v

# exact qsort ratio special keys
special={257:0.960813673436702,196:0.964986144313222,212:0.965667451667081,256:0.993094744577438,391:0.996253483716185,331:0.997707747535481,572:1.001184026457622,156:1.007371177945545}
def cmpclub(a,b):
 x=special.get(a,1.0); y=special.get(b,1.0); return -1 if x<y else (1 if x>y else 0)
def shortsort(a,lo,hi):
 while hi>lo:
  mx=lo
  for p in range(lo+1,hi+1):
   if cmpclub(a[p],a[mx])>0:mx=p
  a[mx],a[hi]=a[hi],a[mx];hi-=1
def qsort(a):
 if len(a)<2:return
 stack=[];lo=0;hi=len(a)-1
 while True:
  if hi-lo+1<=8:
   shortsort(a,lo,hi)
   if not stack:return
   lo,hi=stack.pop();continue
  mid=lo+(hi-lo+1)//2;a[mid],a[lo]=a[lo],a[mid];i=lo;j=hi+1
  while True:
   i+=1
   while i<=hi and cmpclub(a[i],a[lo])<=0:i+=1
   j-=1
   while j>lo and cmpclub(a[j],a[lo])>=0:j-=1
   if j>=i:a[i],a[j]=a[j],a[i];continue
   break
  a[lo],a[j]=a[j],a[lo]
  L=j-lo;R=hi-i+1
  if L>=R:
   if lo<j-1:stack.append((lo,j-1))
   if i<hi:lo=i;continue
  else:
   if i<hi:stack.append((i,hi))
   if lo<j-1:hi=j-1;continue
  if not stack:return
  lo,hi=stack.pop()

def qsort_cmp(a,cmp):
 if len(a)<2:return
 def short(lo,hi):
  while hi>lo:
   mx=lo
   for p in range(lo+1,hi+1):
    if cmp(a[p],a[mx])>0:mx=p
   a[mx],a[hi]=a[hi],a[mx];hi-=1
 stack=[];lo=0;hi=len(a)-1
 while True:
  if hi-lo+1<=8:
   short(lo,hi)
   if not stack:return
   lo,hi=stack.pop();continue
  mid=lo+(hi-lo+1)//2;a[mid],a[lo]=a[lo],a[mid];i=lo;j=hi+1
  while True:
   i+=1
   while i<=hi and cmp(a[i],a[lo])<=0:i+=1
   j-=1
   while j>lo and cmp(a[j],a[lo])>=0:j-=1
   if j>=i:a[i],a[j]=a[j],a[i];continue
   break
  a[lo],a[j]=a[j],a[lo]
  L=j-lo;R=hi-i+1
  if L>=R:
   if lo<j-1:stack.append((lo,j-1))
   if i<hi:lo=i;continue
  else:
   if i<hi:stack.append((i,hi))
   if lo<j-1:hi=j-1;continue
  if not stack:return
  lo,hi=stack.pop()

def eligible_club(c):
 if c.id==0 or c.name=='FREE TRANSFER' or c.name.startswith('!') or c.category in (2,3):return False
 if c.manager<0 or c.manager>=len(managers):return False
 m=managers[c.manager]
 if m.club is None:return False
 if c.country not in countries or countries[c.country]['euro']<=0:return False
 return True
arr=[c.id for c in clubs if eligible_club(c)]; assert len(arr)==895
qsort(arr); rng=RNG(0xDFCED283,ARGS.mode)
for _pass in range(2):
 for rem in range(len(arr),1,-1):
  k=rng.draw(rem,'shuffle'); arr[k],arr[rem-1]=arr[rem-1],arr[k]
assert rng.state==0xBD5CC00F
visits=list(reversed(arr[1:]))

# fresh state helpers
transfer_listed=set(p.id for p in players if (p.flags>>8)&1)
loan_listed=set()
def runtime_flags(p): return p.flags | ((1<<8) if p.id in transfer_listed else 0) | ((1<<12) if p.id in loan_listed else 0)
def effective_roster_count(cid):
 n=0
 for pid in rosters[cid]:
  fl=runtime_flags(player_by_id[pid])
  # 405080 excludes bits 8,0,6,1
  if fl & ((1<<8)|(1<<0)|(1<<6)|(1<<1)):continue
  n+=1
 return n
def threshold(cid): return fan48[clubs[cid].fan_index]-4

def completed_weeks(p):
 # Proven startup sentinel handling: source 1950 join date is replaced by current-200 days.
 jd=odate(p.join)
 if jd is None:return 9999
 if jd.year==1950: days=200
 else: days=(CURRENT-jd).days
 return math.trunc(days/7)

def final_club_ok(cid):
 # Fresh tracker: +08 initial roster count, +0c/+0e zero; no roster movement in population loop.
 return True

def eligibility(p,rng,why=None):
 fl=runtime_flags(p)
 # active/current club == registered club in fresh ordinary source roster
 # mode 0 rejects bits 8,0,12,10,4; bit1 has special immediate false path too
 if fl & ((1<<8)|(1<<0)|(1<<12)|(1<<10)|(1<<4)|(1<<1)):
  return False,('flags',hex(fl))
 if completed_weeks(p)<26:return False,('weeks',completed_weeks(p),odate(p.join))
 if p.special>-1:return False,('special',p.special)
 br=best_rating(p); roll=None
 if br>=70:passed=True
 elif br>=61: roll=rng.draw(100,'rating');passed=roll>=50
 elif br>=51: roll=rng.draw(100,'rating');passed=roll>=33
 else: roll=rng.draw(100,'rating');passed=roll>=25
 if not passed:return False,('rating-fail',br,roll)
 if not final_club_ok(p.club):return False,('club-final',)
 return True,('ok',br,roll)

def pool_players(cid):
 out=[]
 for pid in rosters[cid]:
  p=player_by_id[pid];fl=runtime_flags(p)
  if fl & ((1<<8)|(1<<9)|(1<<6)|(1<<12)|(1<<13)):continue
  out.append(p)
 return out

def positional(cid,rng):
 if cid==0:return None,{'exit':'user'}
 if len(rosters[cid])<=threshold(cid):return None,{'exit':'threshold','roster':len(rosters[cid]),'th':threshold(cid)}
 pool=pool_players(cid)
 if len(pool)<18:return None,{'exit':'pool<18','pool':len(pool)}
 m=managers[clubs[cid].manager]
 demand=[0]*20
 for f in m.forms:
  if 0<=f<len(F):
   for role in F[f]: demand[role]+=1
 supply=[0]*20
 # 61A790 calls identical supply accumulator three times
 for p in rosters[cid]:
  pl=player_by_id[p]
  for j,role in enumerate(pl.pos):
   if role:supply[role]+=3*(role_rating(pl,role)//(j+1))
 # 61A900
 selected=-1; zero_best=0; ratio_best=0.0
 for role in range(20):
  d=demand[role];s=supply[role]
  if d:
   if zero_best:continue
   ratio=s/d
   # exact FPU comparison updates on >=? research says strict greater; use > to preserve lower role ties
   if ratio>ratio_best: ratio_best=ratio;selected=role
  else:
   if s>zero_best:selected=role;zero_best=s
 if selected<0:return None,{'exit':'no-role','demand':demand,'supply':supply}
 entries=[]
 for p in pool:
  for j,role in enumerate(p.pos):
   if role==selected: entries.append(p.id); break
 def rolecmp(pa,pb):
  a=player_by_id[pa]; b=player_by_id[pb]
  ia=next((j for j,r in enumerate(a.pos) if r==selected),-1); ib=next((j for j,r in enumerate(b.pos) if r==selected),-1)
  if ia>ib:return 1
  if ia<ib:return -1
  ra=role_rating(a,selected); rb=role_rating(b,selected)
  if ra<rb:return 1
  if ra>rb:return -1
  return 0
 qsort_cmp(entries,rolecmp)
 if not entries:return None,{'exit':'empty-role','role':selected}
 p=player_by_id[entries[0]]
 # fresh 41EE60 numerator zero => first role-vector entry
 g=pos_group.get(p.pos[0],255); mins=(4,5,5,2)
 cnt=sum(1 for pid in rosters[cid] if pos_group.get(player_by_id[pid].pos[0],255)==g)
 if g>=4 or cnt<mins[g]:return None,{'exit':'group','role':selected,'candidate':p.id,'group':g,'count':cnt}
 ok,why=eligibility(p,rng)
 return (p if ok else None),{'role':selected,'candidate':p.id,'candidate_name':p.name,'best':best_rating(p),'selected_role_rating':role_rating(p,selected),'why':why,'group':g,'group_count':cnt,'zero_best':zero_best,'ratio_best':ratio_best,'pool':len(pool)}

def randomsel(cid,rng):
 if cid==0:return None,{'exit':'user'}
 ec=effective_roster_count(cid);th=threshold(cid)
 if ec<=th:return None,{'exit':'threshold','effective':ec,'th':th}
 roster=rosters[cid];atts=[]
 for attempt in range(20):
  branch=rng.draw(10,'random-branch')
  if branch<3:
   draw=rng.draw(len(roster)-1,'random-index-a');idx=1+draw
  else:
   draw=rng.draw(len(roster)-11,'random-index-b');idx=11+draw
  p=player_by_id[roster[idx]];ok,why=eligibility(p,rng)
  atts.append({'attempt':attempt+1,'branch':branch,'bound':(len(roster)-1 if branch<3 else len(roster)-11),'draw':draw,'idx':idx,'pid':p.id,'name':p.name,'best':best_rating(p),'why':why})
  if ok:return p,{'effective':ec,'th':th,'attempts':atts}
 return None,{'effective':ec,'th':th,'attempts':atts,'exit':'20'}

def replay(n=20,verbose=True):
 global transfer_listed
 # reset mutations to source flags only
 transfer_listed=set(p.id for p in players if (p.flags>>8)&1)
 r=RNG(0xBD5CC00F,ARGS.mode); out=[]
 for vi,cid in enumerate(visits[:n],1):
  before=r.state;dispatch=r.draw(10,'dispatch')
  if dispatch<7:p,detail=positional(cid,r);kind='pos'
  else:p,detail=randomsel(cid,r);kind='rand'
  if p:transfer_listed.add(p.id)
  rec={'visit':vi,'club':cid,'clubname':clubs[cid].name,'before':before,'dispatch':dispatch,'kind':kind,'selected':None if p is None else p.id,'selected_name':None if p is None else p.name,'state':r.state,'detail':detail}
  out.append(rec)
  if verbose: print(rec)
 return out,r

SCALED_FIRST40_CLUBS=(118,750,510,1216,430,622,877,243,404,500,717,597,616,842,413,89,822,804,484,1,470,215,818,680,213,165,23,237,630,144,549,556,780,496,145,173,103,803,538,620)
SCALED_FIRST40_STATES=(0x6A346701,0x7B490815,0xF0AD5F37,0x0C123F69,0x7302C488,0x86F7B742,0xABE8BCA6,0x047A80D1,0x79B832E5,0x80BA6087,0x7FCFCB39,0x145D6118,0x3081B852,0x1850595C,0x4FD812B6,0x458226E0,0x9405EC5A,0xCCF96DA4,0xD8E7093E,0x651BA9FF,0x97342071,0x60EBD638,0x2C98D672,0x20DD687C,0xEE729AD6,0x4554FE7A,0x1F9E10C4,0x5675C55E,0x5701AEC8,0xD8E3EE0C,0x96AFCCE6,0x5DFB3290,0x4E46D58A,0xC71FD16E,0xD1A29B58,0x8E9AC492,0xE32BC79C,0x5D58F2F6,0xBFA0E09A,0x1EBAE4F5)
MODULO_FIRST40_CLUBS=(805,610,140,862,362,757,507,214,611,166,867,698,399,68,209,234,779,719,1211,232,79,742,775,624,409,118,681,23,179,67,643,514,664,469,131,761,355,248,662,740)
MODULO_FIRST40_STATES=(0x6A346701,0x31D39583,0xF0AD5F37,0x7647CFCC,0xABE8BCA6,0xFF61A050,0x6076B14A,0x1931DA14,0x2130592E,0x458226E0,0x9405EC5A,0xCCF96DA4,0xA11011A8,0x969F09CB,0x98446D62,0xAC8D5E9D,0x97342071,0x03BB2D4E,0x60EBD638,0x2C98D672,0x20DD687C,0xEE729AD6,0xBFBDF000,0x4554FE7A,0x1F9E10C4,0x5675C55E,0x5701AEC8,0xF117F382,0x37534713,0x8E9AC492,0x5D58F2F6,0xBFA0E09A,0xF7A603E4,0xFA5F9BE8,0x633A49A2,0xB695F52C,0xD8570D06,0xDE6973B0,0x8959BB74,0x80A6458E)


def final_loan_club_eligible(c):
 # 0x619B8A..0x619C1D: valid manager, not user-controlled, 0x403E70,
 # and fresh 0x403F50 + club+0x1A4 < 5. Fresh country windows are enabled,
 # +0x1A4 is zeroed at 0x404166, and no actual loan has executed yet.
 if c.id==0 or c.name=='FREE TRANSFER' or c.name.startswith('!') or c.category in (2,3):
  return False
 if c.manager<0 or c.manager>=len(managers) or managers[c.manager].club is None:
  return False
 return c.country in countries

def replay_canonical_loan_tail():
 global transfer_listed,loan_listed
 if ARGS.mode!='scaled':
  raise AssertionError("--loan-tail is canonical only with --mode scaled")

 # Rebuild the already-locked 894-visit transfer-list state and mutations.
 _,r=replay(894,False)
 if r.state!=0x126CF137 or len(transfer_listed)!=625:
  raise AssertionError((hex(r.state),len(transfer_listed)))

 # Fresh Arsenal/user scan: all 37 source players reach RNG(200); only Upson
 # passes the <5 gate. No fresh player has bit 12 / selected / substitute /
 # injury / loan state here.
 user_hits=[]
 for idx,pid in enumerate(rosters[0]):
  roll=r.draw(200,'loan-user-candidate')
  if roll<5:
   user_hits.append((idx,pid,player_by_id[pid].name,roll))
 if user_hits!=[(12,1422,'Matthew Upson',4)] or r.state!=0x1AB5D762:
  raise AssertionError((user_hits,hex(r.state)))

 # 0x619DC0 resorts the 895-club vector before the two 0x619EB0 passes.
 loan_clubs=[c.id for c in clubs if eligible_club(c)]
 qsort(loan_clubs)
 for rem in range(len(loan_clubs),1,-1):
  k=r.draw(rem,'loan-shuffle-1');loan_clubs[k],loan_clubs[rem-1]=loan_clubs[rem-1],loan_clubs[k]
 if r.state!=0x8B83FB28 or loan_clubs[:5]!=[777,358,304,127,875]:
  raise AssertionError((hex(r.state),loan_clubs[:5]))
 # Mode-1 first pass exits deterministically on the neutral first club.
 for rem in range(len(loan_clubs),1,-1):
  k=r.draw(rem,'loan-shuffle-2');loan_clubs[k],loan_clubs[rem-1]=loan_clubs[rem-1],loan_clubs[k]
 if r.state!=0xB609BA3E or loan_clubs[:8]!=[862,481,317,256,373,1240,233,107]:
  raise AssertionError((hex(r.state),loan_clubs[:8]))

 # The one-player second pass rejects the first seven destinations
 # deterministically. Watford (107) accepts Upson's exact rating 65 in its
 # source-backed 42..66 band; RNG(10)<3 removes him from the candidate list.
 if r.draw(10,'watford-loan-selector')!=2 or r.state!=0xA23BE809:
  raise AssertionError(hex(r.state))
 # User-owned player routes to 0x409240, whose proposal timing consumes RNG(5).
 if r.draw(5,'user-loan-proposal')!=2 or r.state!=0xBB304AA8:
  raise AssertionError(hex(r.state))

 # Final 0x619B5C reverse physical-club loop. Dynamic bit 12 is part of the
 # same runtime flags consumed by positional/random selectors.
 loan_listed=set()
 records=[]
 eligible_visits=0
 last_cid=None
 for cid in range(len(clubs)-1,0,-1):
  club=clubs[cid]
  if not final_loan_club_eligible(club):
   continue
  eligible_visits+=1
  before=r.state
  dispatch=r.draw(10,'loan-list-dispatch')
  if dispatch<7:
   player,detail=positional(cid,r);kind='pos'
  else:
   player,detail=randomsel(cid,r);kind='rand'
  if player:
   loan_listed.add(player.id)
   records.append({
    'club':cid,'clubname':club.name,'dispatch':dispatch,'kind':kind,
    'player':player.id,'player_name':player.name,'rating':best_rating(player),
    'before':before,'state':r.state,'detail':detail,
   })
  last_cid=cid
  if len(loan_listed)>=200:
   break
 if len(loan_listed)!=200 or last_cid!=866 or r.state!=0x472F4DFF or eligible_visits!=292:
  raise AssertionError((len(loan_listed),last_cid,hex(r.state),eligible_visits))

 # One exact RNG(10) in 0x425680 precedes fixed-support-staff creation.
 pre_staff=r.draw(10,'user-init-rng10')
 if pre_staff!=2 or r.state!=0xA54D70C6:
  raise AssertionError((pre_staff,hex(r.state)))

 staff=[]
 for staff_type in (1,2,3,4,5,13):
  age_roll=r.draw(25,f'staff-{staff_type}-age')
  rating_roll=r.draw(2,f'staff-{staff_type}-rating')
  staff.append((staff_type,age_roll,rating_roll+1,r.state))
 if staff[2][2]!=1 or r.state!=0x418CAA72:
  raise AssertionError((staff,hex(r.state)))
 return {
  'post_transfer_state':'0x126CF137',
  'post_user_scan_state':'0x1AB5D762',
  'post_first_loan_shuffle':'0x8B83FB28',
  'post_second_loan_shuffle':'0xB609BA3E',
  'post_user_loan_proposal':'0xBB304AA8',
  'loan_list_count':len(loan_listed),
  'eligible_final_visits':eligible_visits,
  'last_final_club':last_cid,
  'post_final_loan_list_state':'0x472F4DFF',
  'pre_staff_rng10':pre_staff,
  'staff':[(t,a,rt,f"0x{s:08X}") for t,a,rt,s in staff],
  'youth_team_coach_rating':staff[2][2],
  'post_fixed_staff_state':f"0x{r.state:08X}",
  'first_final_listings':[(x['club'],x['player'],x['player_name']) for x in records[:10]],
  'last_final_listings':[(x['club'],x['player'],x['player_name']) for x in records[-10:]],
 }


def validate_prefix(out):
 clubs_expected=SCALED_FIRST40_CLUBS if ARGS.mode=='scaled' else MODULO_FIRST40_CLUBS
 states_expected=SCALED_FIRST40_STATES if ARGS.mode=='scaled' else MODULO_FIRST40_STATES
 if len(out)<40: raise AssertionError("prefix validation requires --limit >= 40")
 clubs_actual=tuple(x['club'] for x in out[:40]); states_actual=tuple(x['state'] for x in out[:40])
 if clubs_actual!=clubs_expected: raise AssertionError((clubs_actual,clubs_expected))
 if states_actual!=states_expected: raise AssertionError((states_actual,states_expected))
 return True

if __name__=='__main__':
 if ARGS.loan_tail:
  print(json.dumps(replay_canonical_loan_tail(),ensure_ascii=False,sort_keys=True))
  raise SystemExit(0)
 out,r=replay(ARGS.limit,False)
 if ARGS.validate_prefix:
  validate_prefix(out)
 if not ARGS.summary_only:
  for rec in out:
   printable=dict(rec); printable['before']=f"0x{rec['before']:08X}"; printable['state']=f"0x{rec['state']:08X}"
   print(json.dumps(printable,ensure_ascii=False,sort_keys=True))
 summary={
  'mode':ARGS.mode,'visit_count':len(out),'shuffle_prefix':arr[:10],
  'reverse_prefix':visits[:20],'state_after':f"0x{r.state:08X}",
  'listed_count':sum(x['selected'] is not None for x in out),
  'prefix_validated':bool(ARGS.validate_prefix),
 }
 print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
