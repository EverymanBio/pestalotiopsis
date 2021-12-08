import pdb
import csv
from sys import argv
from Bio import Entrez, SeqIO

class AccessionsDownloader:
    ACCESSIONS_CSV = 'accessions.csv'
    OUTPUT_DIR = './files'
    FORMAT = 'fasta'
    LOCI = ['its', 'tub', 'tef']

    def __init__(self, entrez_email):
        accessions_list = self.build_accessions_list()

        self.download_accessions(accessions_list, entrez_email)
        self.append_subject_sequences()

    def append_subject_sequences(self):
        for locus in self.LOCI:
            subject_filename = "%s/subject_%s.fasta" % (self.OUTPUT_DIR, locus)
            subject_file = open(subject_filename, 'r')
            subject_contents = subject_file.read()
            subject_file.close()

            dest_filename = self.combined_fasta_filename(locus)
            dest_file = open(dest_filename, 'a')
            dest_file.write(subject_contents)
            dest_file.close()

    def combined_fasta_filename(self, locus):
        return "%s/%s_combined.%s" % (self.OUTPUT_DIR, locus, self.FORMAT)

    def download_accessions(self, accessions_list, entrez_email):
        Entrez.email = entrez_email

        for locus in self.LOCI:
            sequences = []

            for accession in accessions_list:
                species = accession['Species'].replace(' ', '_')

                handle = Entrez.efetch(db = 'nucleotide',
                                       id = accession[locus],
                                       rettype = self.FORMAT)

                seq = SeqIO.read(handle, self.FORMAT)
                seq.name = seq.description = ''
                seq.id = species

                sequences.append(seq)

            outfile = self.combined_fasta_filename(locus)
            SeqIO.write(sequences, outfile, self.FORMAT)

    def build_accessions_list(self):
        with open(self.ACCESSIONS_CSV) as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]

if __name__ == '__main__':
    AccessionsDownloader(argv[1])
