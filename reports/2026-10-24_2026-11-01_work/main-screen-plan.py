import pathlib,json,re
P=pathlib.Path(__file__).resolve().parent
rows=json.loads((P/'main-route-screen.json').read_text(encoding='utf-8'))
groups={
'core':{2,9,10,11,12,16,18,22,42,54,56,61,67,70,73,74,76,77,86,94,96,106,107,193,540,549,555,556,558,559,560,561,564,565,567,568,569,572,573,575,576,578,581,588,589,590,592,595,598,602,604,606,609,851},
'geometry':{1,3,5,8,17,24,28,30,31,32,33,37,43,46,47,48,50,53,55,57,101,105,110,186,189,190,201,207,209,227,230,231,257,280,284,301,325,350,438,454,465,479,480,499,519,520,525,531,536,541,563,577,585,587,601,605,607,608,681,686,713,739,811,845,860},
'extension':{6,7,14,15,41,59,68,69,71,75,81,87,90,91,97,98,99,137,160,170,192,208,214,218,220,232,243,249,270,286,299,308,311,339,342,343,345,359,391,399,402,403,406,410,412,415,417,420,421,428,434,439,455,461,462,471,489,501,502,516,517,518,521,522,523,524,526,527,528,529,530,533,534,535,537,538,574,580,583,591,594,597,600,610,673,678,685,692,694,696,698,703,706,710,717,723,732,734,743,746,747,755,756,759,762,766,771,774,776,779,783,794,798,799,805,810,812,816,817,820,824,826,831,841,842,843,844,846,847,857,858}
}
used=set();selected={}
for k,inds in groups.items():
    assert not used&inds,(k,used&inds)
    used|=inds;selected[k]=[dict(rows[i],screen_index=i,screening_note='Main agent manually reviewed title; possible scope requires full abstract judgment') for i in sorted(inds)]
    (P/f'main-extra-{k}.json').write_text(json.dumps(selected[k],ensure_ascii=False,indent=2),encoding='utf-8')
remaining=[dict(x,screen_index=i,title_screened=True,abstract_read=False,disposition='excluded',provisional_title_exclusion=True,reason='题名明确属于本报告范围以外的研究；已由主agent逐题名检查，具体学科理由将在最终台账按主题补记。') for i,x in enumerate(rows) if i not in used]
(P/'main-title-screened-offscope.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'main-screen-audit.json').write_text(json.dumps({'title_reviewed':len(rows),'possible_relevance_routed':{k:len(v) for k,v in selected.items()},'clear_title_offscope':len(remaining),'note':'Manual title audit of every screen entry; routed uncertain/robot/3D/sensor/application candidates for abstract judgment. Clear mathematics/physics/astronomy/audio/NLP/medical2D/etc title exclusions require specific reasons, never low stars or quota.'},ensure_ascii=False,indent=2),encoding='utf-8')
print({k:len(v) for k,v in selected.items()},'offscope',len(remaining))
