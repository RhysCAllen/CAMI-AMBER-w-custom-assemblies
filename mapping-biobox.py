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



    readsMapping = []; #it's gonna be a list of dictionaries, with QNAME key for seqID values and RNAME key for contig ID values

    with open(readsMapping) as file:  #file automatically closes outside of this block
        reader = csv.DictReader(file, delimiter='\t');  #first row is automatically the keys of the dictionaries
        for row in reader:
            readsMapping.append(row);


   
    #make a list of dicts containing all the winning classifications from each kreport
    #pseudocode for this bit:
    # path= location of kreport files
    # for each file:
    #     read file into list of dicts   
    #     get winner dict
    #     append winner dict to list of winner dicts


    #list of winning dicts from all kreports
    winners = [];


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

    
    #take all the winning kreport results from above, and map them to their CAMI seq IDs:
    bioboxOut = [];
    bioboxKeys = ["@@SEQUENCEID", "BINID", "TAXID", "_CONTIG_", "_LENGTH_", "_PERCENT_", "_RANK_", "_TAXON_"]; #only the first three are used by AMBER for read seqIDs. "length" is used by AMBER for contig seqIDs. 

    for winner in winners: #winner is a dict with these keys: ["percent", "contain", "assign", "rank", "taxid", "taxon", "contig", "binid"]
        #get the contig of a winner
        contig = winner["contig"];
        #look up that contig in readsMapping list of dicts
        #write all of the reads for that contig, one read per row, to bioboxOut;
        # strip the BH from the read name before writing each row
        for read in readsMapping: #read is a dict with these keys: QNAME	RNAME
            if read["RNAME"] == contig:
                #strip the BH chars offa RNAME
                seq = read["QNAME"].split(None, 1)[0] #get first field after splitting QNAME value by whitespace
                #make a new dict to add to bioboxOut:
                result = {"@@SEQUENCEID": seq, "BINID": winner["binid"], "taxID": winner["taxid"], "length": winner["assign"], "contig": read[RNAME], "percent": winner["percent"], "rank": winner["rank"], "taxon": winner["taxon"]};
                bioboxOut.append(result);



    #write mapped kreport + seqID to biobox format, to use as AMBER input.

    # #CAMI Format for Binning
    # @Version:0.9.0
    # @SampleID:rhimgCAMI2_short_read_sample_0
    # @@SEQUENCEID	BINID	TAXID	_CONTIG_	_LENGTH_	_PERCENT_   _RANK_  _TAXON_

    CAMI_header = [
        ["#CAMI Format for Binning"],
        ["@Version:0.9.0"],  #TODO confirm with CAMI folks that this is the version of the biobox format itself, not AMBER? 
        ["@SampleID:" + sampleName],  #e.g. @SampleID:rhimgCAMI2_short_read_sample_0
        ["#"]  #insert commented out blank row before body of file
    ]
    
    #print(CAMI_header);

    #write file in biobox format for AMBER input of all of your bin/contig classifications, with one CAMI seq read per line. Good grief.
    # with open("output.csv", mode="a", newline="", encoding="utf-8") as f:

    with open("bioboxTaxonBinsByRead.tsv", "w") as file:
        std_writer = csv.writer(file);
        std_writer.writerows(CAMI_header);
        dict_writer = csv.DictWriter(file, fieldnames=bioboxKeys, delimiter="\t");
        dict_writer.writeheader();  #prints your keys (as defined in fieldnames) as column headers to the resulting file
        #https://stackoverflow.com/questions/33091980/difference-between-writerow-and-writerows-methods-of-python-csv-module#33092054
        dict_writer.writerows(bioboxOut) #writerows takes a list of dicts as argument, and writes the values for the given fieldname keys


	
if __name__ == "__main__":
    main();