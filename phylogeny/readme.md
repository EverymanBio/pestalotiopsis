## Phylogenetic Analysis

The following contains the steps used in compiling accessions, generating multisequence alignments, concatenation, tree building and visualization.

### Sequence Acquisition
A list of type sequences containing ITS, TUB, and TEF accessions were constructed from prior work[^1].

A compiled list of Pestalotiopsis species and attached accessions was curated to remove repeat species and species outside of the target genus and formatted into the following CSV: [phylogeny/accessions.csv](accessions.csv)

An outgroup using the species _Neopestalotiopsis saprophytica_ was appended based on prior work.[^1].

#### Retreiving Gene Sequences from Subject Genome
ITS, TUB, and TEF regions of the subject Pestalotiopsis genome was obtaining using [seqkit](https://bioinf.shenwei.me/seqkit/) `v2.0.0` using the following command and a [primers.tsv](primers.tsv) containing primers targetting the regions of interest: 

```zsh
cat consensus.fasta | seqkit amplicon -j 16 -m 2 -p primers.tsv --bed
```

The outputs of each were saved as individual fasta files:
* [subject_its.fasta](files/subject_its.fasta)
* [subject_tub.fasta](files/subject_tub.fasta)
* [subject_tef.fasta](files/subject_tef.fasta)

#### Sequence Compilation
A [utility script](accession_downloader.py) was made to download the accessions in the source CSV from NCBI GenBank using [BioPython](https://biopython.org/) and compile them into three seperate loci-specific fasta files.

The utility also appends the subject genome loci-specific files to the corresponding list of accession sequences downloaded by the script.

```bash
 python accession_downloader.py email@domain.com
 ```

 The resulting files generated containing all of the accessions used in the phylogenic analysis, including sequences from the outgroup and subject genome are as follows:

* [its_combined.fasta](files/its_combined.fasta)
* [tub_combined.fasta](files/tub_combined.fasta)
* [tef_combined.fasta](files/tef_combined.fasta)

### Sequence Alignment
All three sequences were aligned using [MAFFT](https://mafft.cbrc.jp/alignment/software/) `v7.453`.

```zsh
mafft --auto files/its_combined.fasta > its_aligned.fasta
mafft --auto files/tub_combined.fasta > tub_aligned.fasta
mafft --auto files/tef_combined.fasta > tef_aligned.fasta
```

The alignments were trimmed and concatenated using [Mega 11](https://www.megasoftware.net/dload_mac_beta). 

### Tree Building
A Maximum Likelihood tree was constructed in [Mega 11](https://www.megasoftware.net/) using the combined ITS+TUB+TEF alignment with default settings and 100 bootstrap replications. 

The final tree was saved in Newick format: [final_tree.nwk](final_tree.nwk)



[^1]: Maharachchikumbura SS, Hyde KD, Groenewald JZ, Xu J, Crous PW. Pestalotiopsis revisited. Stud Mycol. 2014 Sep;79:121-86. doi: 10.1016/j.simyco.2014.09.005. PMID: 25492988; PMCID: PMC4255583.