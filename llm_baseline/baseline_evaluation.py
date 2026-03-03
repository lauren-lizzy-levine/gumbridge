import json
from collections import Counter
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def abbreviate_labels(label_list):
    new_labels = []
    for label in label_list:
        if label == "comparison":
            new_labels.append("other")
        elif label == "comparison-relative":
            new_labels.append("comp-rel")
        elif label == "comparison-sense":
            new_labels.append("comp-sen")
        elif label == "comparison-time":
            new_labels.append("comp-time")
        elif label == "entity-associative":
            new_labels.append("ent-assoc")
        elif label == "entity-meronomy":
            new_labels.append("ent-mero")
        elif label == "entity-property":
            new_labels.append("ent-prop")
        elif label == "entity-resultative":
            new_labels.append("ent-result")
        elif label == "set-member":
            new_labels.append("set-mem")
        elif label == "set-span-interval":
            new_labels.append("set-span")
        elif label == "set-subset":
            new_labels.append("set-sub")
        else:
            new_labels.append(label)

    return new_labels

def make_confusion_matrix(gold_bridgetype_list, pred_bridgetype_list, name=""):
    singled_admin_bridgetype = abbreviate_labels(gold_bridgetype_list)
    singled_anno_bridgetype = abbreviate_labels(pred_bridgetype_list)
    labels = sorted(set(singled_admin_bridgetype + singled_anno_bridgetype))  # Get all unique labels
    conf_matrix = confusion_matrix(singled_admin_bridgetype, singled_anno_bridgetype, labels=labels)
    cm_df = pd.DataFrame(conf_matrix, index=labels,
                         columns=labels)

    # Replace 0s with empty strings for annotations
    annot_labels = np.where(conf_matrix == 0, "", conf_matrix)

    # Plot the heatmap
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_df, annot=annot_labels, fmt="", cmap="Blues", cbar=False, linewidths=0.5)
    plt.title("GPT-5 Performance on Bridging Subtypes")
    plt.ylabel("Gold Label")
    plt.xlabel("GPT-5 Label")
    plt.xticks(rotation=60, ha="right")  # Rotate x-axis labels for better visibility
    plt.yticks(rotation=0)  # Keep y-axis labels horizontal
    plt.tight_layout()
    # save off confusion matrix in pilot1_results dictionary
    file_name = "/Users/laurenlevine/Documents/GUMBridge_Efforts/pythonProject/llm_baseline_2/" + "cm_gpt5_trimmed" + name + ".png"
    plt.savefig(file_name)
    return

def get_subtype_lists(instance_list):
    gold_list = []
    pred_list = []
    for gold_id, pred_subtype, gold_subtype in instance_list:
        gold_labels = set(gold_subtype.split(";"))
        if pred_subtype is None:
            continue
        pred_labels = set(pred_subtype.split(";"))
        if len(gold_labels) == 1 and len(pred_labels) == 1:
            # if both labels are single, just add them
            gold_list.append(gold_labels.pop())
            pred_list.append(pred_labels.pop())
        else:
            # Get intersection and non overlapping labels from the sets above
            # store in 3 variables: intersection, admin_only, anno_only
            intersection = gold_labels.intersection(pred_labels)
            gold_only = gold_labels - intersection
            pred_only = pred_labels - intersection
            # add individual entries for each label
            gold_only_list = list(gold_only)
            pred_only_list = list(pred_only)
            if len(gold_only_list) < len(pred_only_list):
                gold_only_list.extend(["none"] * (len(pred_only_list) - len(gold_only_list)))
            elif len(pred_only_list) < len(gold_only_list):
                pred_only_list.extend(["none"] * (len(gold_only_list) - len(pred_only_list)))

            if intersection:
                for label in intersection:
                    gold_list.append(label)
                    pred_list.append(label)
                # commenting out to see what it would be like to count as correct if at least 1 label matches
            for admin_label, anno_label in zip(gold_only_list, pred_only_list):
                gold_list.append(admin_label)
                pred_list.append(anno_label)
    """
    for gold_id, pred_subtype, gold_subtype in instance_list:
        gold_types = gold_subtype.split(";")
        pred_types = pred_subtype.split(";")
        all_types = set.union(set(gold_types), set(pred_types))
        for t in all_types:
            if t not in gold_types:
                gold_list.append("missed")
            else:
                gold_list.append(t)
            if t not in pred_types:
                pred_list.append("missed")
            else:
                pred_list.append(t)
    """
    return gold_list, pred_list

