from optparse import make_option
from django.core.management.base import CommandError
from Bio import SeqIO
import cyano.models as cmodels
from cyano.helpers import slugify
from django.core.exceptions import ObjectDoesNotExist
from cyano_command import CyanoCommand

class Command(CyanoCommand):
    args = '<file file ...>'
    help = 'Imports NCBI GenBank Files'
    
    option_list = CyanoCommand.option_list + (
        make_option('--chromosome', '-c',
                    action='store',
                    dest='chromosome',
                    default=False,
                    help='Name of the Chromosome (or Plasmid) to assign the GenBank data to. Created if necessary.'),
        make_option('--name', '-n',
                    action='store',
                    dest='name',
                    default=False,
                    help='Human readable name of the species')
        )

    def handle_command(self, species, revdetail, *args, **options):
        if not options["chromosome"]:
            raise CommandError("chromosome argument is mandatory")
        if not options["name"]:
            raise CommandError("name argument is mandatory")
        
        chr_name = slugify(options["chromosome"])

        if options["chromosome"] != chr_name:
            raise CommandError("Chromosome {} contained invalid characters. Only letters, numbers and _ are allowed".format(options["chromosome"]))
        
        for arg in args:
            self.stdout.write("Parsing %s" % (arg))
            with open(arg, "r") as handle:
                f = SeqIO.parse(handle, "genbank")
                for record in f:
                    if not record.annotations:
                        raise CommandError("File lacks annotation block")
                    
                    anno = record.annotations
    
                    if "organism" in anno:
                        species.name = anno["organism"]
                    
                    species.comments = ""
                    if record.description != None:
                        species.comments = record.description
                    if "comment" in anno:
                        species.comments += "\n" + anno["comment"]
    
                    species.genetic_code = '11'
                    species.save(revision_detail = revdetail)
                    
                    if record.dbxrefs:
                        for xref in record.dbxrefs:
                            # BioPython doesnt always properly split the db xrefs
                            xref = xref.split(" ")
                            for x in xref:
                                if ":" in x:
                                    source, xid = x.split(":")
                                    wid = source + ":" + xid
                                    try:
                                        x = cmodels.CrossReference.objects.get(wid = slugify(wid))
                                    except ObjectDoesNotExist:
                                        x = cmodels.CrossReference(wid = slugify(wid))
    
                                    x.name = wid
                                    x.xid = xid
                                    x.source = source
                                    x.save(revision_detail = revdetail)
                                    x.species.add(species)
                                    x.save(revision_detail = revdetail)
                                    species.cross_references.add(x)
                        
                        species.save(revision_detail = revdetail)
    
                    if "references" in anno:
                        for ref in anno["references"]:
                            # calculate the wid
                            if ref.pubmed_id:
                                wid = "PUB_" + ref.pubmed_id
                                name = "Pubmed #" + ref.pubmed_id
                            elif ref.medline_id:
                                wid = "MED_" + ref.medline_id
                                name = "Pubmed #" + ref.medline_id
                            else:
                                publication = cmodels.PublicationReference.objects.filter(
                                    authors__exact = ref.authors, title__exact = ref.title, publication__exact = ref.journal)
                                next_id = 0
                                if publication.exists():
                                    wid = publication[0].wid
                                    name = publication[0].name
                                else:
                                    refs = cmodels.PublicationReference.objects.filter(wid__startswith = "REF_")
                                    if refs.exists():
                                        last = refs.reverse()[0]
                                        next_id = int(last.wid[4:], 10) + 1
                                        
                                        wid = "REF_" + "%04d" % (next_id)
                                        name = "Reference #%04d" % (next_id)
                                    else:
                                        wid = "REF_0001"
                                        name = "Reference #0001"
                            
                            try:
                                pubref = cmodels.PublicationReference.objects.get(wid = slugify(wid))
                            except ObjectDoesNotExist:
                                pubref = cmodels.PublicationReference(wid = slugify(wid))
                            pubref.name = name
                            pubref.authors = ref.authors
                            pubref.title = ref.title
                            pubref.publication = ref.journal
                            pubref.save(revision_detail = revdetail)
    
                            if ref.pubmed_id:
                                wid = "PUBMED" + ":" + ref.pubmed_id
                                try:
                                    xref = cmodels.CrossReference.objects.get(wid = slugify(wid))
                                except ObjectDoesNotExist:
                                    xref = cmodels.CrossReference(wid = slugify(wid))
                                xref.name = wid
                                xref.xid = ref.pubmed_id
                                xref.source = "PUBMED"
                                xref.save(revision_detail = revdetail)
                                xref.species.add(species)
                                xref.save(revision_detail = revdetail)
                                pubref.cross_references.add(xref)
    
                            if ref.medline_id:
                                wid = "MEDLINE" + ":" + ref.medline_id
                                try:
                                    xref = cmodels.CrossReference.objects.get(wid = slugify(wid))
                                except ObjectDoesNotExist:
                                    xref = cmodels.CrossReference(wid = slugify(wid))
                                xref.name = wid
                                xref.xid = ref.medline_id
                                xref.source = "MEDLINE"
                                xref.save(revision_detail = revdetail)
                                xref.species.add(species)
                                xref.save(revision_detail = revdetail)
                                pubref.cross_references.add(xref)
                                
                            pubref.species.add(species)
                            pubref.save(revision_detail = revdetail)
                            species.publication_references.add(pubref)
    
                        species.save(revision_detail = revdetail)
    
                    if "gi" in anno:
                        wid = "GI" + ":" + anno["gi"]
                        try:
                            xref = cmodels.CrossReference.objects.get(wid = slugify(wid))
                        except ObjectDoesNotExist:
                            xref = cmodels.CrossReference(wid = slugify(wid))
                        xref.name = wid
                        xref.xid = anno["gi"]
                        xref.source = "GI"
                        xref.save(revision_detail = revdetail)
                        xref.species.add(species)
                        xref.save(revision_detail = revdetail)
                        species.cross_references.add(xref)
                        species.save(revision_detail = revdetail)

                    try:
                        chromosome = cmodels.Chromosome.objects.get(wid = chr_name)
                    except ObjectDoesNotExist:
                        chromosome = cmodels.Chromosome(wid = chr_name)
                    chromosome.name = options["name"]
                    chromosome.sequence = record.seq
                    chromosome.length = len(record.seq)
                    chromosome.save(revision_detail = revdetail)
                    chromosome.species.add(species)
                    chromosome.save(revision_detail = revdetail)
                    
                    features = record.features
                    
                    gene_features = filter(lambda x : x.type == "gene", features)
                    cds_features = filter(lambda x : x.type in ["CDS", "ncRNA", "rRNA", "tmRNA", "tRNA"], features)
                    
                    gene_map = {}
                    for g in gene_features:
                        if not "locus_tag" in g.qualifiers:
                            self.stderr.write("WARN: " + str(g) + " without locus")
                            continue
                        loci = g.qualifiers["locus_tag"][0]
                        if loci in gene_map:
                            raise CommandError("locus_tag " + loci + " appeared twice")
                        gene_map[loci] = g
                    
                    cds_map = {}
                    for c in cds_features:
                        if not "locus_tag" in c.qualifiers:
                            self.stderr.write("WARN: " + str(c) + " without locus")
                            continue
                        loci = c.qualifiers["locus_tag"][0]
                        if loci in cds_map:
                            raise CommandError("locus_tag " + loci + " appeared twice")
                        if loci in gene_map:
                            cds_map[loci] = c
                    
                    sorted_cds_values = sorted(cds_map.values(), key = lambda x: x.qualifiers["locus_tag"])
                    for i, v in enumerate(sorted_cds_values):
                        qualifiers = v.qualifiers
                        try:
                            g = cmodels.Gene.objects.get(wid = slugify(qualifiers["locus_tag"][0]))
                        except ObjectDoesNotExist:
                            g = cmodels.Gene(wid = slugify(qualifiers["locus_tag"][0]))
    
                        g.chromosome = chromosome
    
                        if "gene" in qualifiers:
                            g.name = qualifiers["gene"][0]
                            g.symbol = qualifiers["gene"][0]
    
                        g.direction = 'f' if v.location.strand == 1 else 'r'
                        
                        # __len__ because len() fails for numbers < 0
                        # Joins output the wrong length
                        if v.location.__len__() < 0:
                            g.length = v.location.__len__() + len(record.seq)
                        else:
                            g.length = len(v.location)
                        
                        g.coordinate = v.location.start + 1 if 'f' else v.location.start
    
                        if "note" in qualifiers:
                            g.comments = "\n".join(qualifiers["note"])
                        
                        g.save(revision_detail = revdetail)
                        
                        if "db_xref" in qualifiers:
                            for xref in qualifiers["db_xref"]:
                                if ":" in xref:
                                    source, xid = xref.split(":")
                                    wid = source + ":" + xid
                                    try:
                                        xref = cmodels.CrossReference.objects.get(wid = slugify(wid))
                                    except ObjectDoesNotExist:
                                        xref = cmodels.CrossReference(wid = slugify(wid))
                                    xref.name = wid
                                    xref.xid = xid
                                    xref.source = source
                                                                    
                                    xref.save(revision_detail = revdetail)
                                    xref.species.add(species)
                                    g.cross_references.add(xref)
                                    xref.save(revision_detail = revdetail)
                        
                        if "EC_number" in qualifiers:
                            for ec in qualifiers["EC_number"]:
                                wid = "EC" + ":" + ec
                                try:
                                    xref = cmodels.CrossReference.objects.get(wid = slugify(wid))
                                except ObjectDoesNotExist:
                                    xref = cmodels.CrossReference(wid = slugify(wid))
                                xref.name = wid
                                xref.source = "EC"
                                xref.xid = ec
                                xref.save(revision_detail = revdetail)
                                xref.species.add(species)
                                g.cross_references.add(xref)
                                xref.save(revision_detail = revdetail)
                        
                        if "gene_synonym" in qualifiers:
                            for synonym in qualifiers["gene_synonym"]:
                                # Inconsistency: Multiple synonyms appear in one entry,
                                # why don't they split them like for all other items?
                                for syn in synonym.split(";"):
                                    try:
                                        obj = cmodels.Synonym.objects.get(name = syn.strip())
                                    except ObjectDoesNotExist:
                                        obj = cmodels.Synonym(name = syn.strip())
                                    obj.save()
                                    g.synonyms.add(obj)
                        
                        if "protein_id" in qualifiers:
                            protxref = qualifiers["protein_id"][0]
                            protxref_wid = "Refseq" + ":" + protxref
                            wid = slugify(g.wid + "_Monomer")
                            try:
                                protein = cmodels.ProteinMonomer.objects.get(wid = wid)
                            except ObjectDoesNotExist:
                                protein = cmodels.ProteinMonomer(wid = wid)
                     
                            if "product" in qualifiers:
                                protein.name = qualifiers["product"][0]
                                
                            try:
                                xref = cmodels.CrossReference.objects.get(wid = slugify(protxref_wid))
                            except ObjectDoesNotExist:
                                xref = cmodels.CrossReference(wid = slugify(protxref_wid))
                            
                            protein.gene = g
                            protein.save(revision_detail = revdetail)

                            protein.species.add(species)
                        
                            xref.xid = protxref
                            xref.source = "RefSeq"
                            xref.save(revision_detail = revdetail)
                            xref.species.add(species)
                            xref.save(revision_detail = revdetail)
                            protein.cross_references.add(xref)
                            protein.save(revision_detail = revdetail)

                        g.save(revision_detail = revdetail)
                        g.species.add(species)
                        
                        if v.type == "CDS":
                            v.type = "mRNA"
                        
                        try:
                            t = cmodels.Type.objects.get(wid = slugify(v.type))
                        except ObjectDoesNotExist:
                            t = cmodels.Type(wid = slugify(v.type), name = v.type)
    
                        t.save(revision_detail = revdetail)
                        t.species.add(species)
                        t.save(revision_detail = revdetail)
    
                        g.type.add(t)
                        
                        g.save(revision_detail = revdetail)
                        self.stdout.write("Importing Gene %s (%d/%d)%10s\r" % (g.wid, i + 1, len(cds_map.values()), " "))
    