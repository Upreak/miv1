import { GoogleGenAI, Type } from "@google/genai";

// Initialize AI - In a real app, API_KEY comes from env. 
// For this demo, we gracefully handle missing keys by returning mocks.
const apiKey = process.env.API_KEY || '';
let ai: GoogleGenAI | null = null;

if (apiKey) {
  ai = new GoogleGenAI({ apiKey });
}

// Helper to clean Markdown code blocks from JSON strings
const cleanJsonString = (text: string): string => {
  let clean = text;
  // Remove markdown code blocks (```json ... ``` or just ``` ... ```)
  clean = clean.replace(/```json\s*([\s\S]*?)\s*```/g, '$1');
  clean = clean.replace(/```\s*([\s\S]*?)\s*```/g, '$1');
  return clean.trim();
};

export const parseResumeAI = async (resumeText: string): Promise<any> => {
  if (!ai) {
    console.warn("Gemini API Key not found. Returning mock parse data.");
    return mockParseResume();
  }

  try {
    const model = "gemini-2.5-flash";
    const prompt = `Extract the following details from the resume text: 
    Full Name, Email, Phone, Skills (array), Experience (years), Current CTC, Expected CTC.
    Resume Text: ${resumeText}`;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            fullName: { type: Type.STRING },
            email: { type: Type.STRING },
            phone: { type: Type.STRING },
            skills: { type: Type.ARRAY, items: { type: Type.STRING } },
            experience: { type: Type.NUMBER },
            currentCtc: { type: Type.STRING },
            expectedCtc: { type: Type.STRING },
          }
        }
      }
    });

    return JSON.parse(response.text || "{}");
  } catch (error) {
    console.error("AI Parse Error:", error);
    return mockParseResume();
  }
};

export const parseJobDescriptionAI = async (jdText: string): Promise<any> => {
  if (!ai) {
    console.warn("Gemini API Key not found. Returning mock JD data.");
    return mockParseJD();
  }

  try {
    const model = "gemini-2.5-flash";
    const prompt = `Extract structured job data from the following Job Description text.
    The output must be a valid JSON object matching the Google Jobs schema.
    
    Fields to extract strictly:
    - clientName (string): The company name.
    - title (string): The job title.
    - jobId (string): The internal reference code or job ID.
    - employmentType (FULL_TIME, PART_TIME, CONTRACTOR, TEMPORARY, INTERN)
    - workMode (On-site, Remote, Hybrid)
    - industry (string)
    - functionalArea (string)
    - minSalary (number): Extract the lower bound of salary.
    - maxSalary (number): Extract the upper bound of salary.
    - currency (string): e.g., USD, INR.
    - salaryUnit (YEAR, MONTH, HOUR)
    - benefitsPerks (array of strings): e.g., ["Health Insurance", "Incentives"]
    - aboutCompany (string): The 'About Company' section text.
    - jobSummary (string): The job summary or description.
    - responsibilities (array of strings): List of key duties.
    - experienceRequired (string): e.g., "3-5 years"
    - educationQualification (string): e.g., "Bachelor's Degree"
    - requiredSkills (array of strings): Mandatory skills.
    - preferredSkills (array of strings): Nice-to-have skills.
    - toolsTechStack (array of strings): e.g., Salesforce, HubSpot.
    - numberOfOpenings (number)
    - applicationDeadline (string): Date in YYYY-MM-DD format if available.
    - hiringProcessRounds (array of strings): e.g., ["Initial Screening", "Interview"]
    - noticePeriodAccepted (string): e.g., "Immediate to 30 Days"
    
    SEO & Metadata:
    - slugUrl (string): The URL slug found in text (e.g., /jobs/account-executive).
    - metaTitle (string): The SEO Meta Title.
    - metaDescription (string): The SEO Meta Description.

    JD Text:
    ${jdText}`;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      }
    });

    const parsed = JSON.parse(cleanJsonString(response.text || "{}"));
    
    // Fallback logic for SEO fields if AI missed them but data exists
    if (!parsed.slugUrl && parsed.title) {
        parsed.slugUrl = `${parsed.title.toLowerCase().replace(/ /g, '-')}-${parsed.clientName?.toLowerCase().replace(/ /g, '-') || 'job'}`;
    }
    if (!parsed.metaTitle && parsed.title) {
        parsed.metaTitle = `${parsed.title} at ${parsed.clientName || 'Top Company'} - Apply Now`;
    }
    if (!parsed.metaDescription && parsed.jobSummary) {
        parsed.metaDescription = parsed.jobSummary.substring(0, 150) + "...";
    }

    return parsed;
  } catch (error) {
    console.error("AI JD Parse Error:", error);
    return mockParseJD();
  }
};

