# Consistency check: claims in lectures/03/answer.md vs hw_runs traces, code and tests. Usage: python3 scripts/check_lec03.py .
import json, re, sys, subprocess, os
root = sys.argv[1]; L = f"{root}/lectures/03"
ans = open(f"{L}/answer.md").read()
ok = []
def check(name, cond, got=""):
    ok.append(bool(cond)); print(("PASS " if cond else "FAIL ") + name + (f"  [{got}]" if got else ""))
rows = [json.loads(l) for l in open(f"{L}/hw_runs/basic_runs.jsonl")]
def R(exp, qstart): return [r for r in rows if r["experiment"].startswith(exp) and r["question"].startswith(qstart)][0]
calls = lambda r: [(c["tool"], c["args"]) for c in r["tool_calls"]]
check("13 Basic runs, model in answer", len(rows)==13 and "gemini-3.5-flash-lite" in ans)
# Exercise claims
r = R("E0","What are the 3"); check("levels: search 'homework levels', ends (Lecture 01)", calls(r)==[("search_glossary",{"query":"homework levels"})] and r["answer"].strip().endswith("(Lecture 01)*") or r["answer"].strip().endswith("(Lecture 01)"), r["answer"].strip()[-20:])
check("levels: Basic/Implementation/Advanced + any one", all(w in r["answer"] for w in ("Basic","Implementation","Advanced")) and "any one" in r["answer"])
r = R("E0","Give me one"); check("quiz: make_quiz(2), asks QLoRA, answer held back", calls(r)==[("make_quiz",{"lecture":2})] and 'What does "QLoRA" mean?' in r["answer"])
r = R("E0","What is the difference between LoRA"); check("LoRA/QLoRA: 2 searches, 2 requests", calls(r)==[("search_glossary",{"query":"LoRA"}),("search_glossary",{"query":"QLoRA"})] and r["requests"]==2)
r = R("E0","Briefly"); check("4 terms: 4 calls in 2 requests", r["n_tool_calls"]==4 and r["requests"]==2)
r = R("E0","What is the difference between RAG"); check("RAG E0: 3 calls 3 requests, RAG searched twice, says not in glossary", r["n_tool_calls"]==3 and r["requests"]==3 and sum(a=={"query":"RAG"} for _,a in calls(r))==2 and r["says_not_in_glossary"])
# E1
e0 = {r["question"]:calls(r) for r in rows if r["experiment"]=="E0 baseline"}
e1 = [r for r in rows if r["experiment"].startswith("E1")]
check("E1: all 3 searched", all(r["n_tool_calls"]>0 for r in e1))
same = all([(t,{k:v.lower() for k,v in a.items()}) for t,a in calls(r)]==[(t,{k:v.lower() for k,v in a.items()}) for t,a in e0[r["question"]]] and r["requests"]==[x for x in rows if x["experiment"]=="E0 baseline" and x["question"]==r["question"]][0]["requests"] for r in e1)
check("E1: same calls (ignoring case) and requests as E0", same)
check("E1 RAG: no 'not in glossary'", not R("E1","What is the difference between RAG")["says_not_in_glossary"])
# E2
e2 = [r for r in rows if r["experiment"].startswith("E2")]
check("E2: 1 combined call each, requests 2", all(r["n_tool_calls"]==1 and r["requests"]==2 for r in e2), str([calls(r)[0][1]["query"] for r in e2]))
r = R("E2","Briefly"); check("E2 4 terms: defines Quantization, says 'based on the course materials'", "**Quantization:**" in r["answer"] and "based on the course materials" in r["answer"])
check("E2 RAG: no 'not in glossary'", not R("E2","What is the difference between RAG")["says_not_in_glossary"])
# E3
r = R("E3",""); check("E3: 1 search 'LoRA', no Lecture NN, ends with '?', no make_quiz", calls(r)==[("search_glossary",{"query":"LoRA"})] and not r["ends_with_lecture"] and r["answer"].strip().rstrip("*").endswith("?"))
# offline search table
sys.path.insert(0, root); os.chdir(root)
from app.tools import search_glossary, MAX_RESULTS
t = lambda q: [h["term"] for h in json.loads(search_glossary(q))]
check("offline: LoRA QLoRA -> LoRA,QLoRA", t("LoRA QLoRA")==["LoRA","QLoRA"])
check("offline: 4 terms -> PEFT,LoRA,QLoRA (cap 3)", t("PEFT LoRA QLoRA quantization")==["PEFT","LoRA","QLoRA"] and MAX_RESULTS==3)
check("offline: RAG -> Token,Fine-tuning,PEFT", t("RAG")==["Token","Fine-tuning","PEFT"])
check("offline: 'RAG fine-tuning' (E2 query) -> Fine-tuning only", t("RAG fine-tuning")==["Fine-tuning"], str(t("RAG fine-tuning")))
check("offline: 'Retrieval-Augmented Generation' not found", "was not found" in search_glossary("Retrieval-Augmented Generation"))
g = json.load(open("data/glossary.json"))["terms"]
check("RAG absent from glossary terms/aliases", not any(x.casefold() in ("rag","retrieval-augmented generation") for e in g for x in [e["term"],e["id"],*e["aliases"]]))
# Implementation
imp = open(f"{L}/hw_runs/impl_run.md").read()
f = "20261109-004424-lec03-agent-loop-tools-and-tracing.md"
check("impl approve: file named & committed", f in imp and os.path.exists(f"learning_log/{f}"))
check("impl approve: requests=2", "requests=2, tool_calls=1" in imp)
check("impl deny: no file, search first, requests=3", "New files in learning_log/: none" in imp and "search_glossary({'query': 'DeferredToolRequests'})" in imp and "requests=3" in imp)
check("impl deny: 'not completed', no retry", imp.count("save_learning_log({")==2 and "not completed" in imp)
# ADK
adk = open(f"{L}/hw_runs/adk_runs.md").read()
check("ADK levels: search 'homework levels'", "search_glossary({'query': 'homework levels'})" in adk)
check("ADK quiz: make_quiz(2), Epoch", "make_quiz({'lecture': 2})" in adk and '"Epoch"' in adk)
check("ADK RAG: 4 searches incl. Retrieval-Augmented Generation, says not in glossary", adk.split("## What is the difference between RAG")[1].count("[tool call]")==4 and "Retrieval-Augmented Generation'})" in adk and "not in the glossary" in adk)
check("ADK wraps str in {'result': ...}", "{'result': '" in adk)
# Pi
pi = open(f"{L}/hw_runs/pi_system_prompt.txt").read()
for s in ("Use read to examine files instead of cat or sed.","Use write only for new files or complete rewrites.","Be concise in your responses","Show file paths clearly","Additional tools may be available."):
    check(f"Pi prompt has: {s[:40]}", s in pi)
check("Pi prompt has no confirm/approval rule", not re.search(r"confirm|approv|ask (the user|before)", pi, re.I))
# code claims
src = open("app/agent.py").read(); tl = open("app/tools.py").read()
check("requires_approval=True on save_learning_log", "agent.tool_plain(tools.save_learning_log, requires_approval=True)" in src)
check("output_type [str, DeferredToolRequests]", "output_type=[str, DeferredToolRequests]" in src)
check("usage carried over", "usage=result.usage" in src)
check("MAX_LOG_CHARS 5000", "MAX_LOG_CHARS = 5000" in tl)
check("INSTRUCTIONS has no braces (ADK templating)", "{" not in src.split('INSTRUCTIONS = """')[1].split('"""')[0])
out = subprocess.run(["uv","run","pytest","-q"],capture_output=True,text=True,env={**os.environ,"PYDANTIC_AI_NO_BANNER":"1"}).stdout.strip().splitlines()[-1]
check("pytest: 21 passed (as claimed)", out.startswith("21 passed") and "21 passed" in ans, out)
check("no em dashes in answer.md", "—" not in ans)
print(f"\n{sum(ok)}/{len(ok)} passed")
