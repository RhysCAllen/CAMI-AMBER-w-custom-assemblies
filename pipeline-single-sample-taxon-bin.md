September 2nd, 2026

The following attempts to describe an example of how to use AMBER to analyze taxon bins from user-created assemblies of CAMI II challenge samples.
References used include https://github.com/CAMI-challenge/AMBER/tree/master and https://cami-challenge.org/file-formats/   

Seeking clarification on the following questions:
--where to find the specs for different biobox format versions?
--does AMBER assume one classification per bin? Or does it break classifications into bp fractions such as 35% unclassified, 65% species A within a single bin?
--does AMBER penalize if only the forward reads are present in the biobox file? How do we get reverse reads if they don't show up in the .sam file? 

The procedure and associated scripts below can be modified for other input file formats.

This procedure uses Sample 0 from the CAMI II plant rhizosphere challenge. It's highly recommended to use the most recent CAMI challenge instead, which is currently CAMI III. The reads were assembled with metaspades 4.2, binned with MetaBat2, and classified with Sourmash 4.9.4. The output of the procedure is a biobox-formatted file that can serve as input for the CAMI AMBER web portal or downloaded AMBER software. 

This procedure assumes the following:
1) Your bin classifications are in kraken report style, or similarly map the bin ID to NCBI taxon ID.
See https://sourmash.readthedocs.io/en/latest/command-line.html for example of kraken report style.
2) You have classification files that enable mapping of contig to bin, such as sourmash match.csv files.
3) A .sam file used previously for binning of sample 0 assemblies(contigs), such as sample_0.sam

 TODO: make a note about singleton bin classification vs multi-contig bins and AMBER requirements. 

This pipeline will create the following additional files:  
4) Mapping file of CAMI reads to your custom assemblies(contigs).
5) Biobox output file for AMBER input. 

Some additional details for using a locally installed version of AMBER rather than the web portal are in Appendix 1 below. 
An example of how to use sourmash to create classifications used here is shown in Appendix 2. 

## Procedure:   

###### Step 1: Create a reads-to-contigs mapping file from your bins sam file

The .sam file that was used to determine differential abundance for binning your assemblies is the input file here.  
SAM format specifications were used to choose the column headers for our mapping file: https://samtools.github.io/hts-specs/SAMv1.pdf  

`echo "QNAME   RNAME" > reads-to-contigs-mapping.tsv`  

Append the read names and corresponding contig names:  

`awk -v FS='\t' -v OFS='\t' '!/^@/ {print $1, $3}' sample_0.sam >> reads-to-contigs-mapping.tsv`

Your output will contain the SEQUENCEID column (currently QNAME) necessary for AMBER to compare your results to the gold standard references.
The BH tags were added during read processing by metaspades BayesHammer; they will be removed in subsequent step. 

```
head reads-to-contigs-mapping.tsv 
QNAME	RNAME
S0R16554400/1 BH:failed	c_000000131573
S0R16554448/2 BH:changed:10	c_000000004317
S0R16554483/2 BH:changed:5	c_000000057414
S0R16555152/2 BH:failed	c_000000223269
...
```

###### Step 2: Create a bins-to-contigs mapping file from sourmash classifications

   This procedure assumes each contig is its own bin. This is because AMBER requires being able to map the bin number to each contig. ???

   
   See Appendix 2 for example of how sourmash files were created. 

   The script below takes as input your sourmash kreport.txt and match.csv files. The output is kreports that are appended with their corresponding bin IDs and    contig IDs. These appended kreports will be used to create the biobox output for AMBER. 
   

   Create environmental variables:

   `IN=<your/path/to/csv/match/files>`
   `OUT=<your/out/path>`

   ```
   #navigate to the directory containing your sourmash kreport outputs:
   
   for i in $(ls "$IN"/*.csv); do
   NAME=$(basename $i .csv);
   BIN=$(basename $i .csv | cut -d '.' -f8);
   CONTIG=$(awk -v FS=',' 'NR==2 {print $18}' "$i");
   awk -F '\t' -v OFS='\t' -v contig=$CONTIG -v bin=$BIN '{ sub(/\r/, ""); print $0, contig, "bin_"bin }' "$OUT"/"$NAME".kreport.txt >> "$OUT"/appended-kreport/"$NAME".appended-kreport.tsv;
   done
   ```

