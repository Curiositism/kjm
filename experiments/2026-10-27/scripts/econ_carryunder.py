#!/usr/bin/env python3
"""Economizer liquid-outlet quality x8 back-calculated three ways (mass, energy, IHX balance). python3 -I econ_carryunder.py data*.json"""
import sys,json,CoolProp.CoolProp as CP
f='R1336MZZZ';K=273.15;PA=lambda g:(g+1.01325)*1e5
H=lambda T,P:CP.PropsSI('H','T',T+K,'P',P,f)/1e3
hf=lambda P:CP.PropsSI('H','P',P,'Q',0,f)/1e3; hg=lambda P:CP.PropsSI('H','P',P,'Q',1,f)/1e3
Tsl=lambda P:CP.PropsSI('T','P',P,'Q',0,f)-K
HL=lambda T,P: hf(P) if T>=Tsl(P)-0.01 else H(T,P)
for fn in sys.argv[1:]:
    d=json.load(open(fn)); P8=PA(d['P608']); m1,m3=d['m701'],d['m703']
    h6=H(d['T14'],PA(d['P510'])); x7=(h6-hf(PA(d['P603'])))/(hg(PA(d['P603']))-hf(PA(d['P603']))); hfg=hg(P8)-hf(P8)
    xm=(m3-(1-x7)*m1)/m3; xe=((m1*h6-(m1-m3)*hg(P8))/m3-hf(P8))/hfg
    xi=(HL(d['T23'],P8)+H(d['T25'],PA(d['P507']))-hg(PA(d['P602']))-hf(P8))/hfg
    mv=m3-(1-x7)*m1
    print(f"{fn}: x7={x7:.3f} flowfrac={(m1-m3)/m1:.3f} x8 mass={xm:+.3f} energy={xe:+.3f} IHX={xi:+.3f} vapor_in_liquid_line={mv:+.3f} kg/s")
