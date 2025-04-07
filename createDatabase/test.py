import pandas as pd
import sqlite3
import re
from collections import Counter

sqlite_db = "./db.sqlite3"
conn = sqlite3.connect(sqlite_db)
cursor = conn.cursor()

organisms = {
    "Homo sapiens (Human)": ["human", "homo sapiens", "h. sapiens", "homo"],
    "Mus musculus (Mouse)": ["mouse", "mus musculus", "m. musculus", "mus"],
    "Rattus norvegicus (Rat)": ["rat", "rattus norvegicus", "r. norvegicus", "rattus"],
    "All": []
}

def normalize_assay_name(assay):
    if not assay:
        return "Unknown"
    assay = assay.strip()
    if re.search(r'lucifer(a|e)se', assay.lower()):
        return "Luciferase Assay"
    elif re.search(r'reporter|gfp|lacz|yfp|rfp', assay.lower()):
        return "Reporter Assay"
    elif re.search(r'knock.?out|ko\b|crispr|deletion|knockout', assay.lower()):
        return "Knock-out Assay"
    elif re.search(r'sif.?seq', assay.lower()):
        return "SIF-seq"
    elif re.search(r'starr.?seq', assay.lower()):
        return "STARR-seq"
    elif re.search(r'capstarr.?seq', assay.lower()):
        return "CAPSTARR-seq"
    elif re.search(r'transgenic', assay.lower()):
        return "Transgenic Assay"
    elif re.search(r'shrna|rnai|interference', assay.lower()):
        return "RNA Interference"
    return assay

# First, check what genome assemblies are actually used in the database
cursor.execute("SELECT DISTINCT genomeAssemblyAsReported FROM enhancers WHERE genomeAssemblyAsReported IS NOT NULL AND genomeAssemblyAsReported != ''")
all_assemblies = [row[0] for row in cursor.fetchall() if row[0]]
print(f"Found these genome assemblies in database: {all_assemblies}")

# Debug: get species-assembly distribution
cursor.execute("""
    SELECT organism, genomeAssemblyAsReported, COUNT(*) 
    FROM enhancers 
    WHERE organism IS NOT NULL AND genomeAssemblyAsReported IS NOT NULL 
    GROUP BY organism, genomeAssemblyAsReported
""")
print("\nOrganism and assembly distribution:")
for row in cursor.fetchall():
    if row[0] and row[1]:  # Only print if both fields have values
        print(f"  {row[0]}: {row[1]} - {row[2]} enhancers")

paper_counts = {}
enhancer_counts = {}
tissue_cell_stats = {}
gene_target_stats = {}
chromosome_stats = {}
assay_results = {}
genome_stats = {}

