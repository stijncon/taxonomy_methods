**Note: this project is on hold, and not actively being worked on anymore. Its main purpose was academic transparency and versioning over the course of the research project. Please be careful in using any of the (unfinished) code or models.**

# Overview of the project

The aim of this project is to check how taxonomic methods are distributed across taxonomy, and what they are associated to. Very exploratory for now, but we might preregister when the classifier is finished and we check associations with other variables. For more (and more up to date) code related to this broader project, see [here](https://codeberg.org/pencelab/biodiversity-disagreement).

Involved in the project: Stijn Conix, Marlies Monnens, Laura Vanstraelen, Jhoe Rheyes (annotating), Tom Artois, Charles Pence

# Step 1: Isolating methods sections and paragraphs

We isolated the methods sections and paragraphs with code written separately for each of the journals in our corpus (see TM_IsolateMethods). This is far from perfect and quite messy -- quite a few of the paragraphs have sentences missing or are merged with other paragraphs. This is due to inconsistenties in the way the pdfs are built. We checked 100 random paragraphs, and found that 10 were not as they should be, and considered this an acceptable rate. Given that it is about the words in the paragraphs in the first place (except for the one shot classification with LLMs), it probably doesn't matter too much for the classifiers. 

# Step 2:Topic Models & classification design

Given that we want to classify taxonomic methods, we need a classification of those methods. To make this, we first explored the data with various topic models (TM_MakeTopicModels, TM_ExploreTopicModels) to get an idea of which categories of methods were prevalent. On the basis of this, Marlies and Stijn made various iterations of a hierarchical classification, which we then also checked with other taxonomists, to get a final hierarchical classification (classif.txt). 

# Step 3: Data annotation

In order to build and test classifiers, we need annotated paragraphs. The classifier will need to be a multi-label one, as many paragraphs refer to various methods. We don't have the funds or time to have a large annotated set of paragraphs, but are aiming for 1500-2000. In a first step, Marlies and Stijn both annotated 100 paragraphs, fine-tuned the classification on the basis of that, and made an [annotation guide](https://docs.google.com/document/d/1V2W2QhHtWv73Ve4rWGEoNlSt3c20y1jzv7sv_Sr1LN0/edit?usp=sharing) Laura, Jhoe, Stijn and Marlies all annotated paragraphs, with around half of the samples annotated by more than one person ( 20/12/2024 total: 1200). All annotations are done using a custom made script in [potato](https://potato-annotation.readthedocs.io/en/latest/) (config-short). 

# Step 4: Baseline classifiers

We start by getting a regex baseline (TM_testRegex and regex_patterns). Then we compare various classic supervised learning models, and choose the best one (TM_testBaselineClassifiers). Then we tune the best one (TM_LogisticRegression). Then we try out transformer models (TM_SciBERT_DistilBERT), even though we have very limited data. We will compare these classifiers with zero-shot classification using an LLM (GTP_annotation_instructionsV1 and GTP_category_listV1, TM_GPTApi). Our expectation is that, given the enourmous amount of background knowledge that is required, the zero-shot LLM classification will outperform the other classifiers.

# Step 5: Choose classifiers for the entire corpus

On the basis of the tests with the annotated data, we use one or multiple classifiers over the entire corpus. This will allow us to associate the use of taxonomic methods with a range of variables that we already have, such as disagreement, taxa, geography (?),...
