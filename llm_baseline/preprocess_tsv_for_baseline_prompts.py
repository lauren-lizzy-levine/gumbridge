from utils.llm_full_bridging_resolution import get_entity_information, process_tsv_v2
import os
import glob
import json
import ast
import copy
from collections import Counter
import pandas as pd
import numpy as np

def make_bridge_pair_df(mentions, entities, bridgetypes=None):

    ana_mention_ids = []
    ante_mention_ids = []
    ana_span = []
    ante_span = []
    bridgetype = []

    for mention in mentions:
        for bridge_mention_id in mention.bridge:
            mention_index = bridge_mention_id - 1
            anaphor_mention = mentions[mention_index]
            if anaphor_mention.infstat not in ["split", "split_candidate"]: #anaphor_mention.infstat not in ["split", "giv", "old", "split_candidate", "giv_candidate", "old_candidate"] and (bridgetypes is None or anaphor_mention.bridgetype in bridgetypes): # and "entity-associative" in anaphor_mention.bridgetype:
                # check that mention.id is the closest mention in its entity cluster to anaphor_mention.id
                # if it is not, change mention to the closest one to be added to the pair
                most_recent_mention_id = max([men_id for men_id in entities[mention.ent_id].coref_mention_ids if men_id < anaphor_mention.id], default=None)
                if most_recent_mention_id is None: # skipping if there are no previous mentions
                    continue
                most_recent_mention_index = most_recent_mention_id - 1
                antecedent_mention = mentions[most_recent_mention_index]
                ana_mention_ids.append(anaphor_mention.id)
                ante_mention_ids.append(antecedent_mention.id)
                ana_span.append(str(anaphor_mention.span))
                ante_span.append(str(antecedent_mention.span))
                bridgetype.append(anaphor_mention.bridgetype)

    bridge_pair_df = pd.DataFrame({"ana_span": ana_span, "ante_span": ante_span, "bridgetype": bridgetype,
                                   "ana_mention_id": ana_mention_ids, "ante_mention_id": ante_mention_ids})

    return bridge_pair_df

def get_mentions_in_window(mentions, window_start, window_end):
    # return list of string mentions in the window
    str_mentions = []
    window_start_sent, window_start_tok = window_start
    window_end_sent, window_end_tok = window_end
    for mention in mentions:
        mention_in_window = True
        for sent_tok_id in mention.span:
            sent_id, tok_id = sent_tok_id.split("-")
            sent_id = int(sent_id)
            tok_id = int(tok_id)
            if sent_id < window_start_sent or sent_id > window_end_sent:
                mention_in_window = False
            else:
                if sent_id == window_start_sent:
                    if tok_id < window_start_tok:
                        mention_in_window = False
                elif sent_id == window_end_sent:
                    if tok_id > window_end_tok:
                        mention_in_window = False
        if mention_in_window:
            str_mentions.append(mention.text)

    return str_mentions

def get_by_sent_string_mentions(mentions):
    sent_string_mentions = {}
    seen_ent_ids = set()
    for mention in mentions:
        sent_id = mention.span[0].split("-")[0]
        if sent_id not in sent_string_mentions:
            sent_string_mentions[sent_id] = {"str_mention": [], "str_mention_coref_binary": [], "candidate_ana": []}
        sent_string_mentions[sent_id]["str_mention"].append(mention.text)
        if mention.ent_id in seen_ent_ids:
            sent_string_mentions[sent_id]["str_mention_coref_binary"].append(1)
        else:
            sent_string_mentions[sent_id]["str_mention_coref_binary"].append(0)
            seen_ent_ids.add(mention.ent_id)
        if "_candidate" in mention.infstat:
            sent_string_mentions[sent_id]["candidate_ana"].append(mention.text)

    return sent_string_mentions

def get_subtype_context(span, sentences, open_symbol, close_symbol, n=5):
    start_sent, start_tok = span[0].split("-")
    end_sent, end_tok = span[-1].split("-")
    start_sent = int(start_sent) - 1
    start_tok = int(start_tok) - 1
    end_tok = int(end_tok) - 1
    sent = copy.deepcopy(sentences[start_sent])
    sent[start_tok] = open_symbol + sent[start_tok]
    sent[end_tok] = sent[end_tok] + close_symbol
    earlier_sents = sentences[:start_sent]
    earlier_tokens = [token for sent in earlier_sents for token in sent]
    earlier_context_tokens = earlier_tokens[-n:]
    later_sents = sentences[start_sent+1:]
    later_tokens = [token for sent in later_sents for token in sent]
    later_context_sentence = later_tokens[:n+1]
    context = " ".join(earlier_context_tokens) + " " + " ".join(sent) + " " + " ".join(later_context_sentence)
    return context

