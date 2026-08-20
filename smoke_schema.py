import os, json, requests
KEY = os.environ["OPENROUTER_API_KEY"]
URL = "https://openrouter.ai/api/v1/chat/completions"
PROMPT = ('One of Candidate SIGMA or Candidate THETA is responsible. Each is equally '
          'likely beforehand. Give your probability that each is responsible.')
SCHEMA = {"type":"json_schema","json_schema":{"name":"beliefs","strict":True,"schema":{
    "type":"object","additionalProperties":False,
    "properties":{"SIGMA":{"type":"number"},"THETA":{"type":"number"}},
    "required":["SIGMA","THETA"]}}}
TRIALS = [("meta-llama/llama-3.3-70b-instruct",None),
          ("meta-llama/llama-3.1-8b-instruct",None),
          ("deepseek/deepseek-v4-flash-0731",{"enabled":False}),
          ("z-ai/glm-5.2",{"enabled":False}),
          ("tencent/hy3",{"effort":"none"}),
          ("openai/gpt-5.6-sol",{"effort":"none"})]
for model, reasoning in TRIALS:
    body={"model":model,"max_tokens":300,"seed":1,"response_format":SCHEMA,
          "messages":[{"role":"user","content":PROMPT}]}
    if reasoning: body["reasoning"]=reasoning
    if "gpt-5.6" not in model: body["temperature"]=0.7
    print("===", model)
    try:
        r=requests.post(URL,json=body,timeout=180,
                        headers={"Authorization":f"Bearer {KEY}"}).json()
        if "error" in r: print("   API ERROR:", r["error"]); continue
        c=r["choices"][0]["message"].get("content") or ""
        print("   raw:", repr(c[:200]))
        try: print("   parsed OK:", json.loads(c))
        except Exception as e: print("   PARSE FAIL:", e)
    except Exception as e: print("   ERROR:", type(e).__name__, e)