Output: your input kreports have been appended with bin and contig IDs:

```
100.00	6000	0	D	2	Bacteria	c_000000005423	bin_5
100.00	6000	0	P	1224	Proteobacteria	c_000000005423	bin_5
100.00	6000	0	C	1236	Gammaproteobacteria	c_000000005423	bin_5
100.00	6000	0	O	72274	Pseudomonadales	c_000000005423	bin_5
100.00	6000	0	F	135621	Pseudomonadaceae	c_000000005423	bin_5
100.00	6000	0	G	286	Pseudomonas	c_000000005423	bin_5
100.00	6000	6000	S	75612	Pseudomonas mandelii	c_000000005423	bin_5
```


###### Step 3: Combine your two mapping files to create biobox file for AMBER.


Inputs:
reads-to-contig.mapping.tsv
/your/path/to/amended/kreports
your sample name, such as rhimgCAMI2_short_read_sample_0

Note: this script has option for multi-contig bins: modify the script according to your use case.
  #see for loop below: comment out rows involving PERCENT; depending on whether using single-contig bins or multi-contig bins as input kreport path.

Function of script is to select "winning" classification(s) per contig (or optionally per bin) from each kreport,
based on the classification(s) with the highest assigned bp per report.

For singleton bins, the winning taxon is chosen from the match with the highest number of kmers assigned (one per kreport).

Example of singleton kreport: Column 3 is the `assigned` column, used to choose winner. Script will choose `Pseudomonas mandelii` as winner for this kreport.

```
100.00	6000	0	D	2	Bacteria	c_000000005423	bin_5
100.00	6000	0	P	1224	Proteobacteria	c_000000005423	bin_5
100.00	6000	0	C	1236	Gammaproteobacteria	c_000000005423	bin_5
100.00	6000	0	O	72274	Pseudomonadales	c_000000005423	bin_5
100.00	6000	0	F	135621	Pseudomonadaceae	c_000000005423	bin_5
100.00	6000	0	G	286	Pseudomonas	c_000000005423	bin_5
100.00	6000	6000	S	75612	Pseudomonas mandelii	c_000000005423	bin_5
```

For multi-contig bins, winning classifications are based on a user-set percentage cutoff threshold, in addition to highest assigned bp.
The percent in sourmash kreport input files represents the cumulative percentage of k-mers for this taxon and all descendants. (e.g the LCA kmers). 

Example of multi-contig bin kreport. With a user-defined cutoff of 20% (first column), script will choose `Unclassified` and `Rhizobium leguminosarum` only as winners, discarding the remaining results. 

```
65.89	4771999	0	D	2	Bacteria
34.11	2470000	2470000	U		unclassified
65.89	4771999	0	P	1224	Proteobacteria
65.89	4771999	0	C	28211	Alphaproteobacteria
65.89	4771999	0	O	356	Rhizobiales
62.61	4533999	0	F	82115	Rhizobiaceae
2.26	164000	0	F	69277	Phyllobacteriaceae
1.02	74000	0	F	41294	Bradyrhizobiaceae
62.52	4527999	0	G	379	Rhizobium
2.26	164000	0	G	68287	Mesorhizobium
1.02	74000	0	G	374	Bradyrhizobium
0.08	6000	0	G	357	Agrobacterium
60.73	4397999	4397999	S	384	Rhizobium leguminosarum
1.55	112000	112000	S	71433	Mesorhizobium amorphae
0.77	56000	56000	S	1076926	Rhizobium laguerreae
0.44	32000	32000	S	375	Bradyrhizobium japonicum
```

`python mapping-biobox.py reads-to-contigs-redacted.tsv /home/redacted/appended-kreport rhimgCAMI2_short_read_sample_0`

