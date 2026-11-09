# Consistency check for the Lecture 2 Basic (basic_ep5) and Implementation (impl_it_helpdesk) sections. Usage: python3 -I scripts/check_lec02_homework.py lectures/02
import json, re
import sys
D=sys.argv[1] if len(sys.argv)>1 else "lectures/02"
ok=[]
def check(n,c,g=""): ok.append(bool(c)); print(("PASS " if c else "FAIL ")+n+(f"  [{g}]" if g else ""))
def nr(r):
    m=re.search(r"\{.*\}",r["raw"],re.S)
    try: return json.loads(m.group(0)).get("needs_review")
    except Exception: return None
# Basic
R=json.load(open(f"{D}/basic_ep5/result.json")); B=json.load(open(f"{D}/basic_ep5/eval_before.json"))["rows"]; A=json.load(open(f"{D}/basic_ep5/eval_after.json"))["rows"]
c=R["config"]; E=json.load(open(f"{D}/exercise_ep20/result.json"))["config"]
diff={k for k in c if c[k]!=E[k]}
check("basic: only num_train_epochs changed (20 -> 5)", diff=={"num_train_epochs"} and c["num_train_epochs"]==5, str(diff))
check("basic: before 0.952/0.381", (round(R["before"]["format_rate"],3),round(R["before"]["content_rate"],3))==(0.952,0.381))
check("basic: after 1.000/0.714", (round(R["after"]["format_rate"],3),round(R["after"]["content_rate"],3))==(1.0,0.714), f"{R['after']['format_rate']:.3f}/{R['after']['content_rate']:.3f}")
reg=R["regressed"]; check("basic: 1 regression 'When will grades be released?'", len(reg)==1 and "grades" in json.dumps(reg).lower(), json.dumps(reg)[:150])
check("basic: grounded correct 15/15", sum(r["content_ok"] for r in A if not r["gold_needs_review"])==15)
check("basic: ungrounded correct 0/6", sum(r["content_ok"] for r in A if r["gold_needs_review"])==0)
check("basic: 4 of 6 ungrounded fabricated with flag false", sum(nr(r) is False for r in A if r["gold_needs_review"])==4)
g=[r for r in A if "grades" in r["question"].lower()]
check("basic: grades answer reuses Sept 30 deadline", g and "September 30" in g[0]["raw"], g[0]["raw"][:120] if g else "")
pdf=[r for r in A if "PDF" in r["question"]]; check("basic: PDF question correct at 5 epochs", pdf and pdf[0]["content_ok"])
for q in ("recordings","feedback"):
    m=[r for r in A if q in r["question"].lower()]; check(f"basic: '{q}' fabricated with flag false", m and nr(m[0]) is False and m[0]["gold_needs_review"], m[0]["raw"][:90] if m else "none")
q4a=json.load(open(f"{D}/basic_ep5/eval_before_4bit.json"))["rows"]; q4b=json.load(open(f"{D}/exercise_ep20/eval_before_4bit.json"))["rows"]
check("4-bit outputs identical across the two sessions", [r["raw"] for r in q4a]==[r["raw"] for r in q4b])
print("basic gen seconds", R["before"]["seconds"], R["after"]["seconds"], "| keys", [k for k in R if k not in ("config","versions","knowledge","before","after","regressed")])
# Impl
R=json.load(open(f"{D}/impl_it_helpdesk/result.json")); B=json.load(open(f"{D}/impl_it_helpdesk/eval_before.json"))["rows"]; A=json.load(open(f"{D}/impl_it_helpdesk/eval_after.json"))["rows"]
check("impl: same CONFIG as exercise", {k for k in R["config"] if R["config"][k]!=E[k]}==set(), str({k for k in R["config"] if R["config"][k]!=E[k]}))
check("impl: before 0.952/0.143", (round(R["before"]["format_rate"],3),round(R["before"]["content_rate"],3))==(0.952,0.143), f"{R['before']['format_rate']:.3f}/{R['before']['content_rate']:.3f}")
check("impl: after 1.000/0.905", (round(R["after"]["format_rate"],3),round(R["after"]["content_rate"],3))==(1.0,0.905))
check("impl: no regressions", R["regressed"]==[])
check("impl: 15/6 split", sum(not r["gold_needs_review"] for r in A)==15 and len(A)==21)
gb=sum(r["content_ok"] for r in B if not r["gold_needs_review"]); ub=sum(r["content_ok"] for r in B if r["gold_needs_review"])
ga=sum(r["content_ok"] for r in A if not r["gold_needs_review"]); ua=sum(r["content_ok"] for r in A if r["gold_needs_review"])
check("impl: grounded 3 -> 14, ungrounded 0 -> 5", (gb,ub,ga,ua)==(3,0,14,5), f"{gb},{ub} -> {ga},{ua}")
check("impl: 8 of 15 grounded flagged true before", sum(nr(r) is True for r in B if not r["gold_needs_review"])==8)
fails=[r["question"] for r in A if not r["content_ok"]]
check("impl: failures = visitors ID + work remotely", len(fails)==2 and any("ID" in q for q in fails) and any("remotely" in q for q in fails), "; ".join(fails))
wr=[r for r in A if "remotely" in r["question"]][0]; check("impl: 'work remotely' answered with Wi-Fi", "NW-Staff" in wr["raw"] or "Wi-Fi" in wr["raw"], wr["raw"][:100])
for q,s in (("colleague","Yes"),("show ID","No")):
    m=[r for r in B if q in r["question"]]; check(f"impl before: '{q}' -> '{s}...'", m and s in m[0]["raw"], m[0]["raw"][:90] if m else "none")
vpn=[r for r in B if "What port does the VPN" in r["question"]]; check("impl before: VPN port question says FAQ silent", vpn and nr(vpn[0]) is True, vpn[0]["raw"][:100] if vpn else "")
K=R["knowledge"]; check("impl: knowledge 3 needs_review before & after, control asserted", sum(k["Before-training classification"]=="needs_review" and k["After-training classification"]=="needs_review" for k in K)==3 and any(k["In FAQ"] and k["After-training classification"]=="asserted" for k in K), str([(k["Question"][:30],k["Before-training classification"],k["After-training classification"]) for k in K]))
fw=[k for k in K if "firewall" in k["Question"].lower()]; check("impl: no invented firewall IP", fw and not re.search(r"\d+\.\d+\.\d+\.\d+", fw[0]["Before-training output"]+fw[0]["After-training output"]))
print(f"\n{sum(ok)}/{len(ok)} passed")
