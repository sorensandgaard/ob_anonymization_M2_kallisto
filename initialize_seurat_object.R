#!/usr/bin/env Rscript
library("Seurat")
library("tidyverse")

args = commandArgs(trailingOnly=TRUE)
outfile_pos <- args[1]
data_input_dir <- args[2]

data <- Read10X(data.dir = data_input_dir)
seurat_object = CreateSeuratObject(counts = data)

saveRDS(seurat_object,file = outfile_pos)
