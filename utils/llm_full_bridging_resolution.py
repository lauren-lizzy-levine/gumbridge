import os
import glob

class Mention:

    def __init__(self, mention_id, token, entity_type, token_index):
        self.id = mention_id
        self.text = token
        self.etype = entity_type
        self.span  = [token_index]
        self.infstat = None
        self.coref = []
        self.bridge = []
        self.bridgetype = None
        self.ent_id = None

class Entity:

        def __init__(self, ent_id, text, men_id):
            self.id = ent_id
            self.first_mention_text = text
            self.coref_mention_ids = [men_id]

def split_annotation(annotation_string):
    annotation_list = []
    seen_ent_ids = []
    if annotation_string == "_":
        return annotation_list
    annotations = annotation_string.split("|")
    for annotation in annotations:
        label, remainder = annotation.split("[")
        ent_id = remainder.split("]")[0]
        while ent_id in seen_ent_ids:
            ent_id += "*"
        seen_ent_ids.append(ent_id)
        annotation_list.append({"id": ent_id, "label": label})
    return annotation_list

def process_tsv(file_path, version=None):
    """
    :param version: version indicating annotation types included in tsv
    :param file_path: path of tsv file to be processed
    :return:    document_text: string of document text
                mentions: list of entity mention objects from document
    """
    # get document text, first mention entities list, bridging anaphora list
    # start with getting an object representation of the mentions in the tsv
    with open(file_path, "r") as f:
        tsv_lines = f.readlines()

    mentions = []
    tokens = []

    for line in tsv_lines:
        if line.startswith("#") or not line.strip():
            continue

        columns = line.strip().split("\t")

        token_index = columns[0]
        token = columns[2]
        entity_types = columns[3]
        info_stats = columns[4]

        if version == "bridgetype":
            # data from after bridgetype annotation
            bridgetypes = columns[6]
            coref_types = columns[8]
            coref_links = columns[9]
        else:
            # data from _build/src/tsv
            coref_types = columns[7]
            coref_links = columns[8]
            bridgetypes = None

        tokens.append(token)

        ent_types_list = split_annotation(entity_types)
        for entity_type in ent_types_list:
            mention_id = int(entity_type["id"])
            mention_index = mention_id - 1
            label = entity_type["label"]
            if mention_index < len(mentions):
                # if the current token is adjacent to the previous token for the entity,
                # add it to the ent_text entry and update the span
                mentions[mention_index].text += " " + token
                mentions[mention_index].span.append(token_index)
            else:
                new_mention = Mention(mention_id, token, label, token_index)
                mentions.append(new_mention)

        info_stat_list = split_annotation(info_stats)
        for info_stat in info_stat_list:
            mention_id = int(info_stat["id"])
            mention_index = mention_id - 1
            label = info_stat["label"]
            if mentions[mention_index].infstat is None:
                mentions[mention_index].infstat = label

        if bridgetypes:
            bridgetype_list = split_annotation(bridgetypes)
            for bridgetype in bridgetype_list:
                mention_id = int(bridgetype["id"])
                mention_index = mention_id - 1
                label = bridgetype["label"]
                if mentions[mention_index].bridgetype is None:
                    mentions[mention_index].bridgetype = label

        coref_types_list = coref_types.split("|")
        coref_links_list = coref_links.split("|")
        for coref_type, coref_link in zip(coref_types_list, coref_links_list):
            if coref_type != "_":
                mention_id_links = coref_link.split("[")[1].split("]")[0]
                link_men_id, curr_men_id = mention_id_links.split("_")
                curr_men_idx = int(curr_men_id) - 1
                if "bridge" in coref_type:
                    # print("tsv bridge")
                    mentions[curr_men_idx].bridge.append(int(link_men_id))
                else:
                    # coref instance
                    mentions[curr_men_idx].coref.append(int(link_men_id))

    document_text = " ".join(tokens)

    return document_text, mentions

def get_entity_information(mentions):
    """
    :param mentions: list of entity mention objects
    :return: mentions: list of entity mention objects from document, now with entity ids
             entities: list of entity objects from document (id, first mention test, coref mentions)
             bridging_anaphora_ent_ids: list of entity ids that are annotated as bridging anaphors in the tsv
    """
    # make entity objects
    entities = []
    entity_mention_map = {}
    for mention in mentions:
        if mention.id in entity_mention_map:
            ent_id = entity_mention_map[mention.id]
            entities[ent_id].coref_mention_ids.append(mention.id)
        else:
            # this mention id has not been named in another entity's coref chain yet
            # this is a new entity
            ent_id = len(entities)
            new_entity = Entity(ent_id, mention.text, mention.id)
            entities.append(new_entity)
        for mention_id in mention.coref:
            entity_mention_map[mention_id] = ent_id

    # add entity ids to mentions
    for entity in entities:
        for men_id in entity.coref_mention_ids:
            mention_index = men_id - 1
            mentions[mention_index].ent_id = entity.id

    # compile bridging anaphora list from tsv annotations
    # go through mentions, for each men_id in bridge field, get the ent_id of that mention, it is a bridging anaphor
    bridging_anaphora_ent_ids = []
    for mention in mentions:
        for men_id in mention.bridge:
            mention_index =  men_id - 1
            bridging_entity = mentions[mention_index].ent_id
            bridging_anaphora_ent_ids.append(bridging_entity)

    return mentions, entities, bridging_anaphora_ent_ids