export const searchJobsWithAI = async (prompt: string): Promise<any[]> => {
  if (!ai) {
    console.warn("Gemini API Key not found. Returning empty list.");
    return [];
  }

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash", 
      contents: prompt,
      config: {
        tools: [{ googleSearch: {} }],
      }
    });

    const rawText = response.text || "[]";
    const cleanedJson = cleanJsonString(rawText);
    
    try {
      const data = JSON.parse(cleanedJson);
      return Array.isArray(data) ? data : [];
    } catch (parseError) {
      console.warn("Failed to parse AI response as JSON. Raw:", rawText);
      const arrayMatch = rawText.match(/\[[\s\S]*\]/);
      if (arrayMatch) {
        try {
          return JSON.parse(arrayMatch[0]);
        } catch (e) { return []; }
      }
      return [];
    }
  } catch (error) {
    console.error("AI Job Search Error:", error);
    return [];
  }
};

export const generateChatResponse = async (
  history: { sender: string; text: string }[],
  candidateName: string,
  jobTitle: string
): Promise<string> => {
  if (!ai) {
     return `(Mock AI): Hi ${candidateName}, thanks for your interest in the ${jobTitle} role. Tell me about your experience.`;
  }

  try {
    const systemInstruction = `You are a professional AI Recruiter screening ${candidateName} for the position of ${jobTitle}.
    Be polite, professional, and concise. Ask relevant screening questions based on the context.
    Do not be repetitive. Keep answers under 50 words.`;

    const conversation = history.map(h => `${h.sender === 'bot' ? 'AI' : 'Candidate'}: ${h.text}`).join('\n');
    const prompt = `${conversation}\nAI:`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        systemInstruction,
        maxOutputTokens: 150,
      }
    });

    return response.text || "I didn't quite catch that, could you rephrase?";
  } catch (error) {
    console.error("Gemini Chat Error:", error);
    return "I'm having trouble connecting right now. Let's continue later.";
  }
};

const mockParseResume = () => ({
  fullName: "John Doe",
  email: "john.doe@example.com",
  phone: "+1 555 0199",
  skills: ["React", "TypeScript", "Node.js", "Tailwind"],
  experience: 5,
  currentCtc: "12 LPA",
  expectedCtc: "18 LPA"
});

const mockParseJD = () => ({
  title: "Senior Software Engineer",
  clientName: "Acme Corp",
  jobId: "ACME-001",
  employmentType: "FULL_TIME",
  workMode: "Hybrid",
  industry: "Technology",
  functionalArea: "Engineering",
  minSalary: 2000000,
  maxSalary: 4000000,
  currency: "INR",
  salaryUnit: "YEAR",
  aboutCompany: "Acme Corp is a leading innovator...",
  jobSummary: "We are looking for a skilled engineer...",
  responsibilities: ["Develop features", "Code review"],
  requiredSkills: ["React", "Node.js"],
  preferredSkills: ["AWS"],
  experienceRequired: "5+ Years",
  educationQualification: "B.Tech",
  benefitsPerks: ["Health Insurance", "Stock Options"],
  numberOfOpenings: 2,
  slugUrl: "senior-software-engineer-acme",
  metaTitle: "Senior Software Engineer at Acme Corp",
  metaDescription: "Join Acme Corp as a Senior Software Engineer."
});