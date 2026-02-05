// Mock data for CareerGold
// Based on Stitch wireframe placeholder content

export interface Job {
    id: string;
    title: string;
    company: string;
    location: string;
    matchScore: number;
    applicants: number;
    applicants_count?: number; // Added for explicit scraped count
    postedAgo: string;
    posted_date?: string;      // Added for raw scraped date string
    salary?: string;
    salary_range?: string;     // Alias for salary
    job_type?: string;         // Added for scraped job type
    status: 'NEW' | 'SAVED' | 'APPLIED' | 'REJECTED';
    description?: string;
    snippet?: string;  // Added for scraped jobs
    link?: string;     // Added for external link
    apply_link?: string; // Added for explicit apply link
    url?: string;      // Alias for link
    responsibilities?: string[];
    requirements?: string[];
    skills?: { name: string; matched: boolean }[];
    raw_data?: any;    // Added for debugging/full scraped data
    companyInfo?: {
        size: string;
        industry: string;
    };
}

export interface Application {
    id: string;
    jobId: string;
    jobTitle: string;
    company: string;
    status: 'Queued' | 'Submitting' | 'Submitted' | 'REJECTED' | 'Manual follow-up';
    submittedAt?: string;
    cvVersion: string;
}

export interface SearchRun {
    id: string;
    status: 'Idle' | 'Running' | 'Paused' | 'Completed';
    progress: number;
    resultsCount: number;
}

export interface SourceConnection {
    name: string;
    status: 'Not connected' | 'Connected' | 'Rate-limited' | 'Error';
}

export interface CVGeneration {
    id: string;
    jobId: string;
    status: 'Drafting' | 'Ready' | 'Needs review' | 'Error';
    version: string;
}

// Mock Jobs Data (from Stitch wireframe)
export const mockJobs: Job[] = [
    {
        id: 'job-001',
        title: 'Software Engineer Intern',
        company: 'Tech Corp Systems',
        location: 'San Francisco, CA (Remote)',
        matchScore: 98,
        applicants: 45,
        postedAgo: '2h',
        salary: '$80k - $100k',
        status: 'NEW',
        description: 'We are seeking an experienced Frontend Developer to join our core product team. You will be responsible for building high-quality, scalable web applications using React and Tailwind CSS.',
        responsibilities: [
            'Develop and maintain responsive web applications using React and TypeScript.',
            'Collaborate with UI/UX designers to implement design systems.',
            'Optimize application performance and ensure cross-browser compatibility.',
            'Participate in code reviews and mentor junior developers.',
        ],
        requirements: [
            'React', 'TypeScript', 'Tailwind CSS', 'Node.js'
        ],
        skills: [
            { name: 'React', matched: true },
            { name: 'TypeScript', matched: true },
            { name: 'Tailwind CSS', matched: true },
            { name: 'Figma', matched: false },
            { name: 'Node.js', matched: true },
        ],
        companyInfo: {
            size: '1,000 - 5,000 Employees',
            industry: 'Enterprise Software',
        },
    },
    {
        id: 'job-002',
        title: 'Product Management Lead',
        company: 'Productify Inc.',
        location: 'New York, NY',
        matchScore: 85,
        applicants: 12,
        postedAgo: '1d',
        status: 'NEW',
        skills: [
            { name: 'Product Strategy', matched: true },
            { name: 'Agile', matched: true },
            { name: 'SQL', matched: false },
        ],
    },
    {
        id: 'job-003',
        title: 'Data Analyst Graduate',
        company: 'DataLog Solutions',
        location: 'Austin, TX',
        matchScore: 72,
        applicants: 88,
        postedAgo: '5h',
        status: 'NEW',
        skills: [
            { name: 'Python', matched: true },
            { name: 'SQL', matched: true },
            { name: 'Tableau', matched: false },
        ],
    },
    {
        id: 'job-004',
        title: 'Senior Frontend Developer',
        company: 'TechFlow Solutions',
        location: 'New York, NY (Hybrid)',
        matchScore: 85,
        applicants: 34,
        postedAgo: '2d',
        salary: '$140k - $180k',
        status: 'SAVED',
        description: 'We are seeking an experienced Frontend Developer to join our core product team.',
        skills: [
            { name: 'React', matched: true },
            { name: 'TypeScript', matched: true },
            { name: 'Tailwind CSS', matched: true },
            { name: 'Figma', matched: false },
            { name: 'Node.js', matched: true },
        ],
        companyInfo: {
            size: '1,000 - 5,000 Employees',
            industry: 'Enterprise Software',
        },
    },
];

// Mock Applications Data
export const mockApplications: Application[] = [
    {
        id: 'app-001',
        jobId: 'job-001',
        jobTitle: 'Software Engineer Intern',
        company: 'Tech Corp Systems',
        status: 'Submitted',
        submittedAt: '2h ago',
        cvVersion: 'v3.1',
    },
    {
        id: 'app-002',
        jobId: 'job-002',
        jobTitle: 'Product Management Lead',
        company: 'Productify Inc.',
        status: 'Queued',
        cvVersion: 'v2.0',
    },
    {
        id: 'app-003',
        jobId: 'job-003',
        jobTitle: 'Data Analyst Graduate',
        company: 'DataLog Solutions',
        status: 'Manual follow-up',
        cvVersion: 'v3.1',
    },
];

// Mock Search Run State
export const mockSearchRun: SearchRun = {
    id: 'search-001',
    status: 'Idle',
    progress: 0,
    resultsCount: 12,
};

// Mock Source Connections
export const mockSources: SourceConnection[] = [
    { name: 'LinkedIn', status: 'Connected' },
    { name: 'Indeed', status: 'Not connected' },
    { name: 'Greenhouse', status: 'Rate-limited' },
];

// Mock CV Generations
export const mockCVGenerations: CVGeneration[] = [
    { id: 'cv-001', jobId: 'job-001', status: 'Ready', version: 'v3.1' },
    { id: 'cv-002', jobId: 'job-002', status: 'Drafting', version: 'v2.0 (draft)' },
    { id: 'cv-003', jobId: 'job-003', status: 'Needs review', version: 'v3.0' },
];
