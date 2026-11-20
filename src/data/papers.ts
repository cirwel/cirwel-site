import catalog from './papers.json';

interface Creator {
  name: string;
  citationName: string;
  type: string;
  orcid: string;
  institutions: string[];
}

interface CatalogPaper {
  slug: string;
  section: string;
  doi: string;
  conceptDoi?: string;
  title: string;
  researchTitle: string;
  publicationDate: string;
  citationDate: string;
  displayDate: string;
  displayVersion: string;
  pdfFile: string;
  repo: string;
  keywords: string[];
  summary: string;
  abstract: string[];
  // Earlier curated entries have a single author and license.
  author?: string;
  citationAuthor?: string;
  institution?: string;
  orcid?: string;
  license?: string;
  creators?: Creator[];
  rights?: { label: string; url: string }[];
  languages?: string[];
  publicationType?: string;
  publisher?: string;
}

const entries: CatalogPaper[] = catalog;

export default entries.map((paper) => ({
  ...paper,
  creators: paper.creators ?? [{
    name: paper.author ?? '', citationName: paper.citationAuthor ?? '', type: 'Person',
    orcid: paper.orcid ?? '', institutions: paper.institution ? [paper.institution] : [],
  }],
  rights: paper.rights ?? (paper.license ? [{
    label: paper.license.includes('apache') ? 'Apache-2.0' : 'CC-BY 4.0', url: paper.license,
  }] : []),
  languages: paper.languages ?? ['en'],
  publicationType: paper.publicationType ?? (paper.section === 'studies' ? 'Study report' : 'Preprint'),
}));