def compare_antecedent_selection_strings(pred_ante, gold_ante):
    matched_count, missed_count = 0, 0
    # matched is tp
    # fn is anaphor fns, correct anaphors with wrong antecedents (minus no antecedent predictions??)
    # fp is anaphor fps, correct anaphors with wrong antecedents (minus no antecedent predictions??)
    fp_count, fn_count = 0, 0
    for ana_id in gold_ante:
        if ana_id in pred_ante and pred_ante[ana_id] in gold_ante[ana_id]:
            matched_count += 1
        else:
            missed_count += 1
            if ana_id in pred_ante and pred_ante[ana_id] not in gold_ante[ana_id]:
                fp_count += 1
                fn_count += 1

    return matched_count, missed_count, fp_count, fn_count

def compare_anaphor_recognition_strings(pred_ana, gold_ana):
    # pred ana is list of string and gold ana is dictionary of strings
    gold_ana_list = list(gold_ana.values())
    c_pred = Counter(pred_ana)
    c_gold = Counter(gold_ana_list)

    # True positives = sum of the min count for each overlapping element
    tp_counter = c_gold & c_pred
    true_positive_instances = list(tp_counter.elements())
    true_positive_count = len(true_positive_instances)

    # False positives = items in pred not matched in gold
    fp_counter = c_pred - c_gold
    false_positive_instances = list(fp_counter.elements())
    false_positive_count = len(false_positive_instances)

    # False negatives = items in gold not matched in pred
    fn_counter = c_gold - c_pred
    false_negatives_instances = list(fn_counter.elements())
    false_negative_count = len(false_negatives_instances)

    return true_positive_count, false_positive_count, false_negative_count, true_positive_instances, false_positive_instances, false_negatives_instances

def compare_bridgetypes(gold_subtypes, pred_subtypes):
    matched_count = 0
    missed_count = 0
    fp_count = 0
    complete_matched_count = 0
    any_missed_count = 0
    instances = []
    for gold_id in gold_subtypes:
        gold_types = set(gold_subtypes[gold_id].split(";"))
        if gold_id in pred_subtypes:
            pred_types = set(pred_subtypes[gold_id].split(";"))
            matched_types = gold_types.intersection(pred_types)
            missed_types = gold_types - pred_types
            fp_types = pred_types - gold_types
            if len(matched_types) > 0:
                matched_count += len(matched_types)
            if len(missed_types) > 0:
                missed_count += len(missed_types)
            if len(fp_types) > 0:
                fp_count += len(fp_types)
            if len(missed_types) > 0:
                any_missed_count += 1
            else:
                complete_matched_count += 1
            instances.append((gold_id, pred_subtypes[gold_id], gold_subtypes[gold_id]))
        else:
            missed_count += len(gold_types)
            any_missed_count += 1
            instances.append((gold_id, None, gold_subtypes[gold_id]))

    return complete_matched_count, any_missed_count, matched_count, fp_count, missed_count, instances