def get_antec_mention(ante_mention_id, mentions):
    # return string mention of the antecedent mention given its id
    ante_mention_index = ante_mention_id - 1
    antec_mention_text = mentions[ante_mention_index].text
    return antec_mention_text

def get_antec_answers(ante_mention_id, mentions, entities):
    antec_answers = set()
    ante_mention_index = ante_mention_id - 1
    antec_ent_id = mentions[ante_mention_index].ent_id
    antec_coref_mention_ids = entities[antec_ent_id].coref_mention_ids
    for coref_mention_id in antec_coref_mention_ids:
        coref_mention_index = coref_mention_id - 1
        mention_text = mentions[coref_mention_index].text
        antec_answers.add(mention_text)
    return list(antec_answers)

def get_antecedent_sel_context(ana_span, sentences, mentions, context_window=150):
    ana_start_sent, ana_start_tok = ana_span[0].split("-")
    ana_end_sent, ana_end_tok = ana_span[-1].split("-")
    ana_start_sent = int(ana_start_sent) - 1
    ana_start_tok = int(ana_start_tok) - 1
    ana_end_tok = int(ana_end_tok) - 1
    ana_sent = copy.deepcopy(sentences[ana_start_sent])
    ana_sent[ana_start_tok] = "{{" + ana_sent[ana_start_tok]
    ana_sent[ana_end_tok] = ana_sent[ana_end_tok] + "}}"
    earlier_sents = sentences[:ana_start_sent]
    earlier_tokens = [token for sent in earlier_sents for token in sent]
    earlier_context_tokens = earlier_tokens[-context_window:]
    context = " ".join(earlier_context_tokens) + " " + " ".join(ana_sent)

    # get the sent-tok_id of the start and end of the context
    sentence_lengths = [len(sent) for sent in sentences]
    tokid2senttokid = {}
    running_total = 0
    for i, l in enumerate(sentence_lengths):
        for j in range(l):
            tokid2senttokid[running_total + j] = (i + 1, j + 1)  # (sent_id, tok_id) both 1-indexed
        running_total += l
    start_index = max(0, sum(len(sent) for sent in sentences[:ana_start_sent]) - context_window)
    end = sum(len(sent) for sent in sentences[:ana_start_sent]) + len(sentences[ana_start_sent])
    antec_left = start_index

    str_mentions = get_mentions_in_window(mentions, tokid2senttokid[antec_left], tokid2senttokid[end - 1])

    return context, str_mentions


def add_pair_distances(bridge_df, sentences, c, dist_list):
    for i, row in bridge_df.iterrows():
        ana_span = ast.literal_eval(row["ana_span"])
        ante_span = ast.literal_eval(row["ante_span"])
        ana_end_sent, ana_end_tok = ana_span[-1].split("-")
        ana_end_sent = int(ana_end_sent) - 1
        ana_end_tok = int(ana_end_tok)
        ante_start_sent, ante_start_tok = ante_span[0].split("-")
        ante_start_sent = int(ante_start_sent) - 1
        ante_start_tok = int(ante_start_tok)
        ana_index = sum(len(sent) for sent in sentences[:ana_end_sent]) + ana_end_tok
        ante_index = sum(len(sent) for sent in sentences[:ante_start_sent]) + ante_start_tok
        distance = ana_index - ante_index
        c.update([distance])
        dist_list.append(distance)
    return

