from openai import OpenAI
from prompt_templates import bridge_ana_prompt, bridge_antec_prompt, subtype_prompt
import json
import os
import ast

# import prompt templates from separate file
# read in API key from file
with open("api_key.txt", ) as f:
    api_key = f.read()

client = OpenAI(api_key=api_key)

with open("api_key_openrouter.txt", ) as f:
    api_key_openrouter = f.read()

def openrouter_api_call(prompt, role_instr, model_version):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key_openrouter,
    )

    try:
        completion = client.chat.completions.create(
            #extra_headers={
            #    "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
            #    "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
            #},
            #extra_body={},
            model=model_version,
            messages=[
                {
                    "role": "system",
                    "content": role_instr,
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
    except:
        return ""
    try:
        print(completion.choices[0].message.content)
        return completion.choices[0].message.content
    except:
        return ""

def gpt_api_call(prompt, role_instr, model_version):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": role_instr, #"You are a chatbot assistant"
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model_version,  # gpt-4o
    )

    print(response)
    return response.choices[0].message.content

def main(preprocessed_json_data, llm_baseline_output_json, model_name, tasks, docs_to_run=None, docs_to_skip=None, sentencewise_ana=True):

    ana_role = "You are an expert in linguistic annotation, specifically bridging anaphora recognition. Output a list of bridging anaphora. Output only a list with no absolutely additional text."
    ante_role = "You are an expert in linguistic annotation, specifically bridging antecedent selection. Output a single antecedent as instructed. Output only the string of the antecedent entity with no additional explanation."
    subtype_role = "You are an expert in bridging anaphora-antecedent pair subcategorization. Output a applicable subtypes as instructed (no spaces in between). Output only the string of the subtype with no additional explanation."

    # open preprocessed json file
    with open(preprocessed_json_data, "r") as jf:
        gold_annotation_data = json.load(jf)

    # open llm_baseline_output_json file if it exists, otherwise create new file and dict
    if os.path.exists(llm_baseline_output_json):
        with open(llm_baseline_output_json, "r") as jf:
            llm_baseline_data = json.load(jf)
    else:
        llm_baseline_data = {}

    for doc_name in list(gold_annotation_data.keys()):#["GUM_academic_librarians_lel76"]:#list(gold_annotation_data.keys())[:4]: # shortening for testing
        if (docs_to_run is not None and doc_name not in docs_to_run) or (docs_to_skip is not None and doc_name in docs_to_skip):
            continue
        print(doc_name)
        if doc_name not in llm_baseline_data:
            llm_baseline_data[doc_name] = {}
        if model_name not in llm_baseline_data[doc_name]:
            llm_baseline_data[doc_name][model_name] = {}
        # plain text prompt
        if "anaphor_recognition" in tasks:
            print("anaphor recognition")
            if sentencewise_ana:
                anaphora = []
                for sentence in gold_annotation_data[doc_name]["sentences"]:
                    anaphor_recognition_prompt = bridge_ana_prompt.replace("{text}", sentence["text_w_buffer"])
                    if "gpt" in model_name:
                        anaphor_recognition_response = gpt_api_call(anaphor_recognition_prompt, ana_role, model_name)
                    else:
                        anaphor_recognition_response = openrouter_api_call(anaphor_recognition_prompt, ana_role, model_name)
                    try:
                        sent_anaphora = ast.literal_eval(anaphor_recognition_response)
                        for ana in sent_anaphora:
                            if ana in sentence["text"]:
                                anaphora.append(ana)
                    except:
                        anaphora.append(anaphor_recognition_response)

            else:
                anaphor_recognition_prompt = bridge_ana_prompt.replace("{text}", gold_annotation_data[doc_name]["text"])
                if "gpt" in model_name:
                    anaphor_recognition_response = gpt_api_call(anaphor_recognition_prompt, ana_role, model_name)
                else:
                    anaphor_recognition_response = openrouter_api_call(anaphor_recognition_prompt, ana_role, model_name)
                try:
                    anaphora = ast.literal_eval(anaphor_recognition_response)
                except:
                    anaphora = anaphor_recognition_response
            llm_baseline_data[doc_name][model_name]["bridging_anaphora"] = anaphora

        if "antecedent_selection" in tasks:
            print("antecedent selection")
            pred_ante_answers = {}
            for ana_id in gold_annotation_data[doc_name]["antecedent_texts"]:
                text = gold_annotation_data[doc_name]["antecedent_texts"][ana_id]
                antecedent_selection_prompt = bridge_antec_prompt.replace("{text}", text)
                if "gpt" in model_name:
                    antecedent_selection_response = gpt_api_call(antecedent_selection_prompt, ante_role, model_name)
                else:
                    antecedent_selection_response = openrouter_api_call(antecedent_selection_prompt, ante_role, model_name)
                pred_ante_answers[ana_id] = antecedent_selection_response.strip() # return is single string answer
            llm_baseline_data[doc_name][model_name]["antecedent_selection"] = pred_ante_answers

        if "subtype_classification" in tasks:
            print("subtype classification")
            pred_subtypes = {}
            for ana_id in gold_annotation_data[doc_name]["subtype_input"]:
                ante_text = gold_annotation_data[doc_name]["subtype_input"][ana_id]["ante_text"]
                ana_text = gold_annotation_data[doc_name]["subtype_input"][ana_id]["ana_text"]
                subtype_classification_prompt = subtype_prompt.replace("{antecedent_text}", ante_text).replace("anaphor_text", ana_text)
                if "gpt" in model_name:
                    subtype_classification_response = gpt_api_call(subtype_classification_prompt, subtype_role, model_name)
                else:
                    subtype_classification_response = openrouter_api_call(subtype_classification_prompt, subtype_role, model_name)
                pred_subtypes[ana_id] = subtype_classification_response.strip().replace(" ", "")  # return is single string answer
            llm_baseline_data[doc_name][model_name]["subtype_classification"] = pred_subtypes

    # write to json file
    with open(llm_baseline_output_json, "w") as jf:
        json.dump(llm_baseline_data, jf, indent=4)


if __name__ == "__main__":
    # Files for API keys must be created and the following variable must be filled in:
    input_json_file = "" # input should be output json file from preprocessing step
    output_json_file = "" # name of new output json file
    model_name = "" # model name, e.g., gpt-5, meta-llama/llama-3.3-70b-instruct
    docs = [""] # names of documents to process, e.g, ["GUM_academic_discrimination", ...]
    main(input_json_file, output_json_file, model_name, ["anaphor_recognition", "antecedent_selection", "subtype_classification"], docs_to_run=docs, docs_to_skip=None)