Output: note that column headers with \_UNDERSCORES\_ are ignored by AMBER, according to biobox format version 0.9 (TODO: is that right?)
head bioboxTaxonBinsByRead.tsv
tail bioboxTaxonBinsByRead.tsv
```
#CAMI Format for Binning
@Version:0.9.0
@SampleID:rhimgCAMI2_short_read_sample_0
#
@@SEQUENCEID    BINID   TAXID   _CONTIG_        _LENGTH_        _PERCENT_       _RANK_  _TAXON_
S0R11174/1      bin_3   1463864 c_000000002290  10000   100.00  S       Streptomyces sp. NRRL F-5630
S0R11174/1      bin_3   1463864 c_000000002290  10000   100.00  S       Streptomyces sp. NRRL F-5630
S0R14964/1      bin_3   1463864 c_000000002290  10000   100.00  S       Streptomyces sp. NRRL F-5630
S0R14964/1      bin_3   1463864 c_000000002290  10000   100.00  S       Streptomyces sp. NRRL F-5630
S0R20859/1      bin_3   1463864 c_000000002290  10000   100.00  S       Streptomyces sp. NRRL F-5630
.....
S0R16604297/1   bin_2   311230  c_000000000341  20000   100.00  S       Paraburkholderia terrae
S0R3327033/1    bin_2   311230  c_000000000341  20000   100.00  S       Paraburkholderia terrae
S0R5876794/1    bin_2   311230  c_000000000341  20000   100.00  S       Paraburkholderia terrae
S0R7112257/1    bin_2   311230  c_000000000341  20000   100.00  S       Paraburkholderia terrae
S0R10531146/1   bin_2   311230  c_000000000341  20000   100.00  S       Paraburkholderia terrae
S0R11732563/1   bin_2   311230  c_000000000341  20000   100.00  S       Paraburkholderia terrae
```



## Appendix 1: using AMBER locally

Obtain the gsa bin mapping file.  
   Download the gsa_mapping.binning file, which will be the gold-standard binning input file for amber.py:  
   https://cami-challenge.org/submit/ →
   https://zenodo.org/records/4982288 →
   https://zenodo.org/records/4982288/files/taxonomic_binning_cami2.tar.gz?download=1  

`curl -JLO https://zenodo.org/records/4982288/files/taxonomic_binning_cami2.tar.gz?download=1`    
`tar -xvf taxonomic_binning_cami2.tar.gz`

You will see three folders in the untarred download: retain the plant-rhizosphere directory. The other two can be deleted. 
    plant_associated_dataset
    strain_associated_dataset
    marine_associated_dataset

Locate the gsa_mapping.binning file in the plant_associated_dataset directory:

`cd plant_associated_dataset/ground_truth`
`tar -xvf rhizosphere_short_read_samples.binning.tar.gz`
Now we have access to the gold-standard read mapping file, `rhizosphere_short_read_sample_0.binning`.

This file will be the input for the -g argument to amber.py.

```
head rhizosphere_short_read_sample_0.binning 
@SampleID:rhimgCAMI2_short_read_sample_0
@@SEQUENCEID	BINID	TAXID	LENGTH
S0R0/1	Otu14.0	1144338	150
S0R0/2	Otu14.0	1144338	150
S0R1/1	LjRoot62	34073	150
```

# Appendix 2: Example of using sourmash to create classification files used in this procedure:

   ```
   #sketching singleton contigs:
   for i in "$IN"/*contig.fa; do
   NAME=$(basename $i .fa);
   echo sourmash sketch dna --singleton --name-from-first -p k=31,abund,scaled=2000 $i -o "$OUT"/${NAME}.sig;
   done | parallel

   #split singleton sketches into their own files:
   sourmash signature split "$IN"/*.sig --dna --ksize=31 --output-dir="$OUT"

   #gather kmer taxonomy matches of sketches:
   for i in "$IN"/*.sig; do
   NAME=$(basename $i .sig);
   echo sourmash gather $i "$DB"/2018.03.29-NCBI-RefSeq-k31.sbt.zip --dna --scaled=2000 --threshold-bp=6000 --save-matches "$OUT"/${NAME}-RefSeq-matches.zip \
   -o "$OUT"/matches/${NAME}-RefSeq-matches.csv;
   done | parallel

   #get taxonomic lineages of gathered taxa
   for i in "$IN"/*.csv; do
   NAME=$(basename $i .csv);
   echo sourmash tax metagenome --gather-csv $i --taxonomy-csv "$TAX"/Mar2018-sbt-lineages-taxpath.csv -F kreport --output-base ${NAME} --output-dir "$OUT";
   done | parallel
   
   ```





