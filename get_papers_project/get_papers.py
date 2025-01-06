import argparse
import csv
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


def fetch_papers(query, max_results=100, debug=False):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    if debug:
        print(f"Fetching papers for query: {query}")

    # Search for paper IDs
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&usehistory=y"
    response = requests.get(search_url)
    root = ET.fromstring(response.content)

    id_list = [id_elem.text for id_elem in root.findall(".//Id")]
    web_env = root.find(".//WebEnv").text
    query_key = root.find(".//QueryKey").text

    if debug:
        print(f"Found {len(id_list)} papers")

    # Fetch paper details
    fetch_url = f"{base_url}efetch.fcgi?db=pubmed&query_key={query_key}&WebEnv={web_env}&retmode=xml"
    response = requests.get(fetch_url)
    papers = ET.fromstring(response.content)

    return papers.findall(".//PubmedArticle")


def is_non_academic(affiliation):
    academic_keywords = ["university", "college", "institute", "school"]
    return not any(keyword in affiliation.lower() for keyword in academic_keywords)


def is_pharma_biotech(affiliation):
    pharma_biotech_keywords = ["pharma", "biotech", "pharmaceutical", "biotechnology"]
    return any(keyword in affiliation.lower() for keyword in pharma_biotech_keywords)


def filter_papers(papers, debug=False):
    filtered_papers = []
    for paper in papers:
        affiliations = paper.findall(".//Affiliation")
        authors = paper.findall(".//Author")
        non_academic_authors = []
        company_affiliations = set()

        for author in authors:
            last_name = author.find("LastName")
            fore_name = author.find("ForeName")
            if last_name is not None and fore_name is not None:
                author_name = f"{last_name.text} {fore_name.text}"
                author_affiliation = author.find("AffiliationInfo/Affiliation")
                if author_affiliation is not None and author_affiliation.text:
                    if is_non_academic(author_affiliation.text):
                        non_academic_authors.append(author_name)
                        if is_pharma_biotech(author_affiliation.text):
                            company_affiliations.add(author_affiliation.text.split(',')[0].strip())

        if non_academic_authors:
            paper_data = {
                'pmid': paper.find(".//PMID").text,
                'title': paper.find(".//ArticleTitle").text,
                'pub_date': get_publication_date(paper),
                'non_academic_authors': ', '.join(non_academic_authors),
                'company_affiliations': ', '.join(company_affiliations),
                'corresponding_author_email': get_corresponding_author_email(paper)
            }
            filtered_papers.append(paper_data)

    if debug:
        print(f"Filtered {len(filtered_papers)} papers with non-academic authors")

    return filtered_papers


def get_publication_date(paper):
    pub_date = paper.find(".//PubDate")
    year = pub_date.find("Year").text if pub_date.find("Year") is not None else ""
    month = pub_date.find("Month").text if pub_date.find("Month") is not None else ""
    day = pub_date.find("Day").text if pub_date.find("Day") is not None else ""

    if month.isalpha():
        try:
            month = datetime.strptime(month, "%b").month
        except ValueError:
            month = ""

    # Convert month and day to integers if possible
    try:
        month = int(month)
    except ValueError:
        month = ""

    try:
        day = int(day)
    except ValueError:
        day = ""

    if year and month and day:
        return f"{year}-{month:02d}-{day:02d}"
    elif year and month:
        return f"{year}-{month:02d}"
    else:
        return year


def get_corresponding_author_email(paper):
    for author in paper.findall(".//Author"):
        if author.get("ValidYN") == "Y" and author.find("AffiliationInfo/Affiliation") is not None:
            affiliation = author.find("AffiliationInfo/Affiliation").text
            email = next((word for word in affiliation.split() if "@" in word), None)
            if email:
                return email.strip(".")
    return ""


def write_output(papers, file=None, debug=False):
    fieldnames = ['PubmedID', 'Title', 'Publication Date', 'Non-academic Author(s)',
                  'Company Affiliation(s)', 'Corresponding Author Email']

    if file:
        with open(file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for paper in papers:
                write_paper(writer, paper)
        if debug:
            print(f"Results written to {file}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for paper in papers:
            write_paper(writer, paper)


def write_paper(writer, paper):
    writer.writerow({
        'PubmedID': paper['pmid'],
        'Title': paper['title'],
        'Publication Date': paper['pub_date'],
        'Non-academic Author(s)': paper['non_academic_authors'],
        'Company Affiliation(s)': paper['company_affiliations'],
        'Corresponding Author Email': paper['corresponding_author_email']
    })


def main():
    parser = argparse.ArgumentParser(description="Fetch and filter PubMed papers based on author affiliations.")
    parser.add_argument("query", help="PubMed search query")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information")
    parser.add_argument("-f", "--file", help="Specify the filename to save the results")
    args = parser.parse_args()

    if args.debug:
        print("Debug mode enabled")

    papers = fetch_papers(args.query, debug=args.debug)
    filtered_papers = filter_papers(papers, debug=args.debug)
    write_output(filtered_papers, args.file, debug=args.debug)


if __name__ == "__main__":
    main()