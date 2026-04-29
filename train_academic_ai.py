import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle
import random

print("Generating Academic Cycle Data for AI...")
data = []
for _ in range(1000):
    mid = random.randint(20, 100)
    model = random.randint(20, 100)
    needs_remedial = 1 if mid < 50 or model < 50 else 0
    rem_att = random.randint(50, 100) if needs_remedial else 0
    rem_marks = random.randint(40, 90) if needs_remedial else 0
    
    base_knowledge = (mid + model) / 2
    if needs_remedial:
        end_sem = (base_knowledge * 0.3) + (rem_marks * 0.5) + (rem_att * 0.2) + random.randint(-5, 5)
    else:
        end_sem = base_knowledge + random.randint(-5, 5)
        
    end_sem = min(100, max(0, round(end_sem)))
    data.append([mid, model, needs_remedial, rem_att, rem_marks, end_sem])

df = pd.DataFrame(data, columns=['mid_term', 'model_exam', 'needs_remedial', 'rem_att', 'rem_marks', 'end_sem'])

X = df[['mid_term', 'model_exam', 'needs_remedial', 'rem_att', 'rem_marks']]
y = df['end_sem']
ai_model = LinearRegression()
ai_model.fit(X, y)

with open('model.pkl', 'wb') as f:
    pickle.dump(ai_model, f)

print("✅ SUCCESS: 'model.pkl' AI Brain created successfully!")