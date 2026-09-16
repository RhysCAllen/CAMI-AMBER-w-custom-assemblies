from sys import argv, exit #command line args for file name input
import csv #read in tsv as dict
from os import scandir #get multiple files residing in a given path


def main():

    #see for loop below: comment out rows involving PERCENT; depending on whether using single-contig bins or multi-contig bins as input kreport path.
    PERCENT=20.00  #cutoff of percent of kmers contained (contained clade, not assigned taxon) to report a classification

    # print(len(sys.argv))

    if len(sys.argv) == 4:
        readsMapping = sys.argv[1]
        kreportPath = sys.argv[2]
        sampleName = sys.argv[3]
    else:
        print("Use case: python mapping-biobox.py <your-reads-to-contigs.tsv> <your-path-to-kreport> <your-sample-name>")
        sys.exit() #end program



    readsMapping = []; #it's gonna be a list of dictionaries, with QNAME for seqIDs and RNAME for contig IDs

    with open(readsMapping) as file:  #file automatically closes outside of this block
        reader = csv.DictReader(file, delimiter='\t');  #first row is automatically the keys of the dictionaries
        for row in reader:
            readsMapping.append(row);


    #list of winning dicts from all kreports
    winners = [];

   
    #pseudocode for this bit:
    # path= location of kreport files
    # for each file:
    #     read file into list of dicts   
    #     get winner dict
    #     append winner dict to list of winner dicts

    #https://stackoverflow.com/questions/56879219/how-can-i-iterate-through-a-list-of-files-and-open-each-file
    #https://stackabuse.com/python-list-files-in-a-directory/
    #with os.scandir(path) as listOfEntries:
    with os.scandir(sys.arg[2]) as listOfEntries:
        for entry in listOfEntries:
            #if entry.is_file():
            if entry.is_csv():  #entry is the (full path?) name of the file, not the contents of the file
                #print(entry.name)
                kreportIn = []  #is the scope of this gonna be remade each iteration or appended across iterations
                #for file in files: 
                with open(entry, 'r') as f:
                    #need keys here that do not exist in my files
                    kreportKeys = ["percent", "contain", "assign", "rank", "taxid", "taxon", "contig", "binid"];
                    # strip() removes trailing newline characters (\n)
                    lines = [line.strip() for line in f.readlines()]; #list comprehension, I believe
                    kreport = dict(zip(kreportKeys, lines)); #make a new dict for each row of file
                    kreportIn.append(kreport);
                        #get winning row (singleton bins) or rows (mutli-contig bins), and append row(s)to bioboxOut list of dicts
                        for row in kreportIn:
                            if row["assign"] !=0:  #comment out this row when using multi-contig bins
                                winners.append(row);  #comment out this row when using multi-contig bins
                            if row["percent"] >= PERCENT:  #comment out this row when using singleton bins
                                winners.append(row);      #comment out this row when using singleton bins

# head reads-to-contigs-mapping.tsv 
# QNAME	RNAME
# S0R16554400/1 BH:failed	c_000000131573
# S0R16554448/2 BH:changed:10	c_000000004317
# S0R16554483/2 BH:changed:5	c_000000057414

    
    bioboxOut = [];
    bioboxKeys = ["seqID", "binID", "taxID", "contig", "length", "percent"];

    for winner in winners: #winner is a dict with these keys: ["percent", "contain", "assign", "rank", "taxid", "taxon", "contig", "binid"]
        #get the contig of the winner
        #look up that contig in readsMapping
        #write all of the reads for that contig, one read per row, to bioboxOut;
        # strip the BH from the read name before writing each row
        for read in readsMapping: #read is a dict with these keys: QNAME	RNAME
            





    #write file in AMBER format of all of your bin/contig classifications, with one CAMI read per line. Good grief
    # #CAMI Format for Binning
    # @Version:0.9.0
    # @SampleID:rhimgCAMI2_short_read_sample_0 or SAMPLENAME
    # @@SEQUENCEID	BINID	TAXID	_CONTIG_	_LENGTH_	_PERCENT_
    
    
    
    
    #Ok so then once we are done with the kreports and made the summary dict,
    #we append sequences from the reads-to-contigs mapping file. 

    #readsMapping = [];  # a very large file, even for a single sample. 
    for i in winners:  #list of winning dicts from parsing all the kreports


	
if __name__ == "__main__":
    main();