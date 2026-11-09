import json, re, sys
# Consistency check: every number/claim in lectures/02/answer.md that has a source file in the repo. Usage: python3 -I scripts/check_lec02.py lectures/02
D = sys.argv[1]
ok = []
def check(name, cond, got=""):
    ok.append(cond); print(("PASS " if cond else "FAIL ") + name + (f"  [{got}]" if got else ""))
R = json.load(open(f"{D}/exercise_ep20/result.json"))
c = R["config"]
check("model Qwen/Qwen3.5-0.8B", c["base_model"] == "Qwen/Qwen3.5-0.8B")
check("revision 2fc0636...", c["revision"].startswith("2fc06364715b967f"))
check("r16 a32 lr2e-4 ep20 warmup6 seed42 greedy", (c["lora_r"],c["lora_alpha"],c["lr"],c["num_train_epochs"],c["warmup_steps"],c["seed"],c["gen"]["do_sample"])==(16,32,2e-4,20,6,42,False))
check("versions", R["versions"]=={"transformers":"5.18.0","peft":"0.21.1","trl":"1.14.2","torch":"2.14.1+cu130"})
check("method LoRA no quant", R["method"]=="LoRA (no quantization)")
b,a = R["before"],R["after"]
check("before 0.952/0.381", (round(b["format_rate"],3),round(b["content_rate"],3))==(0.952,0.381), f"{b['format_rate']:.3f}/{b['content_rate']:.3f}")
check("after 1.000/0.905", (round(a["format_rate"],3),round(a["content_rate"],3))==(1.0,0.905), f"{a['format_rate']:.3f}/{a['content_rate']:.3f}")
check("gen time 49.9 -> 37.9", (b["seconds"],a["seconds"])==(49.9,37.9))
check("no regressions", R["regressed"]==[])
check("executed_training_myself True", R["executed_training_myself"] is True)
K = {k["Question"]:(k["In FAQ"],k["Before-training classification"],k["After-training classification"]) for k in R["knowledge"]}
exp = {"When is the final assignment deadline for this course?":(False,"asserted","asserted"),
       "What is the instructor's name?":(False,"needs_review","needs_review"),
       "What is the topic of the next lecture?":(False,"needs_review","needs_review"),
       "When is the assignment deadline?":(True,"asserted","asserted")}
check("knowledge table (4 rows)", K==exp)
fin = [k for k in R["knowledge"] if k["Question"].startswith("When is the final")][0]
check("final-deadline answers Sept 30, needs_review false", all("September 30" in fin[x] and '"needs_review": false' in fin[x] for x in ("Before-training output","After-training output")))

def rows(n): return json.load(open(f"{D}/exercise_ep20/{n}.json"))
def nr(r):
    m = re.search(r"\{.*\}", r["raw"], re.S)
    try: return json.loads(m.group(0)).get("needs_review")
    except Exception: return None
E = {n: rows(n) for n in ("eval_before","eval_after","eval_before_4bit")}
for n,d in E.items():
    s = d["summary"]; check(f"{n}: summary matches row counts", round(s["content_rate"]*21)==sum(r["content_ok"] for r in d["rows"]) and round(s["format_rate"]*21)==sum(r["format_ok"] for r in d["rows"]) and len(d["rows"])==21)
check("summary == result.json", E["eval_before"]["summary"]["content_rate"]==b["content_rate"] and E["eval_after"]["summary"]["content_rate"]==a["content_rate"])
B,A,Q = (E[n]["rows"] for n in ("eval_before","eval_after","eval_before_4bit"))
g = lambda rs: [r for r in rs if not r["gold_needs_review"]]
u = lambda rs: [r for r in rs if r["gold_needs_review"]]
check("15 grounded / 6 ungrounded", (len(g(B)),len(u(B)))==(15,6))
gb = sum(nr(r) is True for r in g(B)); ga = sum(nr(r) is True for r in g(A))
check("grounded wrongly flagged true 7 -> 1", (gb,ga)==(7,1), f"{gb}->{ga}")
ub = sum(nr(r) is True for r in u(B)); ua = sum(nr(r) is True for r in u(A))
check("ungrounded correctly true 2 -> 5", (ub,ua)==(2,5), f"{ub}->{ua}")
fails = [r["question"] for r in A if not r["content_ok"]]
check("2 failures after training", len(fails)==2, "; ".join(fails))
check("failure: PDF format question", any("PDF" in q for q in fails))
check("failure: office hours appointment", any("office hours" in q.lower() and "appointment" in q.lower() for q in fails))
pdf = [ (x,y) for x,y in zip(B,A) if "PDF" in x["question"] and not y["content_ok"]][0]
check("PDF: before right text but flag true (fail), after refusal", ("No" in pdf[0]["raw"] and not pdf[0]["content_ok"]) and nr(pdf[1]) is True and nr(pdf[0]) is True, f"before nr={nr(pdf[0])}")
s4 = E["eval_before_4bit"]["summary"]
check("4-bit format 1.000 / content 0.048", (round(s4["format_rate"],3),round(s4["content_rate"],3))==(1.0,0.048), f"{s4['format_rate']:.3f}/{s4['content_rate']:.3f}")
check("4-bit needs_review true on all 21", sum(nr(r) is True for r in Q)==21, str(sum(nr(r) is True for r in Q)))
where = [r for r in Q if "where" in r["question"].lower()]
check("4-bit: 'where' questions answered with deadline", len(where)>=3 and all("September 30" in r["raw"] or "deadline" in r["raw"].lower() for r in where), f"{len(where)} where-questions")
print(f"\n{sum(ok)}/{len(ok)} passed")