def process_tsv_v2(file_path, version=None):
    """
    :param version: version indicating annotation types included in tsv
    :param file_path: path of tsv file to be processed
    :return:    document_text: string of document text
                mentions: list of entity mention objects from document
    This is version 2 of the process_tsv function,
    updated after the bridgetype annotation was added as an edge annotation in the tsv.
    """
    # get document text, first mention entities list, bridging anaphora list
    # start with getting an object representation of the mentions in the tsv
    with open(file_path, "r") as f:
        tsv_lines = f.readlines()

    mentions = []
    tokens = []
    # Need to make dictionary of bridge labels for the anaphora and then add them to the mentions at the end
    bridgetype_dict = {} # dictionary to hold bridgetype labels for mentions mention_id -> bridgetype label

    for line in tsv_lines:
        if line.startswith("#") or not line.strip():
            continue

        columns = line.strip().split("\t")

        # bad temp fix for messed up test data
        if len(columns) == 7:
            columns.append("_")
            columns.append("_")

        token_index = columns[0]
        token = columns[2]
        entity_types = columns[3]
        info_stats = columns[4]
        coref_types = columns[7]
        coref_links = columns[8]

        tokens.append(token)

        ent_types_list = split_annotation(entity_types)
        for entity_type in ent_types_list:
            mention_id = int(entity_type["id"])
            mention_index = mention_id - 1
            label = entity_type["label"]
            if mention_index < len(mentions): # checking of mention already encountered, mention_index < len(mentions)
                # if the current token is adjacent to the previous token for the entity,
                # add it to the ent_text entry and update the span
                mentions[mention_index].text += " " + token
                mentions[mention_index].span.append(token_index)
            else:
                new_mention = Mention(mention_id, token, label, token_index)
                mentions.append(new_mention)

        info_stat_list = split_annotation(info_stats)
        for info_stat in info_stat_list:
            mention_id = int(info_stat["id"])
            mention_index = mention_id - 1
            label = info_stat["label"]
            if mentions[mention_index].infstat is None:
                mentions[mention_index].infstat = label

        coref_types_list = coref_types.split("|")
        coref_links_list = coref_links.split("|")
        for coref_type, coref_link in zip(coref_types_list, coref_links_list):
            if coref_type != "_":
                mention_id_links = coref_link.split("[")[1].split("]")[0]
                link_men_id, curr_men_id = mention_id_links.split("_")
                curr_men_idx = int(curr_men_id) - 1
                if "bridge" in coref_type:
                    # print("tsv bridge")
                    if ":" in coref_type:
                        bridgetype = coref_type.split(":")[1]
                        bridgetype_dict[int(link_men_id)] = bridgetype
                    mentions[curr_men_idx].bridge.append(int(link_men_id))
                else:
                    # coref instance
                    mentions[curr_men_idx].coref.append(int(link_men_id))

    # bridgetype annotation
    for mention_id in bridgetype_dict:
        mention_index = mention_id - 1
        if mention_index < len(mentions):
            mentions[mention_index].bridgetype = bridgetype_dict[mention_id]

    document_text = " ".join(tokens)

    return document_text, mentions

def main():
    # let's start by reading a document and pulling out the text, mentions, entities, and bridging anaphora
    file_list = [""] # list of files
    #file_list = glob.glob(os.path.join(input_dir, "*.tsv"))
    ent_count = 0
    tok_count = 0
    bridge_ana_count = 0
    for document_path in file_list:
        doc_name = os.path.splitext(os.path.basename(document_path))[0]
        document_text, mentions = process_tsv(document_path)
        mentions, entities, bridging_anaphora_ent_ids = get_entity_information(mentions)
        ent_count += len(entities)
        bridge_ana_count += len(bridging_anaphora_ent_ids)
        tok_count += len(document_text.split(" "))
    print(ent_count / len(file_list))
    print(bridge_ana_count / len(file_list))
    print(tok_count / len(file_list))


if __name__ == "__main__":
    main()