# courtesy of my friend chatGPT
def sentence_with_context(sentences, mentions, buffer_size_left=10, buffer_size_right=10, antec_buffer_size=150):
    """
    Given a document as a list of sentences (each a list of tokens),
    return:
      1. list of sentence strings
      2. list of sentence strings with up to `buffer_size` tokens of context
         before and after from the entire document.
    """
    sentences_objs = []
    # Flatten the document into one long token list and track sentence boundaries
    all_tokens = [token for sent in sentences for token in sent]
    sentence_lengths = [len(sent) for sent in sentences]

    # make map from flattened token index to sentence token index
    tokid2senttokid = {}
    running_total = 0
    for i, l in enumerate(sentence_lengths):
        for j in range(l):
            tokid2senttokid[running_total + j] = (i + 1, j + 1)  # (sent_id, tok_id) both 1-indexed
        running_total += l

    # Compute start/end token indices for each sentence in flattened text
    starts = []
    ends = []
    running_total = 0
    for l in sentence_lengths:
        starts.append(running_total)
        ends.append(running_total + l)
        running_total += l

    # Build outputs
    for i, (start, end) in enumerate(zip(starts, ends)):
        sentence_values = {}
        # Sentence string
        sent_str = " ".join(all_tokens[start:end])
        sentence_values["text"] = sent_str

        # Context window (± buffer_size)
        left = max(0, start - buffer_size_left)
        right = min(len(all_tokens), end + buffer_size_right)
        context_str = " ".join(all_tokens[left:right])
        sentence_values["text_w_buffer"] = context_str
        #sentences_objs.append(sentence_values)

        # antecedent selection context window (up to antec_buffer_size before)
        antec_left = max(0, start - antec_buffer_size)
        antec_context_str = " ".join(all_tokens[antec_left:end])
        sentence_values["text_w_antec_buffer"] = antec_context_str

        antec_context_str_mentions = get_mentions_in_window(mentions, tokid2senttokid[antec_left], tokid2senttokid[end - 1])
        sentence_values["text_w_antec_buffer_str_mentions"] = antec_context_str_mentions

        sentences_objs.append(sentence_values)

    return sentences_objs

def get_tsv_sentences(file_path):
    sentences = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if "#Text=" in line:
                tokens = line[6:].split(" ")
                sentences.append(tokens)
    return sentences

