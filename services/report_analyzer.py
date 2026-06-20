from utils.config import client

def analyze_report(text):

    prompt = f"""
    You are an experienced medical doctor.
    
    Analyze the following medical report carefully.
    
    Medical Report:
    {text}
    
    Provide the result in this format:
    
    ## Summary
    
    ## Possible Diseases
    
    ## Risk Level
    (Low / Medium / High)
    
    ## Important Findings
    
    ## Symptoms
    
    ## Recommended Tests
    
    ## Medicines (General Information Only)
    
    ## Precautions
    
    ## Specialist Doctor
    
    ## Emergency Warning
    
    IMPORTANT:
    Do not provide a final medical diagnosis.
    Mention that the analysis is AI-generated and for informational purposes only.
    Recommend consultation with a qualified doctor for confirmation.
    
    Keep the explanation simple and patient-friendly.
    """

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content