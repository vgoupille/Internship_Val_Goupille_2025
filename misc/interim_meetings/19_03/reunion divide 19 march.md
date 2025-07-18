
<!--section: 1-->
- who i am :
	- msc plant biology heath and protection angers 
		- => focus on plant immunity, the role of microbiota in plant health 
		- I studied  different pathosystem during my both last internship arabido with alternaria brassicicola . To study the role of some phytocykines
		- I also work on the pathosystem malus domestica with erwinia amylovora  to study the growth-defense trad-off 
		- I like lab and also by analyse data (bioinfo aspect)
	- this years msc of  bioinfo rennes to develop new skills that can be usefull for my work in the futur 
	- 
	- start my intership 5 february at ecobio with Solene and Philippe
	- on the subject of the DOL (Division Of Labor) through an intra-species : pseudomonas bracisicacearum during stress 
	- 
	- hypothesis : 
		- In this Work Package we focus on transcription aspect 
		- verification if there are diff cluster in "normal" conditions 
		- if the stress add can apparition new clusters (milieux appauvri fer or glucose) that can be link with DOL 
		- "latent state", 
		- w


	



- qu'est ce que j'ai fais pour le moment :
	- biblio on the subject 
		- ANR project 
		- Concept of DOL 
		-  pseudomonas bra ( pathogenesis, root colonisation stress combinais)
		- differentes method of scell approch for bacteria analysis 
		- challenge /limitation of sc in bacteria ( 3 principal approch with options for example depletions of rRNA )
			- focus on SPLIT/ POOL strategy => split-seq in bacteria 
				- microsplit ( Kuchina et al )
		- Bioinformatique  aspect to analyse this of data 
			- different step
				- preprocessing 
					- STARsolo...
						- => article : benchmark for split-seq (eucaryote)
							- starsolo is the best strats  (it's not the strats that kuchina and al use (split-seq pipeline) in there article )
							- so i focus on, and test it
								- create the matrix : 
									- for each cell 
										- align (reads/ UMI with the genome )
										- different parameters that could be consider for example : one and multiple aligment maps ( in their article )


					2 principal differentes approch :
						on R with Seurat V5 
						on Python with Scanpy 
						=> both use the matrix in input 
							- feature (gene)
							- cell 
							- count 
						- Scanpy is better for big dataset but Seurat allows to do beautifull representation with ggplot 
					- i will test both strats 
					- we can convert 
					

					- after 
						- create script to add metadata to each cell the condtions
							- (well, condition, DO, repetition)
						- filter rNRA tRNA... 
						- we have many many cells with 0 count 
								-so we need to filter cell
									=> different strats , for example : 
									it's a manual step 
										nb of genes by cell 
										nb of UMIs by cell  (200 UMIs)
						- I work on the dataset of kushina , it was very complicated to find the metadata with the correct annotation, they only publish sequencing data , and processing data (starsolo output) but not the metadata, so I can't do analysis... I find another article (pre-print) which reanalyse there data (they analyse rRNA and growth to see if it's exist a correlation betwenn both  ) = >so i find different script to assign metadata data , I need to understead how they did
						- to compare there of diff DO they do a filtering to to conserv best 70% of each condiutions 
					- => so I analyse there data 
				- I learn how to create a seurat object, assign metadata 
			there are also a step to verify the quality of data
		=> I see there are huge diff of dept of sequencing (UMIs by cell, count by genes ) between the rep in there experiment , the DO have an impact on the number of UMI detected 
			- After the step of filtering , we need to normalise and scale the data, to be able to compare gene expression betwenn cell, well and cond...
			they are Sctransform a package that allow to do that 
			- they  are a step of integration of data with UMAP  
				- differnt strats can be use in seurat V5 that can consider batch effect. I will test and compare all this strats ( benchmarking)
			- after DE 
			- 
		- I find a preprint with do a pipeline/ workflow which use scanpy (python) and many other methods, process  (scdeed) to optimise the analysis of bacterial scell 
			- « Bacterial single-cell RNA sequencing has the potential to elucidate within-population heterogeneity of prokaryotes, as well as their interaction with host systems. Despite conceptual similarities, the statistical properties of bacterial single-cell datasets are highly dependent on the protocol, making proper processing essential to tap their full potential. We present BacSC, a fully data-driven computational pipeline that processes bacterial single-cell data without requiring manual intervention. BacSC performs data-adaptive quality control and variance stabilization, selects suitable parameters for dimension reduction, neighborhood embedding, and clustering, and provides false discovery rate control in differential gene expression testing. We validated BacSC on a broad selection of bacterial single-cell datasets spanning multiple protocols and species. Here, BacSC detected subpopulations in Klebsiella pneumoniae, found matching structures of Pseudomonas aeruginosa under regular and low-iron conditions, and better represented subpopulation dynamics of Bacillus subtilis. BacSC thus simplifies statistical processing of bacterial single-cell data and reduces the danger of incorrect processing. »
			
	- for the moment : 
		- I learn how to connect to HPC to remote run code 
		- I learn how to analysr
		- I start by analyse the pre-data of solene expe
			- but no all barcode so i can't analyse the result with 
		- 
		- Learn how to build docker/ singularity image to produce FAIR envir 
- *fjerjrej*