import openai

def explain_signal(signal, indicators):
    # For demo: use GPT-3.5 to generate explanation
    expl_prompt = f"Explain why the strategy issued '{signal}'. Indicators: {indicators}"
    response = openai.Completion.create(model="text-davinci-003",
        prompt=expl_prompt, max_tokens=80)
    return response.choices[0].text.strip()

def feature_importance(model, X):
    # Use SHAP values if available, dummy for now
    return {"feature_importance": "Not implemented (add SHAP or LIME here)"}