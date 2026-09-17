September 2nd, 2026

I'm a new user of CAMI, using the Plant Rhizosphere dataset from the CAMI II challenges.  
The taxon binning challenge of CAMI II, evaluated with AMBER, supports evaluating binning/classification of assemblies.   
The procedure to evaluate bins of gold-standard assemblies is well-documented.  
The purpose of this repo is to attempt to document an example of evaluating bins of user-generated assemblies with AMBER.   

Purpose of this repo:  
1) Document for myself this procedure of evaluating my own custom assemblies with AMBER, if possible.  
2) Possibly CAMI team or more experienced CAMI users will reply indicating whether this procedure is on the right track, or suggest corrections.   

My current understanding of AMBER evaluation requirements:  
The input file of AMBER has a required SEQUENCEID column, which is the basis of the AMBER evaluations. This column must include sequence IDs from CAMI reference data.  

There are two options for the SEQUENCEID column:  

A) Gold-standard contig IDs  
Users can bin the provided gold-standard assemblies (contigs), listed in the SEQUENCEID column, such as S0C541542.  

B) Individual CAMI read IDs  
Users can bin their own custom assemblies (contigs).
For this option, the SEQUENCEID column contains individual CAMI read IDs, such as S0R11174/1.   

The AMBER repo gives support for option A. This repo is attempting to provide an example of option B.   