def main(data_dirs, json_file):
    # make list of all tsv files in the directories
    file_list = []
    for directory in data_dirs:
        tsv_files = glob.glob(os.path.join(directory, "*.tsv"))
        file_list.extend(tsv_files)

    # load json file if it exists
    if os.path.exists(json_file):
        with open(json_file, "r") as jf:
            json_data = json.load(jf)
    else:
        json_data = {}

    # single file test
    #file_list = [file_list[0]]
    dis_count = Counter()
    distance_list = []

    for file_path in file_list:
        #file_path = "/Users/laurenlevine/Documents/GUMBridge_Efforts/other_data/stanza_mentions/gumbridge/dev/marked/GUM_bio_emperor_lel76_marked.tsv"
        doc_name = file_path.split("/")[-1].split(".")[0]
        document_sentences = get_tsv_sentences(file_path)
        document_text, mentions = process_tsv_v2(file_path)
        mentions, entities, _ = get_entity_information(mentions)
        bridge_df = make_bridge_pair_df(mentions, entities)
        # get by sent string_mentions and string_mentions_coref_binary
        by_sent_string_mentions = get_by_sent_string_mentions(mentions)
        # Process the data as needed and prepare for JSON output
        add_pair_distances(bridge_df, document_sentences, dis_count, distance_list)
        ana_marked_sents = copy.deepcopy(document_sentences)
        ana_ante_marked_sents = copy.deepcopy(document_sentences)
        subtypes = {}
        subtype_input = {}
        if doc_name not in json_data:
            json_data[doc_name] = {}
        json_data[doc_name]["text"] = document_text
        bridging_anaphora = {}
        antecedent_answers = {}
        antecedent_answer_mention = {}
        antecedent_texts = {}
        antecedent_texts_str_mentions = {}
        by_sent_ana_mentions = {}
        # for rows in bridge_df
        for i, row in bridge_df.iterrows():
            ana_span = ast.literal_eval(row["ana_span"])
            ante_span = ast.literal_eval(row["ante_span"])
            ana_mention_id = row["ana_mention_id"]
            ana_sent_id, ana_text = ana_span[0].split("-")[0], mentions[ana_mention_id - 1].text
            if ana_sent_id not in by_sent_ana_mentions:
                by_sent_ana_mentions[ana_sent_id] = []
            by_sent_ana_mentions[ana_sent_id].append(ana_text)
            ante_mention_id = row["ante_mention_id"]
            ante_answers = get_antec_answers(ante_mention_id, mentions, entities)
            antecedent_answers[i] = ante_answers
            antecedent_answer_mention[i] = get_antec_mention(ante_mention_id, mentions)
            bridgetype = row["bridgetype"]
            if bridgetype is None:
                bridgetype = "nosubtype"
            subtypes[i] = bridgetype
            ante_context = get_subtype_context(ante_span, document_sentences, "*", "*", n=50)
            ana_context = get_subtype_context(ana_span, document_sentences, "{{", "}}", n=50)
            subtype_input[i] = {"ante_text": ante_context, "ana_text": ana_context}
            antecedent_sel_context, antecedent_sel_context_str_mentions = get_antecedent_sel_context(ana_span, document_sentences, mentions)
            antecedent_texts[i] = antecedent_sel_context
            antecedent_texts_str_mentions[i] = antecedent_sel_context_str_mentions
            # mark ana in ana_marked_sents
            ana_start_sent, ana_start_tok = ana_span[0].split("-")
            ana_end_sent, ana_end_tok = ana_span[-1].split("-")
            ana_start_sent = int(ana_start_sent) - 1
            ana_start_tok = int(ana_start_tok) - 1
            ana_end_sent = int(ana_end_sent) - 1
            ana_end_tok = int(ana_end_tok) - 1
            # record anaphor string
            bridging_anaphora[i] = " ".join(document_sentences[ana_start_sent][ana_start_tok:ana_end_tok + 1]) #ana_ante_marked_sents
            # mark ana tokens
            ana_marked_sents[ana_start_sent][ana_start_tok] = "{{" + ana_marked_sents[ana_start_sent][ana_start_tok]
            ana_marked_sents[ana_end_sent][ana_end_tok] = ana_marked_sents[ana_end_sent][ana_end_tok] + "}}" + f"{i}"
            # mark ana and ante in ana_ante_marked_sents
            ana_ante_marked_sents[ana_start_sent][ana_start_tok] = "{{" + ana_ante_marked_sents[ana_start_sent][ana_start_tok]
            ana_ante_marked_sents[ana_end_sent][ana_end_tok] = ana_ante_marked_sents[ana_end_sent][ana_end_tok] + "}}" + f"{i}"
            ante_start_sent, ante_start_tok = ante_span[0].split("-")
            ante_end_sent, ante_end_tok = ante_span[-1].split("-")
            ante_start_sent = int(ante_start_sent) - 1
            ante_start_tok = int(ante_start_tok) - 1
            ante_end_sent = int(ante_end_sent) - 1
            ante_end_tok = int(ante_end_tok) - 1
            ana_ante_marked_sents[ante_start_sent][ante_start_tok] = "[[" + ana_ante_marked_sents[ante_start_sent][ante_start_tok]
            ana_ante_marked_sents[ante_end_sent][ante_end_tok] = ana_ante_marked_sents[ante_end_sent][ante_end_tok] + "]]" + f"{i}"
        sentences_w_context = sentence_with_context(document_sentences, mentions)
        # add by mention sentence string mentions to each sentence
        for i, sent_obj in enumerate(sentences_w_context):
            sent_id = str(i + 1)
            if sent_id in by_sent_string_mentions:
                sent_obj["str_mentions"] = by_sent_string_mentions[sent_id]["str_mention"]
                sent_obj["str_mention_coref_binary"] = by_sent_string_mentions[sent_id]["str_mention_coref_binary"]
                sent_obj["candidate_ana"] = by_sent_string_mentions[sent_id]["candidate_ana"]
            else:
                sent_obj["str_mentions"] = []
                sent_obj["str_mention_coref_binary"] = []
                sent_obj["candidate_ana"] = []
            if sent_id in by_sent_ana_mentions:
                sent_obj["actual_ana"] = by_sent_ana_mentions[sent_id]
            else:
                sent_obj["actual_ana"] = []
        json_data[doc_name]["sentences"] = sentences_w_context
        json_data[doc_name]["ana_marked_text"] = " ".join([" ".join(sent) for sent in ana_marked_sents])
        json_data[doc_name]["bridge_pair_marked_text"] = " ".join([" ".join(sent) for sent in ana_ante_marked_sents])
        json_data[doc_name]["subtypes"] = subtypes
        json_data[doc_name]["bridging_anaphora"] = bridging_anaphora
        json_data[doc_name]["antecedent_texts"] = antecedent_texts
        json_data[doc_name]["antecedent_texts_str_mentions"] = antecedent_texts_str_mentions
        json_data[doc_name]["antecedent_answers"] = antecedent_answers
        json_data[doc_name]["antecedent_answer_mention"] = antecedent_answer_mention
        json_data[doc_name]["subtype_input"] = subtype_input
        #break

    # write to json file
    with open(json_file, "w") as jf:
        json.dump(json_data, jf, indent=4)
    #max_count = max(dis_count.keys())
    #print(max_count)
    #p = np.percentile(distance_list, 90)
    #print(p)

    return

if __name__ == "__main__":
    data_dirs = ["../data/test/"] # list of data dir paths to process
    json_file = "test.json" # name of new output json file of preprocessed data
    main(data_dirs, json_file)

