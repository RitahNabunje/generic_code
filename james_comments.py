import vcf
import pandas as pd
import numpy as np

#parameters
#I think its worth testing with a big number here to check the logic!
a_size = 3000  # length of target amplicon in bases
upstream = a_size/2  #number of bases upstream of one target snp
p_dist = 100  #length in bases to fit a primer (i.e 80-100 bases before target amplicon)

vcf_reader = vcf.Reader(open('sample.vcf', 'r'))
snp_list=[]
for record in vcf_reader:
        record = (record.CHROM, record.POS) #extract snp chrom and Position info from vcf
        snp_list.append(record) #save snp info to list

snp_dict = dict() #create empty snp dictionary

#convert snp_list a dict and save it to snp_dict
for chrm, pos in snp_list:
        snp_dict.setdefault(chrm, []).append(pos)
#print (snp_dict)

#number of snps represented in the vcf record
for chrm,pos in snp_dict.items():
        snps = len(list(filter(None, pos)))

#make df for each chrm/contig represented in the vcf
dfs=[]
for chrm, pos in snp_dict.items():
	df = pd.DataFrame.from_dict((list(filter(None, pos))))
	df.columns=['snp_pos']
	df['diff'] = df['snp_pos'].diff()
	dfs.append(df)
print(dfs[0])

# I think here is the place to make sure you include the first window #(From 1-->first SNP position)
#at some point you will also need to know the chromosome lengths to #make sure you check the final window.

# df[row 0] = ('', df.loc[0,'snp1'] if df.loc[0,'snp1'] >= p_dist)
#chrms_length= read file with contig lengths


#extracting snps with p_dist between them for a primer
df1s=[]
for df in dfs:
	snp1 =[]
	snp2=[]
	l_index = 0
	h_index = 1
	last_index = len(df)-1
	pos1 = df.loc[l_index,'snp_pos']
	pos2 = df.loc[h_index,'snp_pos']
	diff = pos2 - pos1
	while h_index < last_index:
        	if diff >=p_dist:
                	snp1.append(pos1)
                	snp2.append(pos2)
        	l_index = l_index + 1
        	h_index = h_index + 1
        	pos1 = df.loc[l_index,'snp_pos']
        	pos2 = df.loc[h_index,'snp_pos']
        	diff = pos2 - pos1
	df1 = pd.DataFrame({'snp1':snp1, 'snp2':snp2})
	df1s.append(df1)
print(df1s[0])

#my idea here is that rather than count SNP between each adjacent plausible 'primer sites' 
#you might as well find plausible amplicons and then count SNPs in them
# so this code replaces the stuff commented out below
#loop through contigs
amplicons=[]
for i, df1 in enumerate(df1s):
#loop through primer sites	
#find primer pairs that look plausibly close
	#start and end of SNP-free regions that could become primer sites
	primer1_starts = []
	primer1_ends = []
	primer2_starts = []
	primer2_ends = []
	#size of gap between end of primer 1 region and start of primer 2 region
	gap = []
	#number of SNPs in this gap
	num_snps = []
	#loop through all first primer positions
	for primer1_index in list(df1.index):
		#end of possible placements for primer 1
		start_primer1 = (df1.loc[primer1_index, 'snp1'] +1)
		end_primer1 = (df1.loc[primer1_index,'snp2'] -1)
		primer2_index = primer1_index+1
		#loop through primer 2 positions
		while primer2_index < list(df1.index)[-1]:
			print(primer2_index)
			start_primer2 = (df1.loc[primer2_index,'snp1'] +1)
			end_primer2 = (df1.loc[primer2_index, 'snp2']-1)
			if (start_primer2 - end_primer1 > a_size - (2*p_dist) ):
			#if the start of primer 2 region is too far, skip to the end of this loop
				primer2_index = list(df1.index)[-1]
			else:
			#otherwise, store this as  a possible amplicon
				primer1_starts.append(start_primer1)
				primer1_ends.append(end_primer1)
				primer2_starts.append(start_primer2)
				primer2_ends.append(end_primer2)
				gap.append( end_primer1 - start_primer2 + 1 )
				n=[n for n in dfs[i].loc[:,'snp_pos'] if df1.loc[primer1_index,'snp2'] <= n <=  df1.loc[primer2_index,'snp1']]
				num_snps.append(len(n))
			primer2_index=primer2_index+1 
	amplicon_contig = pd.DataFrame({'primer1_start':primer1_starts,'primer1_end':primer1_ends,'primer2_start':primer2_starts,'primer2_end':primer2_ends,'gap':gap,'num_snps':num_snps},columns =['primer1_start', 'primer1_end', 'primer2_start','primer2_end','gap','num_snps'])
	amplicons.append(amplicon_contig)

print(amplicons[0])
	
	
#note at this stage I just know where I *could* put a primer..
#you will want to extract smaller regions for primer3: but I think its good to have the maximum
#in case you need to relax your rules a bit for primer3

#now identify regions to pass to primer 3:
#I think this will be a_size - gap at the end of primer 1 region and start of primer 2 region

#NB : I think it should be possible to add information to the existing 'amplicons' data table from this point on, rather than 
#creating lots of new data tables.



def make_boulderio(seqid, seq):
    length = len(seq)-1
    boulder = {
    "SEQUENCE_ID":seqid,
    "SEQUENCE_TEMPLATE":seq,
    "PRIMER_TASK":"generic",
    "PRIMER_PICK_LEFT_PRIMER":1,
    "PRIMER_PICK_INTERNAL_OLIGO":0,
    "PRIMER_PICK_RIGHT_PRIMER":1,
    "PRIMER_PRODUCT_SIZE_RANGE":"50-"+str(len(seq)),
    "PRIMER_OPT_SIZE":15,
    "PRIMER_MIN_SIZE":15,
    "PRIMER_MAX_SIZE":35,
    "PRIMER_MAX_POLY_X":10,
    "PRIMER_MIN_TM":50,
    "PRIMER_OPT_TM":60,
    "PRIMER_MAX_TM":72,
    "PRIMER_PAIR_MAX_DIFF_TM":8,
    "PRIMER_MIN_GC":20.0,
    "PRIMER_MAX_HAIRPIN_TH":100.0,
    "P3_FILE_FLAG":1,
    "PRIMER_EXPLAIN_FLAG":1,
    }
