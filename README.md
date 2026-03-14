# GUMBridge v1

Repository for the [GUMBridge corpus]((https://arxiv.org/abs/2512.07134)) for varieties of bridging anaphora. 

GUMBridge is an extended bridging layer for [the Georgetown University Multilayer (GUM) corpus](https://gucorpling.org/gum). 
As of GUM version 12, the extended bridging coverage of GUMBridge has been merged into [the main distribution of GUM](https://github.com/amir-zeldes/gum).

This repository contains release data of GUMBridge, covering 24 written and spoken English text types:

Main genres: (available in train/dev/test)

- academic writing
- biographies
- courtroom transcripts
- essays
- fiction
- how-to guides
- interviews
- letters
- news
- online forum discussions
- podcasts
- political speeches
- spontaneous face to face conversations
- textbooks
- travel guides
- vlogs

Out-of-domain test genres: (test2 partition):

- dictionary entries
- live esports commentary
- legal documents
- medical notes
- poetry
- mathematical proofs
- course syllabuses
- threat letters

## Bridging Annotation Guidelines

A full version of the annotation guidelines used for the bridging annotation in GUMBridge is available in the ```documentation``` directory. 

A truncated version of the annotation instructions is also available on the [GUM wiki](https://wiki.gucorpling.org/gum/entities).

## Demo

Check out our [web demo](https://gucorpling.org/gitdox/GUMBridge/spannotator.html) of the annotation interface for bridging annotation used in the creation of the GUMBridge corpus!

The demo imports/exports the tsv format described below.

Instructions on using the demo annotation interface can be found in the ```documentation``` directory.

The full corpus annotation was conducted using [GitDox](https://github.com/gucorpling/gitdox) (dev_bridging branch).

## Splits

GUMBridge follows the splits of GUM v12, which reserves 2 documents from each genre for dev and test (total: 32 test documents, 32 dev documents). 
An additional out-of-domain test2 partition is available with 26 documents from the [GENTLE corpus](https://gucorpling.org/gum/cite_gentle.html), representing 8 additional 'extreme' genres (which are not present in any other partition).
See splits.md for the official train, dev, test, and test2 partitions.

## Data Format

The GUMBridge entity annotations are given in the WebAnno .tsv format, including 5 summaries, entity type, graded salience and information status annotations, Wikification, **bridging**, split antecedent and singleton entities.
This follows the format of the src entity tsv files in the GUM corpus.

A description of how to interpret the bridging annotations follows below.
Please refer to [the GUM corpus](https://github.com/amir-zeldes/gum) for a descriptions of the other entity annotations included with the data.

### Interpreting the bridging annotations:

In the tsv file, each token is on a separate line with annotations delineated by tabs. 
The right most column gives an edge between 2 entities in the document in the following format: 

A-B\[C_D\]

where D is the mention id of the current entity (the source of the edge), 
C is the mention id of the edge's target entity,
A-B is the sentence id and the token id (within that sentence) of the first token in the target entity.

The column second from the right contains the type of the edge (either coref or bridge).
A bridging edge will also include one or more subtype annotations after a colon (:), (e.g, bridge:entity-associative). 
If there are multiple subtype, they will be separated by a semicolon (;), (e.g., bridge:comparison-sense;set-member). 

If there is more than one edge annotation on a token, the annotations in each column are separated by a vertical bar (|).

Note: There are also split antecedent annotations in the data which have the edge label "bridge", but do not have a subtype and have the information status "split" on the target entity.

## Reddit Data

Due to licensing constraints, documents in the Reddit subcorpus (named ```GUM_reddit_*``` (e.g. GUM_reddit_superman)) are included with all entity annotations, but with underscores instead of text.
To obtain the text data, please run python ```get_text.py```, which will allow you to reconstruct the text in these files. 

If you do not have credentials for the Python Reddit API wrapper (praw) and Google bigquery, the script can attempt to download data for you from a proxy. Otherwise you can also use your own credentials for praw etc. and include them in two files, praw.txt and key.json. For this to work, you must have the praw and bigquery libraries installed for python (e.g. via pip).

To add text to the reddit files:

```python get_text.py -m add```

To remove text from the reddit files:

```python get_text.py -m del```

## LLM Baseline

Code for the LLM baseline is available in the ```llm_baseline``` directory.

## GUMBridge v0.1 

Prior to the full annotation effort for GUMBridge v1, we conducted an annotation pilot on the
GUM test data. The adjudicated results of that initial pilot are included in ```pilot/test_v0```.

The ```pilot``` directory also includes the annotation guidelines used in the pilot. See this [paper](https://aclanthology.org/2025.law-1.4/) for details on the pilot.

Note: The annotation guidelines and test data have undergone revision since the v0 pilot. Please refer to the v1 release in ```data/test``` for the current test data.

Data from the inter-annotator agreement (IAA) study conducted on the dev set can be found in ```pilot/dev_iaa```.

## Citing

GUMBridge v1 release:

Levine, L., & Zeldes, A. (2025). [GUMBridge: a Corpus for Varieties of Bridging Anaphora](https://arxiv.org/abs/2512.07134). *arXiv preprint arXiv:2512.07134*.
```bibtex
@misc{levine2025gumbridgecorpusvarietiesbridging,
      title={GUMBridge: a Corpus for Varieties of Bridging Anaphora}, 
      author={Lauren Levine and Amir Zeldes},
      year={2025},
      eprint={2512.07134},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2512.07134}, 
}
```

GUMBridge test v0.1 release:

```pilot/test_v0``` contains the bridging annotations from the annotation pilot (conducted on the GUM test data) described in the following paper:

Lauren Levine and Amir Zeldes. 2025. [Subjectivity in the Annotation of Bridging Anaphora](https://aclanthology.org/2025.law-1.4/). In *Proceedings of the 19th Linguistic Annotation Workshop (LAW-XIX-2025)*, pages 48–59, Vienna, Austria. Association for Computational Linguistics.
```bibtex
@inproceedings{levine-zeldes-2025-subjectivity,
    title = "Subjectivity in the Annotation of Bridging Anaphora",
    author = "Levine, Lauren  and
      Zeldes, Amir",
    editor = "Peng, Siyao  and
      Rehbein, Ines",
    booktitle = "Proceedings of the 19th Linguistic Annotation Workshop (LAW-XIX-2025)",
    month = jul,
    year = "2025",
    address = "Vienna, Austria",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.law-1.4/",
    doi = "10.18653/v1/2025.law-1.4",
    pages = "48--59",
    ISBN = "979-8-89176-262-6",
    abstract = "Bridging refers to the associative relationship between inferable entities in a discourse and the antecedents which allow us to understand them, such as understanding what ``the door'' means with respect to an aforementioned ``house''. As identifying associative relations between entities is an inherently subjective task, it is difficult to achieve consistent agreement in the annotation of bridging anaphora and their antecedents. In this paper, we explore the subjectivity involved in the annotation of bridging instances at three levels: anaphor recognition, antecedent resolution, and bridging subtype selection. To do this, we conduct an annotation pilot on the test set of the existing GUM corpus, and propose a newly developed classification system for bridging subtypes, which we compare to previously proposed schemes. Our results suggest that some previous resources are likely to be severely under-annotated. We also find that while agreement on the bridging subtype category was moderate, annotator overlap for exhaustively identifying instances of bridging is low, and that many disagreements resulted from subjective understanding of the entities involved."
}
```