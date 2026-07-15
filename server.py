import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from gradio_client import Client

app = FastAPI()

# VS Code যাতে সহজে কানেক্ট হতে পারে তার জন্য CORS অনুমোদন করা
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Axon v26 Hugging Face Client
hf_client = Client("aiencoder-axon.hf.space")[cite: 2]

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    
    # সর্বশেষ ইউজার মেসেজটি বের করা
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
            
    try:
        # Hugging Face API কে কল করা হচ্ছে (Qwen 2.5 Coder 7B ব্যবহার করে)
        result = hf_client.predict(
            message=user_message,
            history=[],
            model="⚖️ Qwen2.5 Coder 7B (Balanced)",  # আপনার পছন্দমতো মডেল দিতে পারেন[cite: 2]
            temp=0.7,[cite: 2]
            tokens=2048,[cite: 2]
            api_name="/respond"[cite: 2]
        )
        
        # Gradio Response থেকে টেক্সট এক্সট্রাক্ট করা
        # নোট: Gradio-র রিটার্ন ফরম্যাট অনুযায়ী ডাটা ফিল্টার করা হয়েছে
        response_text = result[0][-1]['content'][0]['text'][cite: 2]
        
    except Exception as e:
        response_text = f"Error connecting to Axon API: {str(e)}"

    # OpenAI-এর স্ট্যান্ডার্ড ফরম্যাটে রেসপন্স পাঠানো
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }
        ]
    }

if __name__ == "__main__":
    # local port 8000 এ সার্ভার রান করা হচ্ছে
    uvicorn.run(app, host="127.0.0.1", port=8000)
