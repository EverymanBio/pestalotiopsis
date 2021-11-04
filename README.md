## High-quality genome assembly of a Pestalotiopsis fungi using DIY-friendly Methods

[![DOI](https://zenodo.org/badge/406962936.svg)](https://zenodo.org/badge/latestdoi/406962936)

The following contains the steps used in the assembly, polishing and annotation pipeline for generating the Pestalotiopsis draft genome. 

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

4. Use [rakon](https://github.com/lbcb-sci/racon) `v.1.4.22` for error correction

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
Finally, [medeka](https://nanoporetech.github.io/medaka/) `v1.4.4` was used to generate the final consensus assembly.

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