for org_name, org_variations in organisms.items():
    # Create the proper organism filter
    if org_variations:
        organism_clauses = []
        for name in org_variations:
            organism_clauses.append(f"LOWER(e.organism) LIKE '%{name.lower()}%'")
        organism_filter = "WHERE (" + " OR ".join(organism_clauses) + ")"
        
        simple_organism_clauses = []
        for name in org_variations:
            simple_organism_clauses.append(f"LOWER(organism) LIKE '%{name.lower()}%'")
        simple_organism_filter = "WHERE (" + " OR ".join(simple_organism_clauses) + ")"
    else:
        organism_filter = ""
        simple_organism_filter = ""
    
    # Total Number of Papers Curated
    query = f"""
        SELECT COUNT(DISTINCT ev.doi) 
        FROM evidence ev
        JOIN activity a ON ev.evidenceID = a.evidenceID
        JOIN enhancers e ON a.enhancerID = e.enhancerID
        {organism_filter}
    """
    cursor.execute(query)
    paper_counts[org_name] = cursor.fetchone()[0]
    
    # Total Number of Enhancers Curated
    if simple_organism_filter:
        query = f"""
            SELECT COUNT(DISTINCT enhancerID)
            FROM enhancers
            {simple_organism_filter}
        """
    else:
        query = """
            SELECT COUNT(DISTINCT enhancerID)
            FROM enhancers
        """
    cursor.execute(query)
    enhancer_counts[org_name] = cursor.fetchone()[0]
    
    # Total Number of Tissues/Cells Reported & Top Tissues/Cells
    query = f"""
        SELECT t.tissue, COUNT(*) as count
        FROM targets t
        JOIN activity a ON t.targetID = a.targetID
        JOIN enhancers e ON a.enhancerID = e.enhancerID
        {organism_filter} AND t.tissue IS NOT NULL AND t.tissue != ''
        GROUP BY t.tissue
        ORDER BY count DESC
    """
    cursor.execute(query)
    tissues = cursor.fetchall()
    
    query = f"""
        SELECT t.cell, COUNT(*) as count
        FROM targets t
        JOIN activity a ON t.targetID = a.targetID
        JOIN enhancers e ON a.enhancerID = e.enhancerID
        {organism_filter} AND t.cell IS NOT NULL AND t.cell != ''
        GROUP BY t.cell
        ORDER BY count DESC
    """
    cursor.execute(query)
    cells = cursor.fetchall()
    
    total_tissues_cells = len(tissues) + len(cells)
    
    # Store top tissues/cells
    tissue_cell_stats[org_name] = {
        "Total": total_tissues_cells,
        "Top": []
    }
    
    # Combine tissues and cells for ranking
    combined = []
    for tissue, count in tissues:
        combined.append((f"Tissue: {tissue}", count))
    for cell, count in cells:
        combined.append((f"Cell: {cell}", count))
    
    # Sort by count descending
    combined.sort(key=lambda x: x[1], reverse=True)
    
    # Get top 3 (or fewer if not enough data)
    for i, (name, count) in enumerate(combined[:3], 1):
        tissue_cell_stats[org_name]["Top"].append((name, count))
    
    # Make sure we have 3 entries, adding placeholders if needed
    while len(tissue_cell_stats[org_name]["Top"]) < 3:
        tissue_cell_stats[org_name]["Top"].append(("Not Available", 0))
    
    # Number of Gene Targets Reported and Top Targets
    query = f"""
        SELECT COUNT(DISTINCT t.targetID)
        FROM targets t
        JOIN activity a ON t.targetID = a.targetID
        JOIN enhancers e ON a.enhancerID = e.enhancerID
        {organism_filter} AND t.geneName IS NOT NULL AND t.geneName != 'unknown' AND t.geneName != 'Unknown'
    """
    cursor.execute(query)
    total_targets = cursor.fetchone()[0]
    
    query = f"""
        SELECT t.geneName, COUNT(DISTINCT a.activityID) as count
        FROM targets t
        JOIN activity a ON t.targetID = a.targetID
        JOIN enhancers e ON a.enhancerID = e.enhancerID
        {organism_filter} AND t.geneName IS NOT NULL AND t.geneName != 'unknown' AND t.geneName != 'Unknown'
        GROUP BY t.geneName
        ORDER BY count DESC
        LIMIT 3
    """
    cursor.execute(query)
    top_targets = cursor.fetchall()
    
    # Unknown Targets
    query = f"""
        SELECT COUNT(DISTINCT a.activityID)
        FROM activity a
        JOIN targets t ON a.targetID = t.targetID
        JOIN enhancers e ON a.enhancerID = e.enhancerID
        {organism_filter} AND (t.geneName IS NULL OR t.geneName = 'unknown' OR t.geneName = 'Unknown')
    """
    cursor.execute(query)
    unknown_targets = cursor.fetchone()[0]
    
    # Store gene target stats
    gene_target_stats[org_name] = {
        "Total": total_targets,
        "Top": [],
        "Unknown": unknown_targets
    }
    
    # Store top targets
    for i, (target, count) in enumerate(top_targets, 1):
        gene_target_stats[org_name]["Top"].append((target, count))
    
    # Make sure we have 3 entries, adding placeholders if needed
    while len(gene_target_stats[org_name]["Top"]) < 3:
        gene_target_stats[org_name]["Top"].append(("Not Available", 0))
    
    # Number of Enhancers found in Chromosomes
    if simple_organism_filter:
        query = f"""
            SELECT chromosomeNumberAsReported, COUNT(DISTINCT enhancerID) as count
            FROM enhancers
            {simple_organism_filter} AND chromosomeNumberAsReported IS NOT NULL AND chromosomeNumberAsReported != ''
            GROUP BY chromosomeNumberAsReported
            ORDER BY count DESC
            LIMIT 3
        """
    else:
        query = """
            SELECT chromosomeNumberAsReported, COUNT(DISTINCT enhancerID) as count
            FROM enhancers
            WHERE chromosomeNumberAsReported IS NOT NULL AND chromosomeNumberAsReported != ''
            GROUP BY chromosomeNumberAsReported
            ORDER BY count DESC
            LIMIT 3
        """
    cursor.execute(query)
    top_chromosomes = cursor.fetchall()
    
    # Get all chromosomes to check for any without enhancers
    if simple_organism_filter:
        query = f"""
            SELECT DISTINCT chromosomeNumberAsReported
            FROM enhancers
            {simple_organism_filter} AND chromosomeNumberAsReported IS NOT NULL AND chromosomeNumberAsReported != ''
        """
    else:
        query = """
            SELECT DISTINCT chromosomeNumberAsReported
            FROM enhancers
            WHERE chromosomeNumberAsReported IS NOT NULL AND chromosomeNumberAsReported != ''
        """
    cursor.execute(query)
    all_chromosomes = [row[0] for row in cursor.fetchall() if row[0]]
    
    # Store chromosome stats
    chromosome_stats[org_name] = {
        "Top": [],
        "All": all_chromosomes
    }
    
    # Store top chromosomes
    for i, (chrom, count) in enumerate(top_chromosomes, 1):
        chromosome_stats[org_name]["Top"].append((chrom, count))
    
    # Make sure we have 3 entries, adding placeholders if needed
    while len(chromosome_stats[org_name]["Top"]) < 3:
        chromosome_stats[org_name]["Top"].append(("Not Available", 0))
    
    # PART 1: ASSAY ANALYSIS
    query = f"""
        SELECT ev.methodAssay, COUNT(*) as count
        FROM evidence ev
        JOIN activity a ON ev.evidenceID = a.evidenceID
        JOIN enhancers e ON a.enhancerID = e.enhancerID
        {organism_filter}
        GROUP BY ev.methodAssay
        ORDER BY count DESC
    """
    
    cursor.execute(query)
    raw_assay_results = cursor.fetchall()
    
    normalized_assays = {}
    for assay, count in raw_assay_results:
        normalized_name = normalize_assay_name(assay)
        normalized_assays[normalized_name] = normalized_assays.get(normalized_name, 0) + count
    
    sorted_assays = sorted(normalized_assays.items(), key=lambda x: x[1], reverse=True)
    assay_results[org_name] = sorted_assays
    
    # PART 2: GENOME ANALYSIS
    # First, get mappings of assemblies to expected species
    human_assemblies = ["hg17", "hg18", "hg19", "hg38"]
    mouse_assemblies = ["mm5", "mm7", "mm8", "mm9", "mm10"]
    rat_assemblies = ["rn5", "rn6"]
    
    # Determine which assemblies to query based on organism
    if "Human" in org_name:
        relevant_assemblies = human_assemblies
    elif "Mouse" in org_name:
        relevant_assemblies = mouse_assemblies
    elif "Rat" in org_name:
        relevant_assemblies = rat_assemblies
    else:  # All
        relevant_assemblies = human_assemblies + mouse_assemblies + rat_assemblies
    
    # Get counts for specific genome assemblies
    assembly_counts = {}
    for assembly in relevant_assemblies:
        if simple_organism_filter:
            query = f"""
                SELECT COUNT(DISTINCT enhancerID)
                FROM enhancers
                {simple_organism_filter} AND LOWER(genomeAssemblyAsReported) = LOWER('{assembly}')
            """
        else:
            query = f"""
                SELECT COUNT(DISTINCT enhancerID)
                FROM enhancers
                WHERE LOWER(genomeAssemblyAsReported) = LOWER('{assembly}')
            """
        cursor.execute(query)
        count = cursor.fetchone()[0]
        if count > 0:
            assembly_counts[assembly] = count
    
    # Calculate total as sum of recognized assemblies
    total_count = sum(assembly_counts.values())
    
    # Get extrapolated to hg38 count (only for enhancers with recognized assemblies)
    assembly_list = "', '".join([a.lower() for a in relevant_assemblies])
    if simple_organism_filter:
        query = f"""
            SELECT COUNT(DISTINCT enhancerID)
            FROM enhancers
            {simple_organism_filter} 
            AND LOWER(genomeAssemblyAsReported) IN ('{assembly_list}')
            AND hg38Chromosome IS NOT NULL AND hg38Start IS NOT NULL AND hg38End IS NOT NULL
        """
    else:
        query = f"""
            SELECT COUNT(DISTINCT enhancerID)
            FROM enhancers
            WHERE LOWER(genomeAssemblyAsReported) IN ('{assembly_list}')
            AND hg38Chromosome IS NOT NULL AND hg38Start IS NOT NULL AND hg38End IS NOT NULL
        """
    cursor.execute(query)
    extrapolated_count = cursor.fetchone()[0]
    
    # Store the results
    genome_stats[org_name] = {
        "Total Draft Genome Reported": total_count,
        **assembly_counts,
        "Extrapolated to hg38": extrapolated_count
    }

