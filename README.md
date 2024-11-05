# General
code for the project of classifying taxonomy papers by the methods they employ.

# Isolating methods sections and paragraphs
We isolated the methods sections and paragraphs with code written separately for each of the journals in our corpus. This is far from perfect -- quite a few of the paragraphs have sentences missing or are merged with other paragraphs. This is due to inconsistenties in the way the pdfs are built. We checked 100 random paragraphs, and found that 5 were not as they should be, and considered this an acceptable rate. Given that it is about the words in the paragraphs in the first place (except for the one shot classification with LLMs), it probably doesn't matter for the classifiers.

# Topic Models
We first explored the data with various topic models, which informed the classification we designed. We also used this to get samples to train some of the classifiers.

# Data annotation

3 annotators read and annotate paragraphs using potato.
