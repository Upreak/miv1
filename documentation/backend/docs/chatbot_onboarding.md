# Chatbot Onboarding Guide

## For Recruiters

### Getting Started

1. **Access the Chatbot Interface**
   - Navigate to your recruiter dashboard
   - Click on "Chatbot" in the sidebar menu
   - You'll see the chat interface and management panels

2. **Set Up Your Profile**
   - Go to Settings → Profile
   - Upload your profile picture
   - Set your availability hours
   - Configure notification preferences

### Creating Prescreen Questions

1. **Navigate to Job Management**
   - Go to Jobs → Manage Jobs
   - Select a job posting
   - Click on "Prescreen Questions" tab

2. **Add Questions**
   - Use the default questions provided
   - Customize questions for specific roles
   - Set question types (text, number, select, etc.)
   - Mark critical questions as "Must Have"

3. **Example Question Setup**
   ```json
   {
     "qid": "ps_current_ctc",
     "question_text": "What is your current CTC (LPA)?",
     "type": "number",
     "required": true,
     "must_have": true,
     "weight": 10,
     "validation_rule": "min:0,max:100"
   }
   ```

### Managing Candidate Outreach

1. **View Candidate Matches**
   - Go to Candidates → Matches
   - Filter by job, match score, or status
   - Review candidate profiles and prescreen results

2. **Send Outreach Messages**
   - Select candidates for outreach
   - Choose outreach template
   - Send personalized messages via WhatsApp/Email

3. **Track Responses**
   - Monitor response rates
   - View conversation history
   - Update candidate status

### Exporting Candidates

1. **Select Candidates**
   - Choose applications for export
   - Verify candidate information
   - Confirm export settings

2. **Generate Export**
   - Click "Export to Client"
   - Select export options (resumes, JSON, etc.)
   - Wait for export completion

3. **Download and Share**
   - Access download link when ready
   - Share with client SPOC
   - Track client feedback

## For Candidates

### Starting the Conversation

1. **Initiate Contact**
   - Send "Hi" to the WhatsApp number
   - Or visit the web chat interface
   - Click "Start Application" button

2. **Session Setup**
   - Provide your name and email
   - Select your preferred job category
   - Confirm you want to proceed

### Completing Prescreen Questions

1. **Answer Questions Honestly**
   - Current CTC: Your total annual compensation
   - Expected CTC: Your salary expectation
   - Notice Period: How soon you can join
   - Total Experience: Years of relevant work experience

2. **Provide Accurate Information**
   - Skills: List your technical skills
   - Location: Current and preferred work locations
   - Availability: When you're available for interviews

3. **Example Answers**
   ```
   Current CTC: 10.5
   Expected CTC: 15.0
   Notice Period: 60
   Total Experience: 5
   Skills: Python, FastAPI, SQL, AWS
   ```

### Uploading Documents

1. **Resume Upload**
   - Send your resume as PDF or DOCX
   - Ensure file size is under 10MB
   - Use standard file formats

2. **Additional Documents**
   - Certifications (if requested)
   - Portfolio links
   - Work samples

### Tracking Application Status

1. **Check Status**
   - Send "status" to check application progress
   - View match score and feedback
   - Get timeline for next steps

2. **Update Information**
   - Send updated resume if needed
   - Modify preferences
   - Change availability

3. **Communication**
   - Respond to recruiter messages promptly
   - Ask questions about the role
   - Confirm interview schedules

## Best Practices

### For Recruiters

1. **Question Design**
   - Keep questions clear and concise
   - Use appropriate question types
   - Set realistic validation rules
   - Weight questions based on importance

2. **Candidate Engagement**
   - Respond to candidate queries quickly
   - Provide regular updates
   - Personalize communication
   - Set clear expectations

3. **Data Management**
   - Regularly review and update questions
   - Monitor match score accuracy
   - Track conversion rates
   - Analyze outreach effectiveness

### For Candidates

1. **Profile Completeness**
   - Provide complete and accurate information
   - Keep resume updated
   - Be honest about skills and experience
   - Specify clear career goals

2. **Communication**
   - Respond promptly to messages
   - Ask relevant questions about roles
   - Be clear about preferences
   - Maintain professional tone

3. **Follow-up**
   - Check application status regularly
   - Update information when changed
   - Respond to interview requests quickly
   - Provide feedback on process

## Troubleshooting

### Common Issues for Recruiters

1. **Questions Not Appearing**
   - Check job posting status
   - Verify question configuration
   - Ensure questions are published

2. **Export Failures**
   - Check file permissions
   - Verify storage space
   - Contact support if issue persists

3. **Candidate Matching Issues**
   - Review question weights
   - Check validation rules
   - Adjust scoring criteria

### Common Issues for Candidates

1. **Chatbot Not Responding**
   - Check internet connection
   - Try sending a simple message
   - Contact support if issue continues

2. **Questions Not Understood**
   - Use simple, clear language
   - Follow format examples
   - Ask for clarification if needed

3. **Document Upload Issues**
   - Check file format and size
   - Try alternative format
   - Contact support for assistance

## Support and Resources

### Help Documentation
- [API Documentation](./chatbot_api.md)
- [Architecture Guide](./chatbot_architecture.md)

### Contact Support
- Email: support@yourcompany.com
- Phone: +1-234-567-890
- WhatsApp: +1-234-567-890

### Training Resources
- Video tutorials available in dashboard
- Live training sessions weekly
- Documentation and FAQs

## FAQ

### For Recruiters

**Q: How do I customize prescreen questions for different roles?**
A: Navigate to Job Management, select the job, and edit the prescreen questions. You can add role-specific questions and adjust weights.

**Q: Can I modify questions after candidates have started answering?**
A: Yes, but it may affect ongoing applications. It's best to finalize questions before starting outreach.

**Q: How are match scores calculated?**
A: Scores are calculated based on answers to prescreen questions, weighted by importance, and compared against job requirements.

### For Candidates

**Q: What if my current CTC is variable (includes bonuses)?**
A: Provide your total annual compensation including base salary, bonuses, and other benefits.

**Q: Can I update my answers after submission?**
A: Yes, you can update information by sending updated answers. The latest responses will be used for matching.

**Q: How long does the prescreening process take?**
A: Typically 5-10 minutes to complete all questions. You can complete it at your own pace.

**Q: What happens after I complete the prescreening?**
A: Your profile will be matched with suitable jobs, and recruiters will contact you if there's a match.

## Success Metrics

### For Recruiters
- **Response Rate**: Target 70%+ candidate response rate
- **Completion Rate**: Aim for 80%+ prescreen completion
- **Match Accuracy**: Monitor match score correlation with hire quality
- **Time to Fill**: Track reduction in time to fill positions

### For Candidates
- **Application Completion**: Complete all prescreen questions
- **Response Time**: Respond to messages within 24 hours
- **Interview Conversion**: Track progression from prescreen to interview
- **Job Match**: Quality of job matches received

## Updates and Changes

Stay updated with:
- New feature announcements
- Process improvements
- Best practice updates
- Training session schedules

Regular updates will be shared via:
- In-app notifications
- Email communications
- Dashboard announcements