import os, json, requests
KEY=os.environ["OPENROUTER_API_KEY"]; URL="https://openrouter.ai/api/v1/chat/completions"
M="meta-llama/llama-3.1-8b-instruct"
PROMPT=('One of Candidate SIGMA or Candidate THETA is responsible. Each is equally '
        'likely beforehand. Give your probability that each is responsible.')
SCHEMA={"type":"json_schema","json_schema":{"name":"beliefs","strict":True,"schema":{
  "type":"object","additionalProperties":False,
  "properties":{"SIGMA":{"type":"number"},"THETA":{"type":"number"}},
  "required":["SIGMA","THETA"]}}}
VARIANTS=[
  ("A strict schema + explicit JSON instruction",
   {"response_format":SCHEMA,"messages":[{"role":"user","content":PROMPT+
    ' Reply with only a JSON object with keys SIGMA and THETA.'}]}),
  ("B json_object mode (no grammar)",
   {"response_format":{"type":"json_object"},"messages":[{"role":"user","content":PROMPT+
    ' Reply with only a JSON object with keys SIGMA and THETA.'}]}),
  ("C no response_format, one-shot example",
   {"messages":[{"role":"user","content":PROMPT+
    ' Reply with only a JSON object, for example {"SIGMA": 0.700, "THETA": 0.300}'}]}),
]
for label,extra in VARIANTS:
    body={"model":M,"max_tokens":300,"seed":1,"temperature":0.7,**extra}
    print("===",label)
    try:
        r=requests.post(URL,json=body,timeout=180,
                        headers={"Authorization":f"Bearer {KEY}"}).json()
        if "error" in r: print("   API ERROR:",r["error"]); continue
        c=r["choices"][0]["message"].get("content") or ""
        print("   raw:",repr(c[:200]))
    except Exception as e: print("   ERROR:",type(e).__name__,e)
