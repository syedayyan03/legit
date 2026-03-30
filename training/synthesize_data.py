import pandas as pd
import numpy as np
import random

def synthesize_real_jobs(n=10000):
    """Generate diverse, realistic job postings that mimic real web-scraped content."""
    
    titles = [
        "Senior Software Engineer", "Product Manager", "Project Manager", "Data Analyst",
        "Marketing Specialist", "Human Resources Manager", "Accountant", "Sales Executive",
        "Customer Success Manager", "UX Designer", "DevOps Engineer", "Financial Analyst",
        "Operations Coordinator", "Legal Counsel", "Administrative Assistant",
        "Backend Developer", "Frontend Developer", "Full Stack Developer", "Machine Learning Engineer",
        "Business Development Manager", "Content Writer", "Graphic Designer", "QA Engineer",
        "System Administrator", "Database Administrator", "Network Engineer", "Cloud Architect",
        "Scrum Master", "Technical Lead", "VP of Engineering", "Chief Technology Officer",
        "Data Scientist", "Research Scientist", "Security Engineer", "Mobile Developer",
        "iOS Developer", "Android Developer", "React Developer", "Python Developer",
        "Java Developer", "C++ Engineer", "Embedded Systems Engineer", "Firmware Engineer",
        "IT Support Specialist", "Help Desk Technician", "Technical Writer", "Solutions Architect",
        "Sales Engineer", "Account Executive", "Customer Service Representative", "Recruiter",
        "Talent Acquisition Specialist", "Compensation Analyst", "Benefits Administrator",
        "Office Manager", "Executive Assistant", "Paralegal", "Compliance Officer",
        "Risk Analyst", "Investment Banker", "Portfolio Manager", "Auditor"
    ]
    
    companies = [
        "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Tesla", "Adobe",
        "Salesforce", "Oracle", "IBM", "Intel", "Cisco", "SAP", "VMware",
        "Tech Solutions Inc.", "Global Marketing Group", "Financial Services Corp",
        "Innovation Hub", "HealthFirst Systems", "Retail Dynamics", "Consulting Partners",
        "Creative Studio", "Logistics Plus", "Sustainable Energy Ltd", "DataWorks Analytics",
        "CloudNine Technologies", "NextGen Software", "Pinnacle Digital", "Summit Healthcare",
        "Meridian Consulting", "Apex Technologies", "BlueShift Labs", "Horizon Media",
        "Sterling Financial", "Catalyst Innovation", "Vertex Solutions", "Quantum Computing Inc.",
        "PrimeHealth Corp", "EcoTech Solutions", "FutureWave Technologies"
    ]
    
    locations = [
        "New York, NY", "San Francisco, CA", "London, UK", "Berlin, Germany",
        "Austin, TX", "Seattle, WA", "Toronto, ON", "Sydney, NSW", "Tokyo, Japan",
        "Chicago, IL", "Los Angeles, CA", "Boston, MA", "Denver, CO", "Atlanta, GA",
        "Dallas, TX", "Miami, FL", "Portland, OR", "Minneapolis, MN", "Raleigh, NC",
        "Remote", "Hybrid - New York", "Hybrid - San Francisco", "Remote (US Only)"
    ]
    
    industries = [
        "Technology", "Finance", "Healthcare", "Marketing", "Retail", "Manufacturing",
        "Education", "Energy", "Legal", "Consulting", "Media", "Telecommunications",
        "Automotive", "Aerospace", "Pharmaceuticals", "Real Estate", "Insurance",
        "Banking", "Government", "Non-Profit"
    ]
    
    employment_types = ["Full-Time", "Part-Time", "Contract", "Internship", "Temporary"]
    
    experience_levels = [
        "Entry Level", "Mid Level", "Senior Level", "Lead", "Director", "Executive"
    ]

    description_templates = [
        "We are looking for a talented {title} to join our growing team at {company}. In this role, you will be responsible for {responsibility1} and {responsibility2}. You will collaborate with cross-functional teams to deliver high-quality solutions. Our ideal candidate has strong analytical skills and a passion for {industry}.",
        "{company} is seeking an experienced {title} to help drive innovation in our {industry} division. As a key member of our team, you will {responsibility1}, {responsibility2}, and contribute to the overall strategy. This is an excellent opportunity for someone who thrives in a fast-paced environment.",
        "Join {company} as a {title}! We are a leading company in the {industry} sector, and we need someone who can {responsibility1}. You will work closely with stakeholders to {responsibility2}. We value diversity, innovation, and collaboration.",
        "Are you passionate about {industry}? {company} is hiring a {title} who will {responsibility1} and {responsibility2}. We offer competitive compensation, excellent benefits, and opportunities for career growth. Our team has been recognized for our commitment to excellence.",
        "Position: {title} at {company}. Department: {industry}. We are expanding our team and need a dedicated professional who can {responsibility1}. The ideal candidate will also {responsibility2}. This role offers the chance to make a significant impact.",
        "{company} — {title}. About this role: We're building the future of {industry}, and we need your help. You'll {responsibility1} while also {responsibility2}. This is a {employment_type} position based in {location}.",
        "About the role: {company} is looking for a {title}. You will {responsibility1} and {responsibility2}. What we need: {experience} with proven track record in {industry}. What we offer: competitive salary, health benefits, growth opportunities.",
        "The {title} role at {company} involves {responsibility1}, {responsibility2}, and mentoring junior team members. Required: {experience} in {industry}. Preferred: advanced degree or equivalent experience. We are an equal opportunity employer.",
    ]
    
    responsibilities_pool = [
        "designing and implementing scalable systems",
        "managing cross-functional project deliverables",
        "analyzing data to drive business decisions",
        "developing and maintaining software applications",
        "creating marketing campaigns and strategies",
        "overseeing team operations and performance",
        "conducting code reviews and ensuring quality",
        "building and deploying cloud infrastructure",
        "leading agile development processes",
        "performing financial analysis and reporting",
        "writing technical documentation",
        "engaging with clients to understand requirements",
        "optimizing database performance",
        "developing machine learning models",
        "managing vendor relationships",
        "ensuring regulatory compliance",
        "coordinating recruitment activities",
        "designing user interfaces and experiences",
        "conducting market research",
        "monitoring system health and performance",
        "implementing security best practices",
        "creating business intelligence dashboards",
        "driving product roadmap discussions",
        "automating repetitive processes",
        "providing technical support and troubleshooting",
    ]
    
    requirements_templates = [
        "Bachelor's degree in {field} or related discipline. {years}+ years of experience. Strong {skill1} and {skill2} skills. Excellent communication abilities.",
        "Required: {years}+ years in a similar role. Proficiency in {skill1}. Experience with {skill2}. {field} background preferred. Team player with strong work ethic.",
        "Minimum {years} years of professional experience. Expertise in {skill1} and {skill2}. {field} degree or equivalent. Ability to work independently and in teams.",
        "Qualifications: Degree in {field}. {years}+ years experience. Must have {skill1} expertise. {skill2} knowledge is a plus. Strong problem-solving abilities.",
        "We require: A degree in {field} or equivalent experience. At least {years} years in the field. Demonstrated skills in {skill1} and {skill2}. Attention to detail."
    ]

    fields = ["Computer Science", "Engineering", "Business Administration", "Marketing",
              "Finance", "Information Technology", "Data Science", "Mathematics",
              "Communications", "Human Resources", "Accounting"]
    
    skills = ["Python", "Java", "SQL", "JavaScript", "project management", "data analysis",
              "team leadership", "cloud computing", "machine learning", "system design",
              "Excel", "communication", "problem-solving", "agile methodologies",
              "customer relationship management", "financial modeling", "strategic planning",
              "technical writing", "UI/UX design", "networking"]
    
    benefits_templates = [
        "Health insurance, dental and vision coverage, 401(k) matching, paid time off, professional development budget.",
        "Competitive salary, stock options, flexible working hours, remote work options, annual bonus.",
        "Comprehensive healthcare, retirement plan, gym membership, tuition reimbursement, parental leave.",
        "Medical, dental, vision insurance. Paid holidays. Learning and development programs. Employee assistance program.",
        "Attractive compensation package including base salary, performance bonus, equity, and comprehensive benefits.",
        "We offer medical/dental/vision insurance, unlimited PTO, 401k match, and a collaborative culture.",
    ]

    company_profiles = [
        "{company} is a leading {industry} company founded in {year}. With over {employees} employees worldwide, we are committed to innovation and excellence.",
        "At {company}, we believe in the power of {industry} to transform the world. Our team of {employees} professionals works every day to deliver exceptional results.",
        "{company} has been a trusted name in {industry} for over {age} years. We are proud of our diverse team and inclusive culture.",
        "Founded in {year}, {company} has grown to become one of the most respected names in the {industry} space. We foster a culture of growth and innovation.",
    ]

    data = []
    for _ in range(n):
        title = random.choice(titles)
        company = random.choice(companies)
        industry = random.choice(industries)
        location = random.choice(locations)
        employment_type = random.choice(employment_types)
        experience_level = random.choice(experience_levels)
        years = random.randint(1, 10)
        
        resp1, resp2 = random.sample(responsibilities_pool, 2)
        
        description = random.choice(description_templates).format(
            title=title, company=company, industry=industry,
            responsibility1=resp1, responsibility2=resp2,
            location=location, employment_type=employment_type,
            experience=f"{years}+ years experience"
        )
        
        skill1, skill2 = random.sample(skills, 2)
        field = random.choice(fields)
        requirements = random.choice(requirements_templates).format(
            field=field, years=years, skill1=skill1, skill2=skill2
        )
        
        benefits = random.choice(benefits_templates)
        
        year = random.randint(1990, 2020)
        employees = random.choice(["100", "500", "1,000", "5,000", "10,000", "50,000"])
        age = 2026 - year
        company_profile = random.choice(company_profiles).format(
            company=company, industry=industry, year=year, employees=employees, age=age
        )
        
        salary_min = random.randint(40, 120)
        salary_max = salary_min + random.randint(20, 80)
        
        data.append({
            "title": title,
            "description": description,
            "requirements": requirements,
            "company_profile": company_profile,
            "location": location,
            "salary_range": f"${salary_min}k - ${salary_max}k",
            "employment_type": employment_type,
            "industry": industry,
            "benefits": benefits,
            "fraudulent": 0
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Loading fake job postings dataset...")
    df_fake = pd.read_csv('dataset/fake_job_postings.csv')
    df_fake = df_fake.fillna('')
    print(f"Fake postings: {len(df_fake)}")
    
    print("Generating synthetic real job postings...")
    df_real = synthesize_real_jobs(len(df_fake))
    print(f"Real postings: {len(df_real)}")
    
    df_balanced = pd.concat([df_fake, df_real], ignore_index=True)
    df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    df_balanced.to_csv('dataset/job_postings_balanced.csv', index=False)
    print(f"Balanced dataset saved: {len(df_balanced)} rows ({len(df_fake)} fake, {len(df_real)} real)")
