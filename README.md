## High-quality genome assembly of a Pestalotiopsis fungi using DIY-friendly Methods

[![DOI](https://zenodo.org/badge/406962936.svg)](https://zenodo.org/badge/latestdoi/406962936)

The following contains the steps used in the assembly, polishing and annotation pipeline for generating the Pestalotiopsis draft genome.

See [Phylogenetic Analysis Readme](phylogeny/readme.md) for steps used in phylogeny.

### _De novo_ Assembly of Nanopore Sequencing Read Data
Sequencing was performed on the Oxford Nanopore platform and multiple `fastq` files were emitted from Guppy, the basecalling component of the MinKNOW software package.

The resulting `fastq` files were merged, gzipped and assembled locally using [Flye](https://github.com/fenderglass/Flye) `v2.9-b1768` using a [Thinkpad P14s](https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpadp/p14s-amd-g1/22wsp144sa1?orgRef=https%253A%252F%252Fduckduckgo.com%252F) with the following arguments:

```
flye --nano-hq /mnt/e/pestalotiopsis/guppy_sup_output/combined.fastq.gz \
--genome-size=42m \
--out-dir /mnt/e/pestalotiopsis/assembly/flye \
--threads 16 \
&> /mnt/e/pestalotiopsis/assembly/flye/flye.out
```

### Error Correction
A `5kb` circular contained in `contig_11` believed to be unrelated to the source organism was identified and trimmed from the draft assembly. Overlaps were then generated from the truncated assembly and error corrected.

####  Trimming contig_11 (5kb contig)
1. Create list of desired contigs without `contig_11` > `pestalotiopsis/assembly/subseq.lst`
```
contig_4
contig_6
contig_3
contig_8
contig_7
contig_5
contig_9
contig_1
contig_2
contig_10
```
2. Use [seqkit](https://bioinf.shenwei.me/seqkit/) to create fasta without `contig_11`
```
 ./seqtk subseq /mnt/e/pestalotiopsis/assembly/flye/assembly.fasta \
> /mnt/e/pestalotiopsis/assembly/subseq.lst \
> /mnt/e/pestalotiopsis/assembly/flye/assembly_no_contig_11.fasta
```

3. Use [minimap2](https://github.com/lh3/minimap2) `v2.22` to generate overlaps
```
 ./minimap2 -x map-ont -t 12 \
/mnt/e/pestalotiopsis/assembly/flye/assembly_no_contig_11.fasta \
/mnt/e/pestalotiopsis/guppy_sup_output/combined.fastq.gz > \
/mnt/e/pestalotiopsis/assembly/minimap2/overlaps.paf
```

4. Use [racon](https://github.com/lbcb-sci/racon) `v.1.4.22` for error correction

Note that the overlaps were gzipped prior to running rakon (e.g. `gzip overlaps.paf`)

```
./build/bin/racon -t 16 \
/mnt/e/pestalotiopsis/guppy_sup_output/combined.fastq.gz \
/mnt/e/pestalotiopsis/assembly/minimap2/overlaps.paf.gz \
/mnt/e/pestalotiopsis/assembly/flye/assembly.fasta > \
/mnt/e/pestalotiopsis/assembly/rakon/corrected.fasta

[racon::Polisher::initialize] loaded target sequences 0.173205 s
[racon::Polisher::initialize] loaded sequences 67.255879 s
[racon::Polisher::initialize] loaded overlaps 2.016656 s
[racon::Polisher::initialize] aligning overlaps [====================] 141.591912 s
[racon::Polisher::initialize] transformed data into windows 6.779552 s
[racon::Polisher::polish] generating consensus [====================] 1084.741511 s
[racon::Polisher::] total = 1309.127294 s
```

### Create Consenus Assembly
Finally, [medaka](https://nanoporetech.github.io/medaka/) `v1.4.4` was used to generate the final consensus assembly.

```
medaka_consensus -i /mnt/e/pestalotiopsis/guppy_sup_output/combined.fastq.gz \                    
-d /mnt/e/pestalotiopsis/assembly/rakon/corrected.fasta \
-o /mnt/e/pestalotiopsis/assembly/medaka
```

### Assembly Annotation
Annotation was performed using [liftoff](https://github.com/agshumate/Liftoff) `v1.6.1` against reference assembly [Pestalotiopsis sp. NC0098 v1.0 genome](https://mycocosm.jgi.doe.gov/Pestal1/Pestal1.info.html). 

```
liftoff -g Pestal1_GeneCatalog_20180925.gff3 \
> -o gene_catalog \
> ../ncbi/consensus.fasta \
> Pestal1_AssemblyScaffolds.fasta
```

### Estimating the number of chromosomes 

The first step was to determine which contigs contained telomere repeat sequences. Contigs 1, 4, 6, 7, 8 have telomeres at both the start and end of the fasta file, suggesting there are at least 5 telomere-to-telomere chromosomes. Contig 2, 3, 5, 9 do not have any telomeres. Contig 10 is the mitochondrion since it is circularized, 68 kilobases long, and a BLASTN search revealed high identity to previous mitochondrial genomes.

```
cat assembly.fasta | grep -A 2 -B 1 -n --no-group-separator -E "AACCCTAACCCTAACCCT|AGGGTTAGGGTTAGGGTT"
1->contig_1
2:CCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAA
3:CCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAA
4-CCCTAAGCTAATATGCTTTTTCGTAGGTAGCCGATATTTCGTAAATTCGGTTTTCGGCGT
5-TATAAAATATAAATAAAGTTTATTTTTTAAATTTATCGTAATCGGTATAAATTATATTAC
68377-TTTTAAAAACAAAACGAGCGGTTTAAATAGCGTTTTTTTTATATCGGCTCGCTTTTATAA
68378:CGGTTTATTAGCTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGG
68379:TTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGG
68380:TTAGGGTTAGGGTTAGGGTTAGGGTTAGGGAGCAATACGTAACT
68381->contig_3
68382-TGTACTTCGTTCAGTTGCAGCATACTTGCTATTACAGTTCGAAGCAGCCATATTTGTAGC
168492->contig_4
168493:GTTACGTATTGCTCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAA
168494:CCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAA
168495:CCCTAACCCTAACCCTAACCCTAAGCTAGCTAGCTAATGATTAAACGAAGGAATTTAAGT
168496-AAAAAAAATACCGTTAATTAATATATAAAAAATAAATAAAAAAAGCTACGCAGTAAAAAC
168497-GCTATTTAAAATTATTTAAAATTATTATTAAAGTATATAAAAATACGTTTATTTATTAAT
316520-AGAGCTCCATTTTGATGGTTGATGTGGCCGGAGGTCGTGGCCACGACTTGCTCGAATTTT
316521:AGGGTTAGGGTTAGGTTAGCTTAGGGTTAGGGTTAGCTTAGGGTTAGGGTTAGGGTTAGG
316522:GTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGG
316523-GTTAGGGTTAGGGTTAGG
316524->contig_5
406562->contig_6
406563:TTCAGTTACGTATTGCTCCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAAC
406564:CCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAAC
406565:CCTAACCCTAACCCTAACCCTAACCCTAGGCTGATAATTCTTTTTATTAAATTATAATTC
406566-CGGTTATAATTTATTTTTTAAAATTATTATTAAAATTATAATCCCGTTAATAATTATTAA
406567-TAATTATTAATTTTAATTAGTATTTTAATAAGTTTTTTATTTAATAATAATATCCTTGTA
528377-TACTGACTGCTGCATTGACTGTTGTATTCACTGCTGCACTGACTGTTGTACTGACTGCTG
528378:CATTGACTGCTGTATTGACTGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTA
528379:GGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTA
528380:GGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGAGCAATACGTAACTGAACG
528381->contig_7
528382:TACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCT
528383:AACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCT
528384-AAGCTAACCCTAACCCTAATGGTCCTTGGGAGCAGACGCTTGTGGTCTTTTCGTATAGCA
528385-AAAGCTGCTGTGTGATTTCGACTTGCCTAGTTCGGACTCGAATAAGTGGCGATTCCAGAG
625696-AAAATATATCCGATTTAAACGCCGTTAATACGGCCGACCCGGGCTTAAAATTAATTTAAA
625697:AAGTTAATTAGCTTAGGGTTAGGTTAGCTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTT
625698:AGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTT
625699:AGGGTTAGGGTTAGGGTTAGGG
625700->contig_8
625701:ACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTA
625702:ACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCTATGCGCGT
625703-ACACGCTGTAAAAAGAAGCGAACCCCGCAAAAAGGCATACCTACCCCAGCCAAGTGGTAC
625704-AGCAATTGTGAATGGTCCAGATAGTAGTTGGCGATAAATGAGCCCTTTGACTAGAAATAA
794422-TTGCAAGAAGATGATTGCAATCTTGGGTGCTTAGAGTTAGCTTAGGGTTAGCTTAGGGTT
794423:AGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTT
794424:AGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGGTTAGGAGCAATACGTAACTG
794425-AACGAAGTAC
```

### Estimate the number of chromosomes by generating network graphs of all telomere-containing reads

[seqtk](https://github.com/lh3/seqtk) is used to filter the reads by length, and [minimap2](https://github.com/lh3/minimap2) is used to generate all-vs-all overlaps between all telomere-containing reads. 

```
# filter to take only reads that are at least 5 kb long
seqtk seq -L 5000 pest.fastq.gz | gzip > pest_5kb.fastq.gz

# extract telomere-containing reads only
gunzip -c pest_5kb.fastq.gz | grep -A 2 -B 1 --no-group-separator -E "AACCCTAACCCTAACCCT|AGGGTTAGGGTTAGGGTT" - | gzip > telomere_5kb_pest.fastq.gz

# 774 reads pass this filtering. this is about the expected sequencing coverage range we expect for anywhere 5-10 chromosomes.

# align all telomere-containing reads against each other.
minimap2 -x ava-ont -t 14 telomere_5kb_pest.fastq.gz telomere_5kb_pest.fastq.gz  > 5kb_overlaps.paf

# filter the overlaps so all overlaps have > 95% query coverage
awk '( ($4 - $3 ) / $2 ) >= 0.95 {print $0}' 5kb_overlaps.paf  > 5kb_overlaps_filt.paf

# this reduces the overlaps from ~ 24k to ~ 6k
```

### Visualize the network graphs in R

The 14 unique highly interconnected network graphs separate perfectly, each network graph of reads represents a group of reads that all come from a single telomere. Since we expect 2 telomeres per chromosome (one at the start, one at the end, and because DNA was extracted during a haploid life cycle so there is only a single haplotype expected), this suggests that are 14 unique telomeres and 7 chromosomes. 

```
# open the R programming language on the command land 
R

library(igraph)

d <- read.table("5kb_overlaps_filt.paf")

# we only need the target and query read names
subset <- data.frame(from=d$V1, to=d$V6)

# create the network graph
g <- graph_from_data_frame(subset)

# extract all sub graphs with a minimum of 10 reads 
subgraphs <- decompose.graph(g, min.vertices=10)

# plot all network graphs 
pdf("network_graph.pdf", width = 50, height = 50)
par(mfrow=c(3,5))
for (i in seq(subgraphs)) {

    plot(subgraphs[[1]], vertex.label=NA, vertex.size=15, edge.arrow.size=0.1, vertex.color=rgb(0.2,0,1, 0.2), vertex.frame.color="NA")
} 

dev.off()

```

