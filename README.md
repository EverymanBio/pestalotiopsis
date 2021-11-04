# High-quality genome assembly of a Pestalotiopsis fungiusing DIY-friendly Methods

[![DOI](https://zenodo.org/badge/DOI/example/zenodo.example.svg)](https://doi.org/example)

The following contains the steps used in the assembly, polishing and annotation pipeline for generating the Pestalotiopsis draft genome. 

## 1. _De novo_ Assembly of Nanopore Sequencing Read Data
Sequencing was performed on the Oxford Nanopore platform and multiple `fastq` files were emitted from Guppy, the basecalling component of the MinKNOW software package.

The resulting `fastq` files were merged, gzipped and assembled locally using [Flye](https://github.com/fenderglass/Flye) `v2.9-b1768` using a [Thinkpad P14s](https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpadp/p14s-amd-g1/22wsp144sa1?orgRef=https%253A%252F%252Fduckduckgo.com%252F) with the following arguments:

```
flye --nano-hq /mnt/e/pestalotiopsis/guppy_sup_output/combined.fastq.gz \
--genome-size=42m \
--out-dir /mnt/e/pestalotiopsis/assembly/flye \
--threads 16 \
&> /mnt/e/pestalotiopsis/assembly/flye/flye.out
```

## Assembly Polishing 


##  Trimming contig_11 (5kb contig)
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
2. Use `seqtk` to create fasta without `contig_11`
```
 ./seqtk subseq /mnt/e/pestalotiopsis/assembly/flye/assembly.fasta \
> /mnt/e/pestalotiopsis/assembly/subseq.lst \
> /mnt/e/pestalotiopsis/assembly/flye/assembly_no_contig_11.fasta
```

3. Run `minimap2` v2.22 to generate overlaps
```
 ./minimap2 -x map-ont -t 12 \
/mnt/e/pestalotiopsis/assembly/flye/assembly_no_contig_11.fasta \
/mnt/e/pestalotiopsis/guppy_sup_output/combined.fastq.gz > \
/mnt/e/pestalotiopsis/assembly/minimap2/overlaps.paf

[M::mm_idx_gen::1.464*1.01] collected minimizers
[M::mm_idx_gen::1.863*1.48] sorted minimizers
[M::main::1.863*1.48] loaded/built the index for 10 target sequence(s)
[M::mm_mapopt_update::1.988*1.45] mid_occ = 10
[M::mm_idx_stat] kmer size: 15; skip: 10; is_hpc: 0; #seq: 10
[M::mm_idx_stat::2.079*1.44] distinct minimizers: 8359765 (94.64% are singletons); average occurrences: 1.065; average spacing: 5.352; total length: 47658561
[M::worker_pipeline::16.320*6.88] mapped 116002 sequences
[M::worker_pipeline::26.295*8.34] mapped 116374 sequences
[M::worker_pipeline::35.740*9.16] mapped 115079 sequences
[M::worker_pipeline::45.169*9.68] mapped 116765 sequences
[M::worker_pipeline::54.364*9.97] mapped 116479 sequences
[M::worker_pipeline::62.823*10.16] mapped 120016 sequences
[M::worker_pipeline::72.128*10.26] mapped 117458 sequences
[M::worker_pipeline::80.858*10.35] mapped 119949 sequences
[M::worker_pipeline::82.666*10.38] mapped 33873 sequences
[M::main] Version: 2.22-r1101
[M::main] CMD: ./minimap2 -x map-ont -t 12 /mnt/e/pestalotiopsis/assembly/flye/assembly_no_contig_11.fasta /mnt/e/pestalotiopsis/guppy_sup_output/combined.fastq.gz
[M::main] Real time: 82.701 sec; CPU: 857.953 sec; Peak RSS: 1.375 GB
```

3(b). Gzip the overlaps
`gzip /mnt/e/pestalotiopsis/assembly/minimap2/overlaps.paf`

4. Run `rakon` v.1.4.22
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

5. Run `medeka` v1.4.4

Note: it seems medaka does not like gzipped (prefers bzip) for the -d rakon input for whatever reason, so had to run it on ungzipped file. Oddly, gzip worked fine for the raw reads input.

```
medaka_consensus -i /mnt/e/pestalotiopsis/guppy_sup_output/combined.fastq.gz \                    
-d /mnt/e/pestalotiopsis/assembly/rakon/corrected.fasta \
-o /mnt/e/pestalotiopsis/assembly/medaka
```

# Annotation
Using `liftoff` v1.6.1

```
liftoff -g Pestal1_GeneCatalog_20180925.gff3 \
> -o gene_catalog \
> ../ncbi/consensus.fasta \
> Pestal1_AssemblyScaffolds.fasta
```
