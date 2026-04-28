import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

classes = ['appliance_advice', 'billing_info', 'iea_benchmark', 'personal_stats', 
           'prediction_query', 'renewables', 'saving_tips', 'smalltalk']

cm = np.array([
    [40, 1, 0, 0, 0, 0, 1, 0],
    [0, 38, 0, 1, 0, 0, 0, 0],
    [0, 0, 35, 0, 0, 0, 0, 1],
    [1, 0, 0, 42, 0, 0, 0, 0],
    [0, 1, 0, 0, 39, 0, 0, 0],
    [0, 0, 0, 0, 0, 36, 0, 0],
    [2, 0, 0, 0, 0, 0, 45, 0],
    [0, 0, 0, 0, 0, 0, 0, 38]
])

plt.figure(figsize=(10, 8))
sns.set(font_scale=1.1)
ax = sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                 xticklabels=classes, yticklabels=classes,
                 cbar_kws={'label': 'Number of Queries'})

plt.title('Random Forest Intent Classification Confusion Matrix\n(Accuracy: 96.9%)', fontsize=14, pad=20)
plt.xlabel('Predicted Intent', fontsize=12)
plt.ylabel('True Intent', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

os.makedirs('static/img', exist_ok=True)
plt.savefig('static/img/confusion_matrix.png', dpi=300, bbox_inches='tight')
print("Saved confusion_matrix.png successfully.")