# Print basic statistics
for org_name in organisms.keys():
    print(f"\nStatistics for {org_name}:")
    print("-" * 60)
    print(f"Total Number of Papers Curated: {paper_counts[org_name]}")
    print(f"Total Number of Enhancers Curated: {enhancer_counts[org_name]}")
    print(f"Total Number of Tissues/Cells Reported: {tissue_cell_stats[org_name]['Total']}")
    
    for i, (name, count) in enumerate(tissue_cell_stats[org_name]["Top"], 1):
        if count > 0:
            print(f"  Top {i}: {name} ({count})")
        else:
            print(f"  Top {i}: No data available")

# Print assay results
for org_name, assays in assay_results.items():
    print(f"\nAssay Types for {org_name}:")
    print("-" * 60)
    print(f"{'Rank':<6}{'Assay Type':<40}{'Count':<10}")
    print("-" * 60)
    
    for i, (assay, count) in enumerate(assays, 1):
        print(f"{i:<6}{assay:<40}{count:<10}")

# Print genome results
for org_name, stats in genome_stats.items():
    print(f"\nGenome Statistics for {org_name}:")
    print("-" * 60)
    print(f"Total Draft Genome Reported: {stats['Total Draft Genome Reported']}")
    
    # Only print relevant assemblies
    if "Human" in org_name:
        assemblies_to_show = human_assemblies
    elif "Mouse" in org_name:
        assemblies_to_show = mouse_assemblies
    elif "Rat" in org_name:
        assemblies_to_show = rat_assemblies
    else:  # All
        assemblies_to_show = human_assemblies + mouse_assemblies + rat_assemblies
    
    for assembly in assemblies_to_show:
        count = stats.get(assembly, 0)
        if count > 0:
            print(f"  {assembly}: {count}")
    
    print(f"Extrapolated to hg38: {stats['Extrapolated to hg38']}")
    
    # Print gene target stats
    print(f"\nGene Target Statistics for {org_name}:")
    print("-" * 60)
    print(f"Number of Gene Targets Reported: {gene_target_stats[org_name]['Total']}")
    
    for i, (target, count) in enumerate(gene_target_stats[org_name]["Top"], 1):
        if count > 0:
            print(f"  Top {i}: {target} ({count})")
        else:
            print(f"  Top {i}: No data available")
    
    print(f"Unknown Targets: {gene_target_stats[org_name]['Unknown']}")
    
    # Print chromosome stats
    print(f"\nChromosome Statistics for {org_name}:")
    print("-" * 60)
    print(f"Number of Enhancers found in Chromosomes:")
    
    for i, (chrom, count) in enumerate(chromosome_stats[org_name]["Top"], 1):
        if count > 0:
            print(f"  Top {i}: Chromosome {chrom} ({count} enhancers)")
        else:
            print(f"  Top {i}: No data available")
    
    # Check for chromosomes without enhancers
    if "Human" in org_name:
        expected_chromosomes = [str(i) for i in range(1, 23)] + ["X", "Y"]
        missing = [c for c in expected_chromosomes if c not in chromosome_stats[org_name]["All"]]
    elif "Mouse" in org_name:
        expected_chromosomes = [str(i) for i in range(1, 20)] + ["X", "Y"]
        missing = [c for c in expected_chromosomes if c not in chromosome_stats[org_name]["All"]]
    elif "Rat" in org_name:
        expected_chromosomes = [str(i) for i in range(1, 21)] + ["X", "Y"]
        missing = [c for c in expected_chromosomes if c not in chromosome_stats[org_name]["All"]]

conn.close()

print("\nCombined statistics analysis completed")