def main(pred_data, gold_data, agg_output_path, indiv_output_path, genre_output_path):
    evaluation_results = {}
    evaluation_results_genre = {}
    evaluation_results_individual = {}
    for doc in pred_data:
        print(doc)
        evaluation_results_individual[doc] = {}
        for model in pred_data[doc]:
            if doc in gold_data:
                evaluation_results_individual[doc][model] = {"anaphor_recognition":{}, "antecedent_selection":{}, "subtype_classification":{}}
                # compare anaphor recognition
                if "bridging_anaphora" not in pred_data[doc][model]:
                    continue
                pred_ana = pred_data[doc][model]["bridging_anaphora"]
                gold_ana = gold_data[doc]["bridging_anaphora"]
                ana_tp_count, ana_fp_count, ana_fn_count, ana_tp_instances, ana_fp_instances, ana_fn_instances = (
                    compare_anaphor_recognition_strings(pred_ana, gold_ana))
                evaluation_results_individual[doc][model]["anaphor_recognition"] = {"counts": {"true_positives": ana_tp_count, "false_positives": ana_fp_count, "false_negatives": ana_fn_count},
                                                                                   "instances": {"true_positives": ana_tp_instances, "false_positives": ana_fp_instances, "false_negatives": ana_fn_instances}}
                if "antecedent_selection" not in pred_data[doc][model]:
                    continue
                pred_ante = pred_data[doc][model]["antecedent_selection"]
                gold_ante = gold_data[doc]["antecedent_answers"]
                ante_matched, ante_missed, ante_fp, ante_fn = compare_antecedent_selection_strings(pred_ante, gold_ante)
                ante_fp += evaluation_results_individual[doc][model]["anaphor_recognition"]["counts"]["false_positives"]
                ante_fn += evaluation_results_individual[doc][model]["anaphor_recognition"]["counts"]["false_negatives"]
                evaluation_results_individual[doc][model]["antecedent_selection"] = {"counts": {"matched": ante_matched, "missed": ante_missed, "false_positives": ante_fp, "false_negatives": ante_fn}}

                if "subtype_classification" not in pred_data[doc][model]:
                    continue
                pred_subtypes = pred_data[doc][model]["subtype_classification"]
                gold_subtypes = gold_data[doc]["subtypes"]
                subtypes_complete_matched_count, subtypes_any_missed_count, subtypes_matched_count, subtypes_fp_count, subtypes_missed_count, subtype_pair_instances = compare_bridgetypes(
                    gold_subtypes, pred_subtypes)
                evaluation_results_individual[doc][model]["subtype_classification"] = {"counts": {"true_positives": subtypes_matched_count, "false_positives": subtypes_fp_count, "false_negatives": subtypes_missed_count,
                                                                                             "complete_matched": subtypes_complete_matched_count, "any_missed": subtypes_any_missed_count}, "instances": subtype_pair_instances}

    # aggregate results
    for doc in evaluation_results_individual:
        for model in evaluation_results_individual[doc]:
            genre = doc.split("_")[1]
            if model not in evaluation_results:
                evaluation_results[model] = {"anaphor_recognition": {"counts": {"true_positives": 0, "false_positives": 0, "false_negatives": 0}},
                                             "antecedent_selection": {"counts": {"matched": 0, "missed": 0, "false_positives": 0, "false_negatives": 0}},
                                             "subtype_classification": {
                                                 "counts": {"true_positives": 0, "false_positives": 0,
                                                            "false_negatives": 0, "complete_matched": 0,
                                                            "any_missed": 0}, "instances": {"gold": [], "pred": []}}}
            # by genre
            if model not in evaluation_results_genre:
                evaluation_results_genre[model] = {}
            if genre not in evaluation_results_genre[model]:
                evaluation_results_genre[model][genre] = {"anaphor_recognition": {"counts": {"true_positives": 0, "false_positives": 0, "false_negatives": 0}},
                                                          "antecedent_selection": {"counts": {"matched": 0, "missed": 0, "false_positives": 0, "false_negatives": 0}},
                                                          "subtype_classification": {
                                                              "counts": {"true_positives": 0, "false_positives": 0,
                                                                         "false_negatives": 0, "complete_matched": 0,
                                                                         "any_missed": 0}, "instances": {"gold": [], "pred": []}}}

            # anaphor recognition
            ana_counts = evaluation_results_individual[doc][model]["anaphor_recognition"]["counts"]
            evaluation_results[model]["anaphor_recognition"]["counts"]["true_positives"] += ana_counts["true_positives"]
            evaluation_results[model]["anaphor_recognition"]["counts"]["false_positives"] += ana_counts["false_positives"]
            evaluation_results[model]["anaphor_recognition"]["counts"]["false_negatives"] += ana_counts["false_negatives"]
            # by genre
            evaluation_results_genre[model][genre]["anaphor_recognition"]["counts"]["true_positives"] += ana_counts["true_positives"]
            evaluation_results_genre[model][genre]["anaphor_recognition"]["counts"]["false_positives"] += ana_counts["false_positives"]
            evaluation_results_genre[model][genre]["anaphor_recognition"]["counts"]["false_negatives"] += ana_counts["false_negatives"]
            # antecedent selection
            if "counts" in evaluation_results_individual[doc][model]["antecedent_selection"]:
                ante_counts = evaluation_results_individual[doc][model]["antecedent_selection"]["counts"]
                evaluation_results[model]["antecedent_selection"]["counts"]["matched"] += ante_counts["matched"]
                evaluation_results[model]["antecedent_selection"]["counts"]["missed"] += ante_counts["missed"]
                evaluation_results[model]["antecedent_selection"]["counts"]["false_positives"] += ante_counts["false_positives"]
                evaluation_results[model]["antecedent_selection"]["counts"]["false_negatives"] += ante_counts["false_negatives"]
                # by genre
                evaluation_results_genre[model][genre]["antecedent_selection"]["counts"]["matched"] += ante_counts["matched"]
                evaluation_results_genre[model][genre]["antecedent_selection"]["counts"]["missed"] += ante_counts["missed"]
                evaluation_results_genre[model][genre]["antecedent_selection"]["counts"]["false_positives"] += ante_counts["false_positives"]
                evaluation_results_genre[model][genre]["antecedent_selection"]["counts"]["false_negatives"] += ante_counts["false_negatives"]
            # subtype classification
            if "counts" in evaluation_results_individual[doc][model]["subtype_classification"]:
                subtype_counts = evaluation_results_individual[doc][model]["subtype_classification"]["counts"]
                evaluation_results[model]["subtype_classification"]["counts"]["true_positives"] += subtype_counts["true_positives"]
                evaluation_results[model]["subtype_classification"]["counts"]["false_positives"] += subtype_counts["false_positives"]
                evaluation_results[model]["subtype_classification"]["counts"]["false_negatives"] += subtype_counts["false_negatives"]
                evaluation_results[model]["subtype_classification"]["counts"]["complete_matched"] += subtype_counts["complete_matched"]
                evaluation_results[model]["subtype_classification"]["counts"]["any_missed"] += subtype_counts["any_missed"]
                # by genre
                evaluation_results_genre[model][genre]["subtype_classification"]["counts"]["true_positives"] += subtype_counts["true_positives"]
                evaluation_results_genre[model][genre]["subtype_classification"]["counts"]["false_positives"] += subtype_counts["false_positives"]
                evaluation_results_genre[model][genre]["subtype_classification"]["counts"]["false_negatives"] += subtype_counts["false_negatives"]
                evaluation_results_genre[model][genre]["subtype_classification"]["counts"]["complete_matched"] += subtype_counts["complete_matched"]
                evaluation_results_genre[model][genre]["subtype_classification"]["counts"]["any_missed"] += subtype_counts["any_missed"]
                # make kappa input list from instances
                gold_sub_list, pred_sub_list = get_subtype_lists(evaluation_results_individual[doc][model]["subtype_classification"]["instances"])
                evaluation_results[model]["subtype_classification"]["instances"]["gold"] += gold_sub_list
                evaluation_results[model]["subtype_classification"]["instances"]["pred"] += pred_sub_list
                # by genre
                evaluation_results_genre[model][genre]["subtype_classification"]["instances"]["gold"] += gold_sub_list
                evaluation_results_genre[model][genre]["subtype_classification"]["instances"]["pred"] += pred_sub_list


    # calculate precision, recall, f1 for each task
    for model in evaluation_results:
        # anaphor recognition
        ana_tp = evaluation_results[model]["anaphor_recognition"]["counts"]["true_positives"]
        ana_fp = evaluation_results[model]["anaphor_recognition"]["counts"]["false_positives"]
        ana_fn = evaluation_results[model]["anaphor_recognition"]["counts"]["false_negatives"]
        ana_precision = ana_tp / (ana_tp + ana_fp) if (ana_tp + ana_fp) > 0 else 0.0
        ana_recall = ana_tp / (ana_tp + ana_fn) if (ana_tp + ana_fn) > 0 else 0.0
        ana_f1 = 2 * (ana_precision * ana_recall) / (ana_precision + ana_recall) if (ana_precision + ana_recall) > 0 else 0.0
        evaluation_results[model]["anaphor_recognition"]["metrics"] = {"precision": ana_precision, "recall": ana_recall, "f1": ana_f1}
        # antecedent selection
        matched = evaluation_results[model]["antecedent_selection"]["counts"]["matched"]
        missed = evaluation_results[model]["antecedent_selection"]["counts"]["missed"]
        ante_accuracy = matched / (matched + missed) if (matched + missed) > 0 else 0.0
        evaluation_results[model]["antecedent_selection"]["metrics"] = {"accuracy": ante_accuracy}
        ante_tp = matched
        ante_fp = evaluation_results[model]["antecedent_selection"]["counts"]["false_positives"]
        ante_fn = evaluation_results[model]["antecedent_selection"]["counts"]["false_negatives"]
        ante_precision = ante_tp / (ante_tp + ante_fp) if (ante_tp + ante_fp) > 0 else 0.0
        ante_recall = ante_tp / (ante_tp + ante_fn) if (ante_tp + ante_fn) > 0 else 0.0
        ante_f1 = 2 * (ante_precision * ante_recall) / (ante_precision + ante_recall) if (ante_precision + ante_recall) > 0 else 0.0
        evaluation_results[model]["antecedent_selection"]["metrics"].update({"precision": ante_precision, "recall": ante_recall, "f1": ante_f1})

        # subtype cat
        type_complete_matched = evaluation_results[model]["subtype_classification"]["counts"]["complete_matched"]
        subtypes_any_missed = evaluation_results[model]["subtype_classification"]["counts"]["any_missed"]
        type_accuracy = type_complete_matched / (type_complete_matched + subtypes_any_missed) if (type_complete_matched + subtypes_any_missed) > 0 else 0.0
        gold_bridgetype_list, pred_bridgetype_list = evaluation_results[model]["subtype_classification"]["instances"]["gold"], evaluation_results[model]["subtype_classification"]["instances"]["pred"]
        bridgetype_kappa = cohen_kappa_score(gold_bridgetype_list, pred_bridgetype_list)
        evaluation_results[model]["subtype_classification"]["metrics"] = {"accuracy": type_accuracy, "kappa": bridgetype_kappa}
        subtype_tp = evaluation_results[model]["subtype_classification"]["counts"]["true_positives"]
        subtype_fp = evaluation_results[model]["subtype_classification"]["counts"]["false_positives"]
        subtype_fn = evaluation_results[model]["subtype_classification"]["counts"]["false_negatives"]
        subtype_precision = subtype_tp / (subtype_tp + subtype_fp) if (subtype_tp + subtype_fp) > 0 else 0.0
        subtype_recall = subtype_tp / (subtype_tp + subtype_fn) if (subtype_tp + subtype_fn) > 0 else 0.0
        subtype_f1 = 2 * (subtype_precision * subtype_recall) / (subtype_precision + subtype_recall) if (subtype_precision + subtype_recall) > 0 else 0.0
        evaluation_results[model]["subtype_classification"]["metrics"].update(
            {"precision": subtype_precision, "recall": subtype_recall, "f1": subtype_f1})
        #if "gpt" in model:
        #    # add confusion matrix for gpt models
        #    make_confusion_matrix(gold_bridgetype_list, pred_bridgetype_list)
        # remove bridgetype instances to save space
        evaluation_results[model]["subtype_classification"].pop("instances", None)

    # calculate precision, recall, f1 for each task by genre
    for model in evaluation_results_genre:
        for genre in evaluation_results_genre[model]:
            # anaphor recognition
            ana_tp = evaluation_results_genre[model][genre]["anaphor_recognition"]["counts"]["true_positives"]
            ana_fp = evaluation_results_genre[model][genre]["anaphor_recognition"]["counts"]["false_positives"]
            ana_fn = evaluation_results_genre[model][genre]["anaphor_recognition"]["counts"]["false_negatives"]
            ana_precision = ana_tp / (ana_tp + ana_fp) if (ana_tp + ana_fp) > 0 else 0.0
            ana_recall = ana_tp / (ana_tp + ana_fn) if (ana_tp + ana_fn) > 0 else 0.0
            ana_f1 = 2 * (ana_precision * ana_recall) / (ana_precision + ana_recall) if (ana_precision + ana_recall) > 0 else 0.0
            evaluation_results_genre[model][genre]["anaphor_recognition"]["metrics"] = {"precision": ana_precision, "recall": ana_recall, "f1": ana_f1}
            # antecedent selection
            matched = evaluation_results_genre[model][genre]["antecedent_selection"]["counts"]["matched"]
            missed = evaluation_results_genre[model][genre]["antecedent_selection"]["counts"]["missed"]
            ante_accuracy = matched / (matched + missed) if (matched + missed) > 0 else 0.0
            evaluation_results_genre[model][genre]["antecedent_selection"]["metrics"] = {"accuracy": ante_accuracy}
            ante_tp = matched
            ante_fp = evaluation_results_genre[model][genre]["antecedent_selection"]["counts"]["false_positives"]
            ante_fn = evaluation_results_genre[model][genre]["antecedent_selection"]["counts"]["false_negatives"]
            ante_precision = ante_tp / (ante_tp + ante_fp) if (ante_tp + ante_fp) > 0 else 0.0
            ante_recall = ante_tp / (ante_tp + ante_fn) if (ante_tp + ante_fn) > 0 else 0.0
            ante_f1 = 2 * (ante_precision * ante_recall) / (ante_precision + ante_recall) if (ante_precision + ante_recall) > 0 else 0.0
            evaluation_results_genre[model][genre]["antecedent_selection"]["metrics"].update(
                {"precision": ante_precision, "recall": ante_recall, "f1": ante_f1})

            # subtype cat
            type_complete_matched = evaluation_results_genre[model][genre]["subtype_classification"]["counts"]["complete_matched"]
            subtypes_any_missed = evaluation_results_genre[model][genre]["subtype_classification"]["counts"]["any_missed"]
            type_accuracy = type_complete_matched / (type_complete_matched + subtypes_any_missed) if (type_complete_matched + subtypes_any_missed) > 0 else 0.0
            gold_bridgetype_list, pred_bridgetype_list = evaluation_results_genre[model][genre]["subtype_classification"]["instances"]["gold"], evaluation_results_genre[model][genre]["subtype_classification"]["instances"]["pred"]
            bridgetype_kappa = cohen_kappa_score(gold_bridgetype_list, pred_bridgetype_list)
            evaluation_results_genre[model][genre]["subtype_classification"]["metrics"] = {"accuracy": type_accuracy, "kappa": bridgetype_kappa}
            #if "gpt" in model:
            #    # add confusion matrix for gpt models
            #    make_confusion_matrix(gold_bridgetype_list, pred_bridgetype_list, "_" + genre)
            # remove bridgetype instances to save space
            evaluation_results_genre[model][genre]["subtype_classification"].pop("instances", None)

    # write both evaluation_results and evaluation_results_individual to json files
    with open(agg_output_path, "w") as af:
        json.dump(evaluation_results, af, indent=4)
    with open(indiv_output_path, "w") as inf:
        json.dump(evaluation_results_individual, inf, indent=4)
    with open(genre_output_path, "w") as gf:
        json.dump(evaluation_results_genre, gf, indent=4)

    return

if __name__ == "__main__":
    gold_file_path = "" # input should be output json file from preprocessing step
    model_pred_file_path = "" # input should be output json file from llm query step
    indiv_output_path = "" # name of new output json file for individual document results
    agg_output_path = "" # name of new output json file for aggregate results
    genre_output_path = "" # name of new output json file for aggregate results by genre
    with open(gold_file_path, "r") as gf:
        gold_json_data = json.load(gf)
    with open(model_pred_file_path, "r") as mf:
        model_json_data = json.load(mf)
    main(model_json_data, gold_json_data, agg_output_path, indiv_output_path, genre_output_path)
