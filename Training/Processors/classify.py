import pandas as pd
from regex import classify_with_regex
from bert import classify_with_bert
from llm import classify_with_llm

def classify(logs):
    labels = []
    for source,log_msg in logs:
        labels.append(classify_log(source,log_msg))
        
    return labels
        
        
        
        
def classify_log(source,log_message):
    if source == 'LegacyCRM':
        label = classify_with_llm(log_message)
    else:
        label = classify_with_regex(log_message)
        if label is not None:
            return label
        else:
            label = classify_with_bert(log_message)
    return label
    
    
def classify_csv(input_csv):
    df = pd.read_csv(input_csv)
    df["target_label"] = classify(list(zip(df['source'], df['log_message'])))
    output_csv = "D:\Desktop\NLP Projects\Log_CLassification\Training\Resources\output.csv"
    df.to_csv(output_csv, index=False)