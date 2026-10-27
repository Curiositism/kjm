#!/usr/bin/env python3
"""IHX UA / effectiveness: design check and experiment (counterflow e-NTU + LMTD)."""
import sys,json,math,CoolProp.CoolProp as CP
f='R1336MZZZ';K=273.15;PA=lambda g:(g+1.01325)*1e5
H=lambda T,P:CP.PropsSI('H','T',T+K,'P',P,f)/1e3
hg=lambda P:CP.PropsSI('H','P',P,'Q',1,f)/1e3
def ntu_cf(eps,cr):
    if cr<1e-6: return -math.log(1-eps)
    return math.log((eps-1)/(eps*cr-1))/(cr-1) if abs(cr-1)>1e-6 else eps/(1-eps)
def eps_cf(ntu,cr):
    if cr<1e-6: return 1-math.exp(-ntu)
    e=math.exp(-ntu*(1-cr)); return (1-e)/(1-cr*e)
def lmtd(dt1,dt2): return (dt1-dt2)/math.log(dt1/dt2)
# design (screenshot table): cold 3->4: 71.00->115.23 C, h 433.920->479.199, m=1.6792; hot 8f->9: 120.14->89.49, h 356.934->313.250, m=1.7405
mc,mh=1.6792,1.7405; Cc=mc*(479.199-433.920)/(115.23-71.00); Ch=mh*(356.934-313.250)/(120.14-89.49)
Q=mc*(479.199-433.920); eps=(115.23-71.00)/(120.14-71.00); cr=min(Cc,Ch)/max(Cc,Ch)
UA=ntu_cf(eps,cr)*min(Cc,Ch); L=lmtd(120.14-115.23,89.49-71.00)
print(f"DESIGN: Q={Q:.2f} kW Cc={Cc:.3f} Ch={Ch:.3f} kW/K Cr={cr:.3f} eps={eps:.3f} UA(eNTU)={UA:.3f} kW/K LMTD={L:.3f} UA(LMTD)={Q/L:.3f}")
UAd=UA
print(" #  m703  eps(T16) Qc   Cc    dTh  Cr_eff  UA_eNTU  UA_LMTD | eps_pred(UAd, Cr->0 / Cr=design) | eps(T24) UA_LMTD(T24)")
for fn in sys.argv[1:]:
    d=json.load(open(fn)); m=d['m703']
    hc_in=hg(PA(d['P602'])); hc_out=H(d['T25'],PA(d['P507'])); Qc=m*(hc_out-hc_in)
    for tag,Tci in (('T16',d['T16']),('T24',d['T24'])):
        dTc=d['T25']-Tci; e=dTc/(d['T22']-Tci); Cc=Qc/dTc
        dTh=d['T22']-d['T23']; Ch=Qc/dTh; cr=min(Cc,Ch)/max(Cc,Ch)
        ua=ntu_cf(e,cr)*min(Cc,Ch); ul=Qc/lmtd(d['T22']-d['T25'],d['T23']-Tci)
        if tag=='T16':
            ep0=eps_cf(UAd/Cc,0.0); epd=eps_cf(UAd/Cc,min(1,Cc/(m*1.40)))
            line=f"{fn.split('/')[-1]:12s} {m:.2f} {e:.3f} {Qc:5.1f} {Cc:.3f} {dTh:5.2f} {cr:.3f} {ua:7.2f} {ul:7.2f} | {ep0:.3f} / {epd:.3f}"
        else:
            line+=f" | {e:.3f} {ul:6.2f}"
    print(line